class DeviceNotFoundError(Exception):
    def __init__(self, message="Device readings not found."):
        self.message = message
        self.status_code = 404

class InvalidDeviceID(Exception):
    def __init__(self, message="Device ID must be valid UUID string."):
        self.message = message
        self.status_code = 400

class InvalidReadingTimestamp(Exception):
    def __init__(self, message="Field 'readings' contains invalid 'timestamp' value."):
        self.message = message
        self.status_code = 400

class InvalidReadingCount(Exception):
    def __init__(self, message="Field 'readings' contains invalid 'count' value. Must be positive integer."):
        self.message = message
        self.status_code = 400
