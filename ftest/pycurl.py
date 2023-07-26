# for mac:
# env PYCURL_SSL_LIBRARY=openssl LDFLAGS="-L$(brew --prefix openssl)/lib" CPPFLAGS="-I$(brew --prefix openssl)/include" pip install --no-cache-dir --compile --ignore-installed pycurl
from threading import Timer, Event
from minet.pycurl import request_with_pycurl
from minet.user_agents import get_random_user_agent

cancel_event = Event()

# Timer(0.1, lambda: cancel_event.set()).start()

result = request_with_pycurl(
    "http://lemonde.fr",
    cancel_event=cancel_event,
    headers={"User-Agent": get_random_user_agent()},
)

print(result)
print()

print("Headers:")
for k, v in result.headers.items():
    print(k + ":", v)

print()
print("Stack:")
for r in result.stack:
    print(r)
