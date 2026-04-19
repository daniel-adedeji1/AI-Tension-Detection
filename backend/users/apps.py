from django.apps import AppConfig
import os
import sys
import threading


_listener_thread = None


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        global _listener_thread

        from django.conf import settings

        should_start_listener = (
            settings.AUTO_START_ZMQ_LISTENER
            and os.environ.get("RUN_MAIN") == "true"
            and any(arg in {"runserver", "runserver_plus"} for arg in sys.argv)
        )

        if not should_start_listener or _listener_thread is not None:
            return

        from .zmq_listener import run_listener

        _listener_thread = threading.Thread(
            target=run_listener,
            name="zmq-listener",
            daemon=True,
        )
        _listener_thread.start()
