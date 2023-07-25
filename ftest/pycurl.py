from threading import Timer, Event
from minet.pycurl import request_with_pycurl
from minet.user_agents import get_random_user_agent

cancel_event = Event()

# Timer(0.1, lambda: cancel_event.set()).start()

result = request_with_pycurl(
    "http://lemonde.fr",
    cancel_event=cancel_event,
    headers={"User-Agent": get_random_user_agent()},
    verbose=True,
)

print(result)

for k, v in result.headers.items():
    print(k, "//", v)
