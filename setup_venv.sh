#!/bin/bash
set -e

echo "Creating virtual environment..."
python -m venv .venv

echo "Setting up environment from requirements.txt file..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete!"
echo "To activate it, run: source .venv/bin/activate"
echo "To deactivate it, run: deactivate"
