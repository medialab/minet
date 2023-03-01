# =============================================================================
# Minet Crawler State
# =============================================================================
#
# Simple class representing a miner Crawler's state.
#
from typing import Callable, Optional

from threading import Lock
from contextlib import contextmanager

CrawlerStateListener = Callable[["CrawlerState"], None]


class CrawlerState(object):
    jobs_done: int
    jobs_doing: int
    jobs_queued: int

    listener: Optional[CrawlerStateListener]

    __lock: Lock

    def __init__(
        self,
        jobs_queued: Optional[int] = None,
        listener: Optional[CrawlerStateListener] = None,
    ):
        self.__lock = Lock()

        self.jobs_done = 0
        self.jobs_doing = 0
        self.jobs_queued = jobs_queued if jobs_queued is not None else 0

        self.listener = listener

    @property
    def total(self) -> int:
        return self.jobs_done + self.jobs_doing + self.jobs_queued

    def __notify(self):
        if callable(self.listener):
            self.listener(self)

    def set_listener(self, listener: CrawlerStateListener):
        with self.__lock:
            self.listener = listener

    def inc_queued(self, count=1) -> None:
        with self.__lock:
            self.jobs_queued += count
            self.__notify()

    def dec_queued(self) -> None:
        with self.__lock:
            self.jobs_queued -= 1
            self.__notify()

    def inc_done(self) -> None:
        with self.__lock:
            self.jobs_done += 1
            self.__notify()

    def inc_doing(self) -> None:
        with self.__lock:
            self.jobs_doing += 1
            self.__notify()

    def dec_doing(self) -> None:
        with self.__lock:
            self.jobs_doing -= 1
            self.__notify()

    def inc_working(self) -> None:
        with self.__lock:
            self.jobs_queued -= 1
            self.jobs_doing += 1
            self.__notify()

    def dec_working(self) -> None:
        with self.__lock:
            self.jobs_done += 1
            self.jobs_doing -= 1
            self.__notify()

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
