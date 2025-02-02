from api.helpers import error_response
from db.device_reading import DeviceReading
from db.device_readings_accessor import readings_accessor
from errors import (
    DeviceNotFoundError,
    InvalidDeviceID,
    InvalidReadingCount,
    InvalidReadingTimestamp,
)
from flask import Blueprint, jsonify, request

api_blueprint = Blueprint("api", __name__, url_prefix="/api")

@api_blueprint.route("/ping", methods=["GET"])
def routes_ping_check():
    # Simple alive check for debugging or uptime monitor
    # Could be adjusted to validate connection to datastore
    return jsonify({"status": "ok"})


@api_blueprint.route("/device-readings/create", methods=["POST"])
def device_readings_create():
    provided_data = request.get_json(force=True)
    device_id = provided_data.get("id", None)
    readings = provided_data.get("readings", None)
    if not device_id:
        return error_response("Field 'id' is required")

    if not readings:
        return error_response("Field 'readings' is required")

    try:
        readings_accessor.save_batch_for_device(device_id, readings)
    except (InvalidReadingCount, InvalidReadingTimestamp, InvalidDeviceID) as e:
        return error_response(e.message, status_code=e.status_code)
    except Exception as e:
        if app.debug:
            raise e
        return error_response("Unknown error occurred")

    return jsonify({"status": "ok"})


# For GETs, opted for placing device_id in URL path as it feels like a targeted resource lookup with
# one expected returned data point ("give me the one field I want for resource X") more than a query
# for one or more matching resources where a query param may be more appropriate as a filter
# criteria ("give me all records where device_id = X"). Could go either way though
@api_blueprint.route("/device-readings/<device_id>/latest-timestamp", methods=["GET"])
def device_readings_latest_timestamp(device_id):
    try:
        latest_timestamp = readings_accessor.retrieve_latest_timestamp(device_id)
    except (InvalidDeviceID, DeviceNotFoundError) as e:
        return error_response(e.message, status_code=e.status_code)
    except Exception as e:
        if app.debug:
            raise e
        return error_response("Unknown error occurred")
    robj = {"timestamp": latest_timestamp.strftime(DeviceReading.timestamp_format())}
    return jsonify(robj)


@api_blueprint.route("/device-readings/<device_id>/cumulative-count", methods=["GET"])
def device_readings_cumulative_count(device_id):
    try:
        sum_count = readings_accessor.retrieve_sum_count(device_id)
    except (InvalidDeviceID, DeviceNotFoundError) as e:
        return error_response(e.message, status_code=e.status_code)
    except Exception as e:
        if app.debug:
            raise e
        return error_response("Unknown error occurred")
    robj = {"cumulative_count": sum_count}
    return jsonify(robj)
