import datetime

from errors import InvalidReadingCount, InvalidReadingTimestamp


class DeviceReading:
    # Represents one reading entry. Primary use is to validate data points and parse timestamp
    # into datetime for ease of use.
    # Trying slots as memory-efficient object
    __slots__ = ("count", "timestamp")

    def __init__(self, count=None, timestamp=None):
        self.count = self._format_count(count)
        self.timestamp = self._format_timestamp(timestamp)

    @classmethod
    def timestamp_format(cls):
        return '%Y-%m-%dT%H:%M:%S%z'

    def _format_count(self, input_count):
        if not type(input_count) == int:
            raise InvalidReadingCount

        if input_count <= 0:
            raise InvalidReadingCount

        return input_count

    def _format_timestamp(self, input_timestamp):
        if not type(input_timestamp) == str:
            raise InvalidReadingTimestamp

        try:
            parsed_timestamp = datetime.datetime.strptime(
                input_timestamp, DeviceReading.timestamp_format()
            )
        except ValueError:
            raise InvalidReadingTimestamp

        return parsed_timestamp
