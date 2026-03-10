import csv
import logging
import queue
import signal
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Optional

import cv2
import imagezmq
import numpy as np
import sounddevice as sd
import tensorflow as tf
import tensorflow_hub as hub


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(threadName)s | %(message)s",
)
logger = logging.getLogger("edge_pipeline")


@dataclass(slots=True)
class EdgeConfig:
    # Identity / transport
    camera_id: str = "cachyos_simulating_pi5"
    zmq_address: str = "tcp://127.0.0.1:5555"
    imagezmq_req_rep: bool = True  # True => REQ/REP, False => PUB/SUB

    # Video ingest
    video_device_index: int = 1
    frame_width: int = 1920
    frame_height: int = 1080
    fps: int = 30
    buffer_seconds: int = 60
    jpeg_quality: int = 85
    video_warmup_seconds: float = 5.0

    # Audio ingest / YAMNet
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    audio_chunk_seconds: float = 1.0
    audio_dtype: str = "float32"
    audio_latency: str = "high"
    audio_queue_maxsize: int = 8
    audio_input_device = "pulse"

    # Triggering / label tuning
    trigger_cooldown_seconds: float = 10.0
    debug_top_k: int = 5
    monitored_label_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "Shout": 0.10,
            "Yell": 0.10,
            "Screaming": 0.08,
            "Bellow": 0.10,
            "Gunshot, gunfire": 0.05,
            "Glass": 0.15,
        }
    )


