import bisect


class DeviceEntry:
    # Represents one device's set of readings, timestamps, and aggregate counts
    # Trying slots as memory-efficient object
    __slots__ = ("timestamps", "count_sum", "readings_list")

    def __init__(self):
        self.timestamps = []
        self.count_sum = 0
        self.readings_list = []

    def add_reading(self, new_reading):
        if self._is_dupe_date(new_reading.timestamp):
            # Ignore duplicate datetimes and their associated counts
            return
        
        # Rely on bisect to keep timestamp list sorted upon insertion to avoid manual sorting
        # here or needing to sort as part of 'latest-timestamp' GET request'
        bisect.insort(self.timestamps, new_reading.timestamp)
        self.count_sum += new_reading.count

        # Optional, unused for user-facing GET requests but may be useful to retain per-date counts
        # Should be removed if unneeded for production to avoid extra memory use
        self.readings_list.append(new_reading)

    def _is_dupe_date(self, new_datetime):
        insertion_point = bisect.bisect_left(self.timestamps, new_datetime)
        if (
            insertion_point == len(self.timestamps) or
            self.timestamps[insertion_point] != new_datetime
        ):
            return False
        return True
