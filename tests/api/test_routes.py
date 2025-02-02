import json

from db.device_readings_accessor import readings_accessor


# --- ping endpoint tests
def test_ping_success(client):
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


# -- device-readings create endpoint tests
def test_create_saves_provided_reading_for_device(client, helpers):
    device_id = helpers.generate_device_id()

    # No data saved initially
    assert device_id not in readings_accessor.device_store.keys()

    data = {
        "id": device_id,
        "readings": [{"count": 5, "timestamp": "2024-02-02T08:03:29-0600"}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 201
    assert device_id in readings_accessor.device_store.keys()
    assert len(readings_accessor.device_store[device_id].timestamps) == 1
    assert len(readings_accessor.device_store[device_id].readings_list) == 1
    assert readings_accessor.device_store[device_id].count_sum == 5

def test_create_saves_multiple_readings_for_device(client, helpers):
    device_id = helpers.generate_device_id()

    # No data saved initially
    assert device_id not in readings_accessor.device_store.keys()

    data = {
        "id": device_id,
        "readings": [
            {"count": 5, "timestamp": "2024-02-02T08:03:29-0600"},
            {"count": 4, "timestamp": "2022-12-23T09:18:01-0600"}
        ]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 201
    assert device_id in readings_accessor.device_store.keys()
    assert len(readings_accessor.device_store[device_id].timestamps) == 2
    assert len(readings_accessor.device_store[device_id].readings_list) == 2
    assert readings_accessor.device_store[device_id].count_sum == 9

def test_create_appends_new_readings_for_device(client, helpers):
    device_id = helpers.generate_device_id()
    data = {
        "id": device_id,
        "readings": [{"count": 5, "timestamp": "2024-02-02T08:03:29-0600"}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 201
    assert device_id in readings_accessor.device_store.keys()
    assert len(readings_accessor.device_store[device_id].timestamps) == 1
    assert len(readings_accessor.device_store[device_id].readings_list) == 1
    assert readings_accessor.device_store[device_id].count_sum == 5

    new_data = {
        "id": device_id,
        "readings": [{"count": 23, "timestamp": "2023-02-02T08:03:29-0600"}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(new_data))
    assert response.status_code == 201
    assert len(readings_accessor.device_store[device_id].timestamps) == 2
    assert len(readings_accessor.device_store[device_id].readings_list) == 2
    assert readings_accessor.device_store[device_id].count_sum == 28

def test_create_for_new_device_does_not_impact_unrelated_device(client, helpers):
    device_id = helpers.generate_device_id()
    unrelated_device_id = helpers.generate_device_id()
    readings_accessor.save_batch_for_device(
        unrelated_device_id, [
            {"count": 3, "timestamp": "2024-01-01T08:03:29-0600"},
            {"count": 2, "timestamp": "2020-03-03T09:45:00-0600"}
        ]
    )
    assert unrelated_device_id in readings_accessor.device_store.keys()
    assert len(readings_accessor.device_store[unrelated_device_id].timestamps) == 2
    assert len(readings_accessor.device_store[unrelated_device_id].readings_list) == 2
    assert readings_accessor.device_store[unrelated_device_id].count_sum == 5

    assert device_id not in readings_accessor.device_store.keys()
    data = {
        "id": device_id,
        "readings": [{"count": 52, "timestamp": "2020-01-29T08:03:29-0600"}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 201
    assert device_id in readings_accessor.device_store.keys()
    assert len(readings_accessor.device_store[device_id].timestamps) == 1
    assert len(readings_accessor.device_store[device_id].readings_list) == 1
    assert readings_accessor.device_store[device_id].count_sum == 52

    # Unrelated data unchanged
    assert len(readings_accessor.device_store[unrelated_device_id].timestamps) == 2
    assert len(readings_accessor.device_store[unrelated_device_id].readings_list) == 2
    assert readings_accessor.device_store[unrelated_device_id].count_sum == 5


def test_create_ignores_duplicate_timestamp_reading(client, helpers):
    device_id = helpers.generate_device_id()
    timestamp = "2024-02-02T08:03:29-0600"
    data = {
        "id": device_id,
        "readings": [{"count": 5, "timestamp": timestamp}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 201
    assert device_id in readings_accessor.device_store.keys()
    assert len(readings_accessor.device_store[device_id].timestamps) == 1
    assert len(readings_accessor.device_store[device_id].readings_list) == 1
    assert readings_accessor.device_store[device_id].count_sum == 5

    # Send same time again
    dupe_data = {
        "id": device_id,
        "readings": [{"count": 53, "timestamp": timestamp}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(dupe_data))
    assert response.status_code == 201
    assert len(readings_accessor.device_store[device_id].timestamps) == 1
    assert len(readings_accessor.device_store[device_id].readings_list) == 1
    assert readings_accessor.device_store[device_id].count_sum == 5

def test_create_returns_error_if_device_id_missing(client):
    data = {"readings": [{"count": 5, "timestamp": "2024-02-02T08:03:29-0600"}]}
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 400
    assert response.json["error_message"] == "Field 'id' is required."

def test_create_returns_error_if_readings_missing(client, helpers):
    data = {"id": helpers.generate_device_id()}
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 400
    assert response.json["error_message"] == "Field 'readings' is required."

def test_create_returns_error_if_device_id_invalid(client):
    data = {
        "id": '679fc0c1d8d3ff14cc8e705ff',
        "readings": [{"count": 5, "timestamp": "2024-02-02T08:03:29-0600"}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 400
    assert response.json["error_message"] == "Device ID must be valid UUID string."

def test_create_returns_error_if_reading_count_not_present(client, helpers):
    device_id = helpers.generate_device_id()
    data = {
        "id": device_id,
        "readings": [{"timestamp": "2024-02-02T08:03:29-0600"}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 400
    assert response.json["error_message"] == "Field 'readings' contains invalid 'count' value. Must be positive integer."

def test_create_returns_error_if_reading_count_not_integer(client, helpers):
    device_id = helpers.generate_device_id()
    data = {
        "id": device_id,
        "readings": [{"timestamp": "2024-02-02T08:03:29-0600", "count": True}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 400
    assert response.json["error_message"] == "Field 'readings' contains invalid 'count' value. Must be positive integer."

def test_create_returns_error_if_reading_count_not_positive(client, helpers):
    device_id = helpers.generate_device_id()
    data = {
        "id": device_id,
        "readings": [{"timestamp": "2024-02-02T08:03:29-0600", "count": 0}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 400
    assert response.json["error_message"] == "Field 'readings' contains invalid 'count' value. Must be positive integer."

def test_create_returns_error_if_reading_timestamp_not_present(client, helpers):
    device_id = helpers.generate_device_id()
    data = {
        "id": device_id,
        "readings": [{"count": 5}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 400
    assert response.json["error_message"] == "Field 'readings' contains invalid 'timestamp' value. Must be ISO-8061 timestamp string."

def test_create_returns_error_if_reading_timestamp_not_string(client, helpers):
    device_id = helpers.generate_device_id()
    data = {
        "id": device_id,
        "readings": [{"count": 5, "timestamp": 1738523887}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 400
    assert response.json["error_message"] == "Field 'readings' contains invalid 'timestamp' value. Must be ISO-8061 timestamp string."

def test_create_returns_error_if_reading_timestamp_not_valid(client, helpers):
    device_id = helpers.generate_device_id()
    data = {
        "id": device_id,
        "readings": [{"count": 5, "timestamp": '2025-02-02 19:18:00.000Z'}]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 400
    assert response.json["error_message"] == "Field 'readings' contains invalid 'timestamp' value. Must be ISO-8061 timestamp string."

def test_create_returns_error_if_one_reading_entry_invalid_but_others_valid(client, helpers):
    device_id = helpers.generate_device_id()
    data = {
        "id": device_id,
        "readings": [
            {"count": 5, "timestamp": "2024-02-02T08:03:29-0600"},
            {"count": 4, "timestamp": "2022-12-23T09:18:01-0600"},
            {"count": 2, "timestamp": "2021-01-01T13:33:13-06:00"},
            # Invalid record
            {"count": 5, "timestamp": '2025-02-02 19:18:00.000Z'}
        ]
    }
    response = client.post(f"/api/device-readings/create",  data=json.dumps(data))
    assert response.status_code == 400
    assert response.json["error_message"] == "Field 'readings' contains invalid 'timestamp' value. Must be ISO-8061 timestamp string."

    # No data saved
    assert device_id not in readings_accessor.device_store.keys()

# --- device-readings cumulative-count endpoint tests
def test_cumulative_count_returns_expected_count(client, helpers):
    device_id = helpers.generate_device_id()
    expected_count = 11
    # Save unrelated readings
    unrelated_device_id = helpers.generate_device_id()
    readings_accessor.save_batch_for_device(
        unrelated_device_id, [{"count": 1, "timestamp": "2021-09-29T16:08:15+01:00"}]
    )

    readings_accessor.save_batch_for_device(
        device_id, [
            {"count": 5, "timestamp": "2024-02-02T08:03:29-0600"},
            {"count": 4, "timestamp": "2022-12-23T09:18:01-0600"},
            {"count": 2, "timestamp": "2021-01-01T13:33:13-06:00"}
        ]
    )
    response = client.get(f"/api/device-readings/{device_id}/cumulative-count")
    assert response.status_code == 200
    assert response.json["cumulative_count"] == expected_count

def test_cumulative_count_returns_expected_count_when_new_readings_added(client, helpers):
    device_id = helpers.generate_device_id()
    initial_count = 4
    later_count = 9
    readings_accessor.save_batch_for_device(
        device_id, [
            {"count": 4, "timestamp": "2024-02-02T08:03:29-0600"}
        ]
    )
    response = client.get(f"/api/device-readings/{device_id}/cumulative-count")
    assert response.status_code == 200
    assert response.json["cumulative_count"] == initial_count

    readings_accessor.save_batch_for_device(
        device_id, [
            {"count": 3, "timestamp": "2024-01-01T08:03:29-0600"},
            {"count": 2, "timestamp": "2020-03-03T09:45:00-0600"}
        ]
    )
    response = client.get(f"/api/device-readings/{device_id}/cumulative-count")
    assert response.status_code == 200
    assert response.json["cumulative_count"] == later_count

def test_cumulative_count_returns_expected_count_when_duplicate_timestamps_ignored(client, helpers):
    device_id = helpers.generate_device_id()
    expected_count = 10
    dupe_timestamp = "2023-11-27T03:55:10-0600"
    readings_accessor.save_batch_for_device(
        device_id, [
            {"count": 5, "timestamp": "2024-02-02T08:03:29-0600"},
            {"count": 5, "timestamp": dupe_timestamp}
        ]
    )
    response = client.get(f"/api/device-readings/{device_id}/cumulative-count")
    assert response.status_code == 200
    assert response.json["cumulative_count"] == expected_count

    # Add new reading with dupe timestamp
    readings_accessor.save_batch_for_device(
        device_id, [
            {"count": 100, "timestamp": dupe_timestamp}
        ]
    )
    response = client.get(f"/api/device-readings/{device_id}/cumulative-count")
    assert response.status_code == 200
    assert response.json["cumulative_count"] == expected_count

def test_cumulative_count_returns_error_if_invalid_device_id_provided(client):
    response = client.get("/api/device-readings/wrong-123/cumulative-count")
    assert response.status_code == 400

    response_data = response.json
    assert response_data["status"] == "error"
    assert response_data["error_message"] == "Device ID must be valid UUID string."

def test_cumulative_count__returns_error_if_no_readings_found(client, helpers):
    device_id = helpers.generate_device_id()
    response = client.get(f"/api/device-readings/{device_id}/cumulative-count")
    assert response.status_code == 404

    response_data = response.json
    assert response_data["status"] == "error"
    assert response_data["error_message"] == "Device readings not found."


# --- device-readings latest-timestamp endpoint tests
def test_latest_timestamp_returns_expected_timestamp(client, helpers):
    device_id = helpers.generate_device_id()
    expected_timestamp = "2024-02-02T11:03:29-0600"
    # Save unrelated timestamp
    unrelated_device_id = helpers.generate_device_id()
    readings_accessor.save_batch_for_device(
        unrelated_device_id, [{"count": 1, "timestamp": "2021-09-29T16:08:15+01:00"}]
    )

    # Save multiple timestamps for target device_id
    readings_accessor.save_batch_for_device(
        device_id, [
            {"count": 9, "timestamp": "2024-02-02T08:03:29-0600"},
            {"count": 9, "timestamp": expected_timestamp},
            {"count": 9, "timestamp": "2021-01-01T13:33:13-06:00"}
        ]
    )
    response = client.get(f"/api/device-readings/{device_id}/latest-timestamp")
    assert response.status_code == 200
    assert response.json["timestamp"] == expected_timestamp

def test_latest_timestamp_returns_expected_timestamp_when_later_time_added(client, helpers):
    device_id = helpers.generate_device_id()
    first_timestamp = "2024-02-02T11:03:29-0600"
    later_timestamp = "2024-02-02T11:33:03-0600"

    readings_accessor.save_batch_for_device(
        device_id, [{"count": 9, "timestamp": first_timestamp}]
    )

    response = client.get(f"/api/device-readings/{device_id}/latest-timestamp")
    assert response.status_code == 200
    assert response.json["timestamp"] == first_timestamp

    # Add later timestamp
    readings_accessor.save_batch_for_device(
        device_id, [{"count": 3, "timestamp": later_timestamp}]
    )
    response = client.get(f"/api/device-readings/{device_id}/latest-timestamp")
    assert response.status_code == 200
    assert response.json["timestamp"] == later_timestamp

def test_latest_timestamp_returns_exepcted_timestamp_when_earlier_time_added(client, helpers):
    device_id = helpers.generate_device_id()
    first_timestamp = "2024-02-02T11:03:29-0600"
    earlier_timestamp = "2024-02-02T11:01:03-0600"

    readings_accessor.save_batch_for_device(
        device_id, [{"count": 9, "timestamp": first_timestamp}]
    )

    response = client.get(f"/api/device-readings/{device_id}/latest-timestamp")
    assert response.status_code == 200
    assert response.json["timestamp"] == first_timestamp

    # Add later timestamp
    readings_accessor.save_batch_for_device(
        device_id, [{"count": 3, "timestamp": earlier_timestamp}]
    )
    response = client.get(f"/api/device-readings/{device_id}/latest-timestamp")
    assert response.status_code == 200
    assert response.json["timestamp"] == first_timestamp

def test_latest_timestamp_returns_error_if_invalid_device_id_provided(client):
    response = client.get("/api/device-readings/wrong-123/latest-timestamp")
    assert response.status_code == 400

    response_data = response.json
    assert response_data["status"] == "error"
    assert response_data["error_message"] == "Device ID must be valid UUID string."

def test_latest_timestamp_returns_error_if_no_readings_found(client, helpers):
    device_id = helpers.generate_device_id()
    response = client.get(f"/api/device-readings/{device_id}/latest-timestamp")
    assert response.status_code == 404

    response_data = response.json
    assert response_data["status"] == "error"
    assert response_data["error_message"] == "Device readings not found."

