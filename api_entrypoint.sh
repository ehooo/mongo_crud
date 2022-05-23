#!/bin/bash

# Setup custom API
python3 main.py --fixtures
uvicorn main:app --host=0.0.0.0 --port=8000 ${API_ARGS}
