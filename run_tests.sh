#!/bin/bash

# run all the tests
# -rxXs shows extra info on xFail and skipped tests
# -s show printed messages
# -vvv verbose mode
pytest -rxXs -s -vvv examples/tests/