class EdgePipeline:
    def __init__(self, config: EdgeConfig) -> None:
        self.config = config
        self.max_frames = self.config.fps * self.config.buffer_seconds

        self.stop_event = threading.Event()
        self.buffer_lock = threading.Lock()
        self.trigger_lock = threading.Lock()
        self.transmit_lock = threading.Lock()

        self.ring_buffer: Deque[tuple[float, np.ndarray]] = deque(maxlen=self.max_frames)
        self.audio_queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=self.config.audio_queue_maxsize)
        self.last_trigger_ts = 0.0

        logger.info("Loading YAMNet model from TensorFlow Hub...")
        self.yamnet_model = hub.load("https://tfhub.dev/google/yamnet/1")
        self.yamnet_classes = self._load_class_names()
        self.monitored_targets = self._resolve_monitored_targets()

        self.sender = self._init_sender()

    def _load_class_names(self) -> list[str]:
        class_map_path = self.yamnet_model.class_map_path().numpy()
        if isinstance(class_map_path, bytes):
            class_map_path = class_map_path.decode("utf-8")

        class_names: list[str] = []
        with tf.io.gfile.GFile(class_map_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                class_names.append(row["display_name"])

        logger.info("Loaded %d YAMNet class names.", len(class_names))
        return class_names

    def _resolve_monitored_targets(self) -> dict[int, tuple[str, float]]:
        label_to_index = {label: idx for idx, label in enumerate(self.yamnet_classes)}
        monitored_targets: dict[int, tuple[str, float]] = {}
        missing_labels: list[str] = []

        for label, threshold in self.config.monitored_label_thresholds.items():
            idx = label_to_index.get(label)
            if idx is None:
                missing_labels.append(label)
                continue
            monitored_targets[idx] = (label, threshold)

        if monitored_targets:
            pretty_targets = [
                f"{label}>= {threshold:.2f}" for label, threshold in self.config.monitored_label_thresholds.items()
                if label in label_to_index
            ]
            logger.info("Monitoring YAMNet labels: %s", pretty_targets)
        else:
            logger.warning(
                "No configured YAMNet labels matched the model class map. "
                "Audio triggers will never fire until you fix monitored_label_thresholds."
            )

        if missing_labels:
            logger.warning("These configured labels were not found in the YAMNet class map: %s", missing_labels)

        return monitored_targets

    def _init_sender(self) -> Optional[imagezmq.ImageSender]:
        try:
            sender = imagezmq.ImageSender(
                connect_to=self.config.zmq_address,
                REQ_REP=self.config.imagezmq_req_rep,
            )
            mode = "REQ/REP" if self.config.imagezmq_req_rep else "PUB/SUB"
            logger.info("imageZMQ sender ready at %s using %s mode.", self.config.zmq_address, mode)
            return sender
        except Exception:
            logger.exception("Failed to initialize imageZMQ sender. Continuing without transmission.")
            return None

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        if status:
            logger.warning("Audio callback status: %s", status)

        if self.stop_event.is_set():
            return

        # Keep the callback lightweight: copy the chunk and hand it to a worker.
        chunk = np.copy(indata)

        try:
            self.audio_queue.put_nowait(chunk)
        except queue.Full:
            try:
                _ = self.audio_queue.get_nowait()
            except queue.Empty:
                pass

            try:
                self.audio_queue.put_nowait(chunk)
            except queue.Full:
                logger.warning("Audio queue is saturated; dropping chunk.")

    def _video_loop(self) -> None:
        cap = cv2.VideoCapture(self.config.video_device_index, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.frame_height)
        cap.set(cv2.CAP_PROP_FPS, self.config.fps)

        if not cap.isOpened():
            logger.error("Could not open video device index %s.", self.config.video_device_index)
            self.stop_event.set()
            return

        logger.info(
            "[%s] Video ingestion active. Buffering up to %ds (%d frames max).",
            self.config.camera_id,
            self.config.buffer_seconds,
            self.max_frames,
        )

        try:
            while not self.stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Video capture returned no frame.")
                    time.sleep(0.05)
                    continue

                ok, jpg_buffer = cv2.imencode(
                    ".jpg",
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), self.config.jpeg_quality],
                )
                if not ok:
                    logger.warning("Failed to JPEG-encode frame; skipping.")
                    continue

                frame_ts = time.time()
                with self.buffer_lock:
                    self.ring_buffer.append((frame_ts, jpg_buffer))
        except Exception:
            logger.exception("Unhandled exception in video loop.")
            self.stop_event.set()
        finally:
            cap.release()
            logger.info("Video capture released.")

    def _audio_worker_loop(self) -> None:
        logger.info("Audio worker thread started.")

        while not self.stop_event.is_set():
            try:
                chunk = self.audio_queue.get(timeout=0.25)
            except queue.Empty:
                continue

            waveform = np.asarray(chunk, dtype=np.float32).reshape(-1)
            if waveform.size == 0:
                continue

            rms = float(np.sqrt(np.mean(np.square(waveform))))
            if rms < 0.01:
                logger.info("Skipping low-energy chunk (rms=%.4f)", rms)
                continue

            try:
                scores, embeddings, spectrogram = self.yamnet_model(waveform)
            except Exception:
                logger.exception("YAMNet inference failed for the audio chunk.")
                continue

            mean_scores = tf.reduce_mean(scores, axis=0).numpy()
            monitored_summary = ", ".join(
                f"{label}={float(mean_scores[idx]):.2f}/{threshold:.2f}"
                for idx, (label, threshold) in self.monitored_targets.items()
            )
            logger.info("Monitored scores: %s", monitored_summary)

            top_k = max(1, self.config.debug_top_k)
            top_indices = np.argsort(mean_scores)[-top_k:][::-1]
            top_summary = ", ".join(
                f"{self.yamnet_classes[idx]}={float(mean_scores[idx]):.2f}" for idx in top_indices
            )
            logger.info("Top YAMNet labels: %s", top_summary)

            if not self.monitored_targets:
                continue

            best_idx = max(self.monitored_targets, key=lambda idx: float(mean_scores[idx]))
            best_label, best_threshold = self.monitored_targets[best_idx]
            best_score = float(mean_scores[best_idx])

            logger.info(
                "Best monitored label: %s=%.2f (threshold=%.2f)",
                best_label,
                best_score,
                best_threshold,
            )

            if best_score >= best_threshold:
                reason = f"{best_label} (confidence={best_score:.2f}, threshold={best_threshold:.2f})"
                self._maybe_trigger(reason)

    def _maybe_trigger(self, trigger_reason: str) -> None:
        now = time.time()

        with self.trigger_lock:
            elapsed = now - self.last_trigger_ts
            if elapsed < self.config.trigger_cooldown_seconds:
                logger.info(
                    "Trigger suppressed by cooldown. Reason=%s | %.2fs remaining",
                    trigger_reason,
                    self.config.trigger_cooldown_seconds - elapsed,
                )
                return

            self.last_trigger_ts = now

        trigger_thread = threading.Thread(
            target=self._extract_and_transmit_event,
            args=(trigger_reason, now),
            name="clip-transmitter",
            daemon=True,
        )
        trigger_thread.start()

    def _extract_and_transmit_event(self, trigger_reason: str, event_ts: float) -> None:
        if not self.transmit_lock.acquire(blocking=False):
            logger.info("Transmission already in progress; skipping overlapping trigger: %s", trigger_reason)
            return

        try:
            with self.buffer_lock:
                contextual_clip = list(self.ring_buffer)

            if not contextual_clip:
                logger.warning("Trigger fired but the ring buffer is empty.")
                return

            logger.info(
                "[ALERT] Trigger fired by %s. Extracted %d buffered frames.",
                trigger_reason,
                len(contextual_clip),
            )

            if self.sender is None:
                logger.warning("No imageZMQ sender available. Skipping transmission.")
                return

            for frame_idx, (frame_ts, jpg_buffer) in enumerate(contextual_clip):
                message = (
                    f"camera={self.config.camera_id};"
                    f"event_ts={event_ts:.6f};"
                    f"frame_ts={frame_ts:.6f};"
                    f"frame_idx={frame_idx};"
                    f"reason={trigger_reason}"
                )
                self.sender.send_jpg(message, jpg_buffer)

            logger.info("Transmission complete for event at %.6f.", event_ts)
        except Exception:
            logger.exception("Failed while extracting/transmitting event clip.")
        finally:
            self.transmit_lock.release()

    def _audio_stream_loop(self) -> None:
        blocksize = int(self.config.audio_sample_rate * self.config.audio_chunk_seconds)
        logger.info(
            "[%s] Audio trigger active at %d Hz, %d channel(s), %.2fs chunks.",
            self.config.camera_id,
            self.config.audio_sample_rate,
            self.config.audio_channels,
            self.config.audio_chunk_seconds,
        )

        try:
            with sd.InputStream(
                samplerate=self.config.audio_sample_rate,
                channels=self.config.audio_channels,
                dtype=self.config.audio_dtype,
                callback=self._audio_callback,
                blocksize=blocksize,
                latency=self.config.audio_latency,
                device=self.config.audio_input_device,
            ):
                while not self.stop_event.is_set():
                    time.sleep(0.25)
        except Exception:
            logger.exception("Audio input stream failed.")
            self.stop_event.set()

    def _install_signal_handlers(self) -> None:
        def _handler(signum, frame) -> None:
            logger.info("Received signal %s. Beginning shutdown.", signum)
            self.stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, _handler)
            except Exception:
                logger.warning("Could not register handler for signal %s.", sig)

    def shutdown(self) -> None:
        self.stop_event.set()

        if self.sender is not None:
            try:
                self.sender.close()
            except Exception:
                logger.exception("Failed to close imageZMQ sender cleanly.")

        logger.info("Shutdown complete.")

    def run(self) -> None:
        self._install_signal_handlers()

        video_thread = threading.Thread(target=self._video_loop, name="video-loop", daemon=True)
        audio_worker_thread = threading.Thread(target=self._audio_worker_loop, name="audio-worker", daemon=True)

        video_thread.start()
        audio_worker_thread.start()

        logger.info("Warming video buffer for %.1f seconds before arming audio trigger...", self.config.video_warmup_seconds)
        time.sleep(self.config.video_warmup_seconds)

        try:
            self._audio_stream_loop()
        finally:
            self.shutdown()
            video_thread.join(timeout=2.0)
            audio_worker_thread.join(timeout=2.0)


if __name__ == "__main__":
    pipeline = EdgePipeline(EdgeConfig())
    pipeline.run()
