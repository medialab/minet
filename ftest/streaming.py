from threading import Timer, Event
from urllib3 import Timeout
from argparse import ArgumentParser

from minet.web import DEFAULT_POOL, BufferedResponse, timeout_to_final_time

parser = ArgumentParser()
parser.add_argument("--cancel-after", type=int)
parser.add_argument("--timeout", type=int)

cli_args = parser.parse_args()

cancel_event = Event()
final_timeout = cli_args.timeout
final_time = timeout_to_final_time(final_timeout) if final_timeout is not None else None


def cancel():
    print("Cancelling")
    cancel_event.set()


if cli_args.cancel_after is not None:
    Timer(cli_args.cancel_after, cancel).start()

response = DEFAULT_POOL.request(
    "GET",
    "http://100poursciences.fr/stream",
    timeout=Timeout(connect=1, read=1),
    preload_content=False,
)

print("Status:", response.status)

buffered = BufferedResponse(response, cancel_event=cancel_event, final_time=final_time)
buffered.read()

print("Finished")
