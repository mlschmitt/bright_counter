from collections import defaultdict
from uuid import UUID

from errors import DeviceNotFoundError, InvalidDeviceID, InvalidReadingCount
from db.device_entry import DeviceEntry
from db.device_reading import DeviceReading


# NOTE: NOT thread safe!
# To productionalize must pivot to Redis or DB datastore
#
# My assumption here is instructions regarding "implement your solution with only the web API server"
# prohibited the use of options like Redis even though that's technically in-memory
class DeviceReadingsAccessor:
    # Class through which interactions with device readings data should pass, including creation
    # and retrieval. Handles validating input data & translating into consistent formats
    def __init__(self):
        self.device_store = defaultdict(DeviceEntry)

    def save_batch_for_device(self, device_id, input_readings):
        if not self.is_uuid(device_id):
            raise InvalidDeviceID

        # Format & validate all readings upfront before attempting to save any,
        # so 1 entry in array with errors will prevent partial list save.
        # TODO: Check with Product if they would prefer we only skip individual invalid readings,
        # and how to handle communicating errors, if any, in that case.
        device_readings = self._format_readings(input_readings)
        for reading in device_readings:
            self.device_store[device_id].add_reading(reading)

    def retrieve_latest_timestamp(self, device_id):
        # Helper method for retrieving last recorded timestamp for device
        # Raises exception if no data found or input device_id is invalid
        return self.retrieve_device_readings(device_id).timestamps[-1]

    def retrieve_sum_count(self, device_id):
        # Helper method for retrieving last recorded timestamp for device
        # Raises exception if no data found or input device_id is invalid
        return self.retrieve_device_readings(device_id).count_sum

    def retrieve_device_readings(self, device_id):
        # Returns DeviceEntry for specified device_id or raises exception if invalid/none found
        if not self.is_uuid(device_id):
            raise InvalidDeviceID

        readings = self.device_store[device_id]
        if not readings.readings_list:
            raise DeviceNotFoundError

        return readings

    def is_uuid(self, device_id):
        if not type(device_id) == str:
            return False
        try:
            converted_uuid = UUID(device_id, version=4)
        except ValueError:
            # Exception thrown if input device_id cannot be parsed as UUIDv4
            return False

        return str(converted_uuid) == device_id

    def _format_readings(self, readings):
        formatted_readings = []
        for reading in readings:
            formatted_readings.append(
                DeviceReading(
                    count=reading.get("count", None),
                    timestamp=reading.get("timestamp", None)
                )
            )
        return formatted_readings


readings_accessor = DeviceReadingsAccessor()
