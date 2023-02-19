# =============================================================================
# Minet Loading Bars
# =============================================================================
#
# Various loading bar utilities used by minet CLI.
#
from typing import Optional
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich.progress import (
    Progress,
    ProgressColumn,
    TextColumn,
    BarColumn,
    SpinnerColumn,
    TaskProgressColumn,
    Task,
)
from rich.console import Group
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

        if task.total is not None and task.time_remaining:
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
        features=[],
    ):
        self.title = title
        self.unit = unit
        self.total = total
        self.features = set(features)

        self.bar_column = None
        self.spinner_column = None
        self.upper_line = None
        self.upper_line_task = None
        self.sub_progress = None
        self.sub_task = None

        self.table = Table.grid(expand=True)

        if "label" in self.features or "stats" in self.features:
            self.upper_line = Progress(
                TextColumn("[progress.description]{task.description}")
            )
            self.upper_line_task = self.upper_line.add_task(
                description="Coucou", total=None
            )
            self.table.add_row(self.upper_line)

        if total is not None:
            self.bar_column = BarColumn()

            columns = [
                TextColumn("[progress.description]{task.description}"),
                self.bar_column,
                CompletionColumn(unit=self.unit),
                SpinnerColumn("dots", style=None, finished_text="·")
                if "secondary" not in self.features
                else None,
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

        columns = [c for c in columns if c]

        self.progress = Progress(*columns, console=console)
        self.table.add_row(self.progress)

        self.task = self.progress.add_task(
            description=self.title, total=self.total, fields={"unit": self.unit}
        )

        if "secondary" in self.features:
            self.sub_progress = Progress(
                SpinnerColumn("dots", style="", finished_text="·"),
                TextColumn("{task.description}"),
            )
            self.sub_task = self.sub_progress.add_task(
                description="Sub task", total=None
            )
            self.table.add_row(self.sub_progress)

        self.live = Live(
            self.table,
            refresh_per_second=10,
            console=console,
        )

    def __enter__(self):
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):

        if exc_type is not None:
            # NOTE: cursor 1up
            console.file.write("\x1b[1A")

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

    def update(self, count=None, label=None):
        if count is not None:
            self.advance(count)

        if label is not None:
            assert self.upper_line is not None
            self.upper_line.update(self.upper_line_task, description=label)
