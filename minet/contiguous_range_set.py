# =============================================================================
# Minet Contiguous Range Set Collection
# =============================================================================
#
# Simplistic implementation of a contiguous range set in python relying on a
# sorted list of contiguous intervals. It is very useful to represent a set of
# dense intervals using very little memory & is used across the task-resuming
# schemes of the CLI tool.
#
# It takes a lot of inspiration from the inversion list data structure.
#
from bisect import bisect_left


class ContiguousRangeSet(object):
    """
    Class representing contiguous ranges of integers as a sorted list of
    intervals.
    """

    def __init__(self):
        # NOTE: replace this by `blist` if not performany enough
        self.intervals = []
        self.current_stateful_interval = 0

    def add(self, point):
        """
        Method adding a single point to the set. We assume that the point
        cannot yet be in the set.
        """

        interval = (point, point)
        N = len(self.intervals)

        # Set is empty
        if N == 0:
            self.intervals.append(interval)
            return

        # Finding insertion point
        index = bisect_left(self.intervals, interval)

        if index >= N:
            last_interval = self.intervals[-1]

            if point == last_interval[1] + 1:
                self.intervals[-1] = (last_interval[0], point)
                return

            self.intervals.append(interval)
            return

        matched_interval = self.intervals[index]
        previous_interval = self.intervals[index - 1] if index != 0 else None

        if point == matched_interval[0] - 1:

            self.intervals[index] = (point, matched_interval[1])

            if previous_interval is not None:

                if point == previous_interval[1] + 1:
                    self.intervals[index] = (previous_interval[0], matched_interval[1])
                    self.intervals.pop(index - 1)

            return

        elif previous_interval is not None and point == previous_interval[1] + 1:

            self.intervals[index - 1] = (previous_interval[0], point)
            return

        if point < matched_interval[0]:
            self.intervals.insert(index, interval)
            return

    def stateful_contains(self, point):
        """
        Method returning whether the given point is found in the set. This
        method is stateful and assumes we will ask for points in a monotonic
        increasing order.
        """

        N = len(self.intervals)

        if N == 0 or self.current_stateful_interval >= N:
            return False

        I = self.intervals[self.current_stateful_interval]

        if point < I[0]:
            return False

        if point > I[1]:
            self.current_stateful_interval += 1
            return False

        return True
