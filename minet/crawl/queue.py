from typing import Generic, TypeVar, Optional, Any, Iterable, List, Tuple
from minet.types import Literal

from shutil import rmtree
from os import makedirs
from os.path import isfile, join
from queue import Queue, LifoQueue as Stack, Empty
from persistqueue import SQLiteAckQueue
from persistqueue.sqlackqueue import FILOSQLiteAckQueue as SQLiteAckStack
from threading import Lock

ItemType = TypeVar("ItemType")

ACK_STATUS_TO_NAME = {
    0: "inited",
    1: "ready",
    2: "unack",
    5: "acked",
    9: "acked_failed",
}

AckStatusType = Literal["inited", "ready", "unack", "acked", "acked_failed"]
DumpedItemType = Tuple[AckStatusType, ItemType]
DumpType = List[DumpedItemType[ItemType]]


class CrawlerQueue(Generic[ItemType]):
    path: Optional[str]
    persistent: bool
    resuming: bool
    cleanup_interval: int

    __write_lock: Lock
    __queue: Any
    __current_task_done_count: int

    def __init__(
        self,
        path: Optional[str] = None,
        db_name: str = "queue.db",
        resume: bool = False,
        cleanup_interval: int = 5000,
        dfs: bool = False,
    ):
        self.path = path
        self.resuming = False
        self.persistent = False
        self.cleanup_interval = cleanup_interval

        self.__write_lock = Lock()

        if path is not None:
            self.persistent = True

            if not resume:
                rmtree(path, ignore_errors=True)
            else:
                if isfile(join(path, db_name)):
                    self.resuming = True

            makedirs(path, exist_ok=True)

            QueueCls = SQLiteAckStack if dfs else SQLiteAckQueue

            self.__queue = QueueCls(
                path, db_file_name=db_name, multithreading=True, auto_resume=True
            )

        else:
            self.__queue = Stack() if dfs else Queue()

        self.__current_task_done_count = 0

    def qsize(self) -> int:
        return self.__queue.qsize()

    def put(self, item: ItemType) -> None:
        with self.__write_lock:
            self.__queue.put(item)

    def put_many(self, items: Iterable[ItemType]) -> int:
        with self.__write_lock:
            count = 0

            for item in items:
                self.__queue.put(item)
                count += 1

            return count

    def get(self, block=True) -> ItemType:
        return self.__queue.get(block=block)

    def get_nowait(self) -> ItemType:
        return self.get(False)

    def ack(self, item: ItemType) -> None:
        self.__current_task_done_count += 1

        if self.persistent:
            self.__queue.ack(item)

        self.__queue.task_done()

        if self.__current_task_done_count >= self.cleanup_interval:
            self.cleanup()

    def cleanup(self):
        with self.__write_lock:
            if not self.persistent:
                return

            self.__current_task_done_count = 0

            self.__queue.clear_acked_data(
                max_delete=None, keep_latest=None, clear_ack_failed=False
            )
            self.__queue.shrink_disk_usage()

    def dump(self) -> DumpType[ItemType]:
        with self.__write_lock:
            if not self.persistent:
                items = []

                while True:
                    try:
                        items.append(("unack", self.__queue.get_nowait()))
                    except Empty:
                        break

                for item in items:
                    self.__queue.put_nowait(item)

                return items

            records = self.__queue.queue()

            items = []

            for record in records:
                items.append((ACK_STATUS_TO_NAME[record["status"]], record["data"]))

            return items

    def __del__(self):
        del self.__queue
