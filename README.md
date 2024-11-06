# Take home test

## Run it

To run there are two options:
* `python3 server.py`
* `python3 -m uvicorn server:app --reload`

The server should be running on port 8000 and the `/usage` endpoint service the usage array in the expected format

## Test it

`python -m pytest`

## Lint it

`python3 -m black .`