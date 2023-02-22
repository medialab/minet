from threading import Timer, Event
from timeit import default_timer as timer
from urllib3 import Timeout
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--cancel-after", type=int)
parser.add_argument("--timeout", type=int)

cli_args = parser.parse_args()

from minet.web import DEFAULT_POOL, BufferedResponse

cancel_event = Event()
final_timeout = cli_args.timeout
end_time = (timer() + final_timeout) if final_timeout is not None else None


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

buffered = BufferedResponse(response, cancel_event=cancel_event, end_time=end_time)
buffered.read()

print("Finished")
