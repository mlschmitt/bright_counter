# Bright Counter

Implementation of in-memory device readings API.

* Python 3.13
* Local API Port: `9000`


## Run the Server

### With Docker

1. cd into project directory, run Docker compose:
```bash
docker compose up -d
```

Server should now be accessible at `http://localhost:9000`


### Without Docker

1. Install Python 3.13
2. Create 3.13 virtualenv if needed:

```bash
python3.13 -m venv venv313; source venv313/bin/activate
```

3. cd into project directory, install requirements:

```bash
pip3 install -r requirements.txt
```

4. Boot Flask

```bash
python app.py
```

Server should now be accessible at `http://localhost:9000`


## Run Tests

1. Run 'Without Docker' steps above to ensure dependencies are installed, including pytest
2. cd into project directory, run pytest:

```bash
pytest
```


## Endpoints

### Uptime Check

Verify server is up and accessible.

* Path: `/api/ping`
* Method: `GET`
* Required Params: None
* Returns on success: JSON, `200 OK`

```json
{"status": "ok"}
```

### Create device readings

Insert one or more new count/timestamp readings for a specified device.

* Path: `/api/device-readings/create`
* Method: `POST`
* Required body (JSON):
    * `id` - String, UUID4 format. Represents device ID. Ex: `"063c5957-8905-45f9-bfe3-960713788919"`
    * `readings` - Array of one or more reading dictionaries
        * `readings.count` - Integer, must be positive. Ex: `9`
        * `readings.timestamp` - String of ISO-8061 timestamp: `%Y-%m-%dT%H:%M:%S%z`. Ex: `"2021-09-29T16:09:15+01:00"`
* Returns on success: JSON, `201 Created`

```json
{"status": "ok"}
```

* Returns on error: JSON, status code varies (also included in response body)

```json
{
    "status": "error",
    "error_message": "Explanation of specific error",
    "status_code": 400
}
```


### Retrieve device latest timestamp

Retrieve a target device's latest store reading timestamp. Note will return 404 error if specified device has no stored readings.

* Path: `/api/device-readings/<device_id_uuid>/latest-timestamp`
* Method: `GET`
* Required Params: None
* Returns on success: JSON, `200 OK`

```json
{"timestamp": "2012-09-29T16:08:15+0100"}
```

* Returns on error: JSON, status code varies (also included in response body)

```json
{
    "status": "error",
    "error_message": "Explanation of specific error",
    "status_code": 400
}
```


### Retrieve device cumulative count

Retrieve a target device's sum of all stored `count` values. Note will return 404 error if specified device has no stored readings.

* Path: `/api/device-readings/<device_id_uuid>/cumulative-count`
* Method: `GET`
* Required Params: None
* Returns on success: JSON, `200 OK`

```json
{"cumulative_count": 23}
```

* Returns on error: JSON, status code varies (also included in response body)

```json
{
    "status": "error",
    "error_message": "Explanation of specific error",
    "status_code": 400
}
```



## Structure Summary

WIP


## Todo With More Time / Next Steps

* Move repeated/shared API route handler functionality into a MethodView-style base class; pivot endpoint functions into classes
    * Would help speed future development as well: handlers for validating only allowed fields/params are provided in the request, all required fields are present, formatting/returning errors, generic exception handler, etc.
* More tests
    * I think I covered most happy/error paths in general but strictly through interactions with the API routes. There are no tests directly flexing the underlying device storage classes which I would want to add with more time.
    * These would be a requirement before building out any additional functionality that interacted with these classes outside of the existing API endpoints. Maybe could even then potentially simplify the API tests, just asserting mocks of the underlying data class functions are called and trusting other tests flex their behavior.
* Real data store
    * Current implementation is not thread-safe, in addition to other drawbacks like losing all data when server restarted
    * Unless project / product requirements prohibit, we should shift to using more resilient data store.
    * Ideally a SQL database. Could potentially have a `devices` table (if needed), and then `device_readings` to save each new reading. Could simplify Python codebase to achieve current requirements: Unique constraint on `device_id` and `timestamp` columns could block duplicates; `ORDER BY timestamp DESC` and `SUM(count)` could retrieve desired data. If needed perhaps such values could live as explicit columns in `devices`, recalculated on a trigger, depending on performance and usage needs.
    * If permanent datastore not an option, then memory option like Redis or memcached. Potentially could rely on pickle'ing current Python objects to push as-is into Redis if needed.
* Investigate performance / memory use
    * How many device readings are we expecting: dozens? Millions? What's the throughput?
    * Expectations on response time?
    * If these are unknown, or currently small but we hope to grow, implement monitoring
    * If we need to retain in-Python memory datastore, I would want to spend a bit of time benchmarking current implementation
    * Especially `__slots__` usage: impact on memory use, especially with more info on use case. Is it worth the constraints
* Implement monitoring with third-party services
    * Tracing like New Relic to monitor for response times, throughput, capture problem tracelogs
    * Error tracking (like Sentry)
    * Log collection (like Papertrail)
 * Rethink API endpoint structure
    * Perhaps with more requirements / features it will become clearer if restructuring needed. For example, if other device aggregate-level data needed, perhaps the 2 current endpoints for latest-timestamp and cumulative-count instead are merged into a single endpoint retrieving all top-level data on a target device with a query param to limit returned fields
    * Or, if needs arise that multiple device data need to be returned, perhaps `device_id` shifts to a query param supporting multiple values
    * Ideally I could ask a PM such "near-future needs" questions to try to get on the right foot from the getgo
