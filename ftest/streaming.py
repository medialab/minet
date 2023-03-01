from threading import Timer, Event
from argparse import ArgumentParser
from ebbe import Timer as BenchTimer

from minet.web import request

parser = ArgumentParser()
parser.add_argument("--cancel-after", type=int)
parser.add_argument("--timeout", type=int)

cli_args = parser.parse_args()

cancel_event = Event()


def cancel():
    print("Cancelling")
    cancel_event.set()


if cli_args.cancel_after is not None:
    Timer(cli_args.cancel_after, cancel).start()

with BenchTimer("atomic_request"):
    response, body = request(
        "http://100poursciences.fr/stream",
        timeout=cli_args.timeout,
        cancel_event=cancel_event,
    )

print("Status:", response.status)
print("Body:", body)
