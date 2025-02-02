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

WIP


## Structure Summary

WIP


## Todo With More Time

WIP
