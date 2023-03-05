#!/bin/bash

cd "$(dirname "$0")"
poetry build
pip install -e .
