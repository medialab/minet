# =============================================================================
# Minet Range Set Collection
# =============================================================================
#
# Simplistic implementation of a range set in python relying on a sorted list of
# intervals. It is very useful to represent a set of dense intervals using very
# little memory & is used across the task-resuming schemes of the CLI tool.
#
from bisect import bisect_left


class RangeSet(object):
    def __init__(self):
        self.min = None
        self.max = None
        self.intervals = []

    def add(self, point):

        # Set is empty
        if self.min is None:
            interval = (point, point)
            self.min = interval
            self.max = interval
            self.intervals.append(interval)

            return

        # Monotonic shortcuts
        if point == self.min[0] or point == self.max[1]:
            return

        only_one_interval = self.min == self.max

        if point < self.min[0]:
            self.min = (point, self.min[1])
            self.intervals[0] = self.min
            return

        if point > self.max[1]:
            self.max = (self.max[0], point)
            self.intervals[-1] = self.max
            return

        # Using binary search to find insertion point
        index = bisect_left(self.intervals, (point, point))

        print(index)
