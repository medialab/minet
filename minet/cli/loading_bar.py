# =============================================================================
# Minet Loading Bars
# =============================================================================
#
# Various loading bar utilities used by minet CLI.
#
from typing import Optional, Iterable
from typing_extensions import TypedDict, NotRequired

from contextlib import contextmanager
from collections import OrderedDict
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
from rich._spinners import SPINNERS
from about_time import HumanDuration, HumanThroughput
from ebbe import format_int

from minet.utils import message_flatmap
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
    def render(self, task: Task) -> Optional[Text]:
        total = format_int(task.total) if task.total is not None else "?"
        completed = format_int(task.completed).rjust(len(total))

        unit = task.fields.get("unit")
        unit_text = f" {unit}" if unit is not None else ""

        return Text(f"{completed}/{total}{unit_text}")


class ThroughputColumn(ProgressColumn):
    def render(self, task: Task) -> Optional[Text]:
        elapsed = task.finished_time if task.finished else task.elapsed

        if not elapsed or not task.completed:
            return Text("(?/s)")

        throughput = HumanThroughput(task.completed / elapsed, "s")

        eta = ""

        if task.total is not None and task.time_remaining:
            remaining = HumanDuration(task.time_remaining)
            eta = f" eta: {remaining}"

        message = f"({throughput}{eta})"

        return Text(message)


class StatsColumn(ProgressColumn):
    def render(self, task: Task) -> Optional[Text]:
        stats = task.fields.get("stats")

        if stats is None:
            return None

        total = 0

        item_parts = []

        for item in stats.values():
            txt = Text()

            count = item["count"]

            if count == 0:
                continue

            total += count

            txt.append(item["name"], style=item["style"])
            txt.append(" ")
            txt.append(format_int(count))

            item_parts.append(txt)

        parts = []

        if task.description and total:
            parts.append(Text("- "))

        return Text.assemble(*parts, *Text(", ").join(item_parts))


class NestedTotalColumn(ProgressColumn):
    def render(self, task: Task) -> Optional[Text]:
        sub_total = task.fields.get("sub_total")

        if sub_total is None:
            return None

        unit = task.fields.get("unit")
        unit_text = f" {unit}" if unit is not None else ""

        return Text(f", total: {format_int(sub_total)}{unit_text}")


class StatsItem(TypedDict):
    name: str
    style: NotRequired[str]
    initial: NotRequired[int]


class LoadingBar(object):
    def __init__(
        self,
        title: Optional[str] = None,
        unit: Optional[str] = None,
        total: Optional[int] = None,
        show_label: bool = False,
        label_format: str = "{task.description}",
        stats: Optional[Iterable[StatsItem]] = None,
        nested: bool = False,
        sub_title: Optional[str] = None,
        sub_unit: Optional[str] = None,
    ):
        self.total = total
        self.sub_total = 0
        self.nested = nested

        self.bar_column = None
        self.spinner_column = None
        self.upper_line = None
        self.upper_line_task_id = None
        self.sub_progress = None
        self.sub_task = None

        self.table = Table.grid(expand=True)

        self.task_stats = None

        if stats is not None:
            self.task_stats = OrderedDict()

            for item in stats:
                self.task_stats[item["name"]] = {
                    "name": item["name"],
                    "style": item.get("style", ""),
                    "count": item.get("count", 0),
                }

        if show_label:
            upper_line_columns = []

            if show_label:
                upper_line_columns.append(TextColumn(label_format))

            if stats is not None:
                upper_line_columns.append(StatsColumn())

            self.upper_line = Progress(*upper_line_columns)
            self.upper_line_task_id = self.upper_line.add_task(
                description="", total=None, stats=self.task_stats
            )
            self.table.add_row(self.upper_line)

        if total is not None:
            self.bar_column = BarColumn()

            columns = [
                TextColumn("[progress.description]{task.description}"),
                self.bar_column,
            ]

            if total > 1:
                columns.append(CompletionColumn())

            if not nested:
                columns.append(SpinnerColumn("dots", style=None, finished_text="·"))

            if total > 1:
                columns.append(
                    TaskProgressColumn(
                        "[progress.percentage][{task.percentage:>3.0f}%]"
                    )
                )

            columns.append(TimeElapsedColumn())

            if total > 1:
                columns.append(ThroughputColumn())
        else:
            self.spinner_column = SpinnerColumn("minetDots2", style="info")

            columns = [
                TextColumn("[progress.description]{task.description}"),
                self.spinner_column,
                CompletionColumn(),
                TimeElapsedColumn(),
                ThroughputColumn(),
            ]

        columns = [c for c in columns if c]

        self.progress = Progress(*columns, console=console)
        self.table.add_row(self.progress)

        self.task_id = self.progress.add_task(
            description=title or "", total=self.total, unit=unit
        )

        if nested:
            sub_columns = [
                SpinnerColumn("dots", style="", finished_text="·"),
                TextColumn("{task.description}"),
                CompletionColumn(),
                TimeElapsedColumn(),
                ThroughputColumn(),
                NestedTotalColumn(),
            ]

            if stats is not None:
                sub_columns.append(StatsColumn())

            self.sub_progress = Progress(*sub_columns)
            self.sub_task = self.sub_progress.add_task(
                description=sub_title or "",
                total=None,
                stats=self.task_stats,
                sub_total=self.sub_total,
                unit=sub_unit,
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

    @contextmanager
    def tick(self):
        try:
            yield
        finally:
            self.advance()

    @contextmanager
    def nested_tick(self):
        try:
            yield
        finally:
            self.nested_advance()

    @contextmanager
    def nested_task(self, description):
        assert self.nested

        try:
            self.reset_sub()
            self.update(sub_title=description)
            yield
        finally:
            self.update(count=1)

    def advance(self, count=1):
        self.progress.update(self.task_id, advance=count)

    def nested_advance(self, count=1):
        self.sub_total += 1
        self.sub_progress.update(self.sub_task, advance=count, sub_total=self.sub_total)

    def reset_sub(self):
        self.sub_progress.reset(self.sub_task)

    def update(self, count=None, sub_title=None, sub_count=None, label=None, **fields):
        if count is not None:
            self.advance(count)

        if sub_count is not None:
            self.nested_advance(sub_count)

        if sub_title is not None:
            self.sub_progress.update(self.sub_task, description=sub_title)

        if label is not None:
            assert self.upper_line is not None
            self.upper_line.update(self.upper_line_task_id, description=label)

        if fields:
            assert self.task_stats is not None

            for field, count in fields.items():
                self.task_stats[field]["count"] += count

            if self.upper_line is not None:
                self.upper_line.update(self.upper_line_task_id, stats=self.task_stats)
            elif self.sub_progress is not None:
                self.sub_progress.update(self.sub_task, stats=self.task_stats)

    def print(self, *msg):
        console.pring(message_flatmap(*msg))
