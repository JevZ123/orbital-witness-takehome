# Take home test

## Prerequisites

To run this project you need:
* Python 3
* Run `pip install -r requirements.txt`

## Run the server

To run there are two options:
* `python3 server.py`
* `python3 -m uvicorn server:app --reload`

The server should be running on port 8000 and the `/usage` endpoint service the usage array in the expected format

## Test it

`python -m pytest`

## Lint it

`python3 -m black .`

## Key design decisions

* I used an async call framework for maximum responsiveness and better resource use
* I added both server-side caching and client-side caching to reduce the amount of I/O and calculations needed. The cache timeout was set to 60 seconds, which is just a random value chosen not accounting for how fresh the responses need to be to reflect the rate of change of the data
* I defined the message types using pydantic for input validation. It would have worked just fine without it, but in my opinion it is much better to have at least the externally communicated data structures documented and validated
* I separated the client-facing server logic from the cost calculation logic for ease of readability and coherence. This was combined with a separate file for defining key external communication message formats
* I am testing the final outputs, including using a test client on the server and all the key rules for credit cost calculation to ensure the base cases work

## Concessions

* I had to put all the unit tests for cost calculations into massive test cases with a lot of asserts to save time
* I potentially did not account for edge cases as a result
* I did not structure this readme as well as I could to save time
* I did not do any API documentation auto-generation due to time constraints
* I did not set up more robust formatting rules and linting due to time constraints
* I did add any error propagation to the client
* I did not prepare the project structure for a seamless expansion of tests and capabilities due to time constraints
* I did not create a more complex CI workflow due to time constraints

