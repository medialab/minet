# =============================================================================
# Minet Crawler State
# =============================================================================
#
# Simple class representing a miner Crawler's state.
#
from threading import Lock
from contextlib import contextmanager


class CrawlerState(object):
    jobs_done: int
    jobs_doing: int
    jobs_queued: int
    __lock: Lock

    def __init__(self):
        self.__lock = Lock()

        self.jobs_done = 0
        self.jobs_doing = 0
        self.jobs_queued = 0

    def inc_queued(self) -> None:
        with self.__lock:
            self.jobs_queued += 1

    def dec_queued(self) -> None:
        with self.__lock:
            self.jobs_queued -= 1

    def inc_done(self) -> None:
        with self.__lock:
            self.jobs_done += 1

    def inc_doing(self) -> None:
        with self.__lock:
            self.jobs_doing += 1

    def dec_doing(self) -> None:
        with self.__lock:
            self.jobs_doing -= 1

    def inc_working(self) -> None:
        with self.__lock:
            self.jobs_queued -= 1
            self.jobs_doing += 1

    def dec_working(self) -> None:
        with self.__lock:
            self.jobs_done += 1
            self.jobs_doing -= 1

    @contextmanager
    def task(self):
        try:
            self.inc_working()
            yield
        finally:
            self.dec_working()

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            "<%(class_name)s queued=%(jobs_queued)i doing=%(jobs_doing)i done=%(jobs_done)i>"
        ) % {
            "class_name": class_name,
            "jobs_done": self.jobs_done,
            "jobs_queued": self.jobs_queued,
            "jobs_doing": self.jobs_doing,
        }
