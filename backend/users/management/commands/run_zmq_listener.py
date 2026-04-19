from django.core.management.base import BaseCommand

from users.zmq_listener import run_listener


class Command(BaseCommand):
    help = "Run the ZeroMQ listener that forwards edge packets to websocket clients."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting ZMQ listener..."))
        run_listener()
