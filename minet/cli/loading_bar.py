# =============================================================================
# Minet Loading Bars
# =============================================================================
#
# Various loading bar utilities used by minet CLI.
#
from typing import Optional
from rich.live import Live
from rich.text import Text
from rich.progress import (
    Progress,
    ProgressColumn,
    TextColumn,
    BarColumn,
    SpinnerColumn,
    TaskProgressColumn,
    Task,
)
from rich._spinners import SPINNERS
from about_time import HumanDuration, HumanThroughput
from ebbe import format_int

from minet.cli.console import console

SPINNERS["minetDots1"] = {
    "interval": 100,
    "frames": [
        "|▰▰▰▰▰▰▰   |",
        "| ▰▰▰▰▰▰▰  |",
        "|  ▰▰▰▰▰▰▰ |",
        "|   ▰▰▰▰▰▰▰|",
        "|▰   ▰▰▰▰▰▰|",
        "|▰▰   ▰▰▰▰▰|",
        "|▰▰▰   ▰▰▰▰|",
        "|▰▰▰▰   ▰▰▰|",
        "|▰▰▰▰▰   ▰▰|",
        "|▰▰▰▰▰▰   ▰|",
    ],
}

SPINNERS["minetDots2"] = {
    "interval": 150,
    "frames": [
        "|▰▰▰▰      |",
        "| ▰▰▰▰     |",
        "|  ▰▰▰▰    |",
        "|   ▰▰▰▰   |",
        "|    ▰▰▰▰  |",
        "|     ▰▰▰▰ |",
        "|      ▰▰▰▰|",
        "|     ▰▰▰▰ |",
        "|    ▰▰▰▰  |",
        "|   ▰▰▰▰   |",
        "|  ▰▰▰▰    |",
        "| ▰▰▰▰     |",
    ],
}


class TimeElapsedColumn(ProgressColumn):
    def render(self, task: Task) -> Optional[Text]:
        elapsed = task.finished_time if task.finished else task.elapsed

        if not elapsed:
            return None

        return Text("in " + str(HumanDuration(elapsed)), style="progress.elapsed")


class CompletionColumn(ProgressColumn):
    def __init__(self, unit: Optional[str] = None, table_column=None):
        self.unit = unit
        super().__init__(table_column=table_column)

    def render(self, task: Task) -> Text:
        total = format_int(task.total) if task.total is not None else "?"
        completed = format_int(task.completed).rjust(len(total))
        unit_text = f" {self.unit}" if self.unit is not None else ""

        return Text(f"{completed}/{total}{unit_text}")


class ThroughputColumn(ProgressColumn):
    def render(self, task: Task) -> Optional[Text]:
        elapsed = task.finished_time if task.finished else task.elapsed

        if not elapsed:
            return None

        throughput = HumanThroughput(task.completed / elapsed, "s")

        eta = ""

        if task.total is not None:
            remaining = HumanDuration(task.time_remaining)
            eta = f" eta: {remaining}"

        message = f"({throughput}{eta})"

        return Text(message)


class LoadingBar(object):
    def __init__(
        self,
        title: Optional[str] = None,
        unit: Optional[str] = None,
        total: Optional[int] = None,
    ):
        self.title = title
        self.unit = unit
        self.total = total

        self.bar_column = None
        self.spinner_column = None

        if total is not None:
            self.bar_column = BarColumn()

            columns = [
                TextColumn("[progress.description]{task.description}"),
                self.bar_column,
                CompletionColumn(unit=self.unit),
                SpinnerColumn("dots", style=None, finished_text="▰"),
                TaskProgressColumn("[progress.percentage][{task.percentage:>3.0f}%]"),
                TimeElapsedColumn(),
                ThroughputColumn(),
            ]
        else:
            self.spinner_column = SpinnerColumn("minetDots2", style="info")

            columns = [
                TextColumn("[progress.description]{task.description}"),
                self.spinner_column,
                CompletionColumn(unit=self.unit),
                TaskProgressColumn("[progress.percentage][{task.percentage:>3.0f}%]"),
                TimeElapsedColumn(),
                ThroughputColumn(),
            ]

        self.progress = Progress(*columns, console=console)
        self.live = Live(self.progress, refresh_per_second=10, console=console)

        self.task = self.progress.add_task(
            description=self.title, total=self.total, fields={"unit": self.unit}
        )

    def __enter__(self):
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):

        if exc_type is not None:
            if self.bar_column is not None:
                self.bar_column.complete_style = "warning"
            if self.spinner_column is not None:
                self.spinner_column.set_spinner("minetDots2", "warning")

        else:
            if self.spinner_column is not None:
                self.spinner_column.set_spinner("minetDots2", "success")

        self.live.stop()

    def advance(self, count=1):
        self.progress.update(self.task, advance=count)
