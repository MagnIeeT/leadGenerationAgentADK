#!/bin/bash

# This script builds the LeadGenerationResearch package into a wheel file using Poetry.

# Exit immediately if a command exits with a non-zero status.
set -e

# The directory where the wheel file will be placed.
OUTPUT_DIR="deployment"

# Ensure Poetry is installed.
if ! command -v poetry &> /dev/null
then
    echo "Poetry could not be found. Please install it first."
    exit
fi

# Remove any previous builds from the dist directory.
rm -rf dist

# Build the wheel file using Poetry.
poetry build --format=wheel

# Move the wheel file to the output directory.
mv dist/*.whl "${OUTPUT_DIR}/"

echo "✅ Wheel file created and moved to ${OUTPUT_DIR}/"
