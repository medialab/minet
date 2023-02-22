from threading import Timer, Event
from timeit import default_timer as timer
from urllib3 import Timeout

from minet.web import stream_request_body, DEFAULT_POOL

cancel_event = Event()
final_timeout = 5
end_time = timer() + final_timeout


def cancel():
    print("Cancelling")
    cancel_event.set()


# Timer(2, cancel).start()

response = DEFAULT_POOL.request(
    "GET",
    "http://100poursciences.fr/stream",
    timeout=Timeout(connect=1, read=1),
    preload_content=False,
)

print(response.status)

body = stream_request_body(response, cancel_event=cancel_event, end_time=end_time)

print(body.getvalue().decode())
