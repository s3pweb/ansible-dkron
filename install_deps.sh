#!/usr/bin/env bash

echo "Upgrading pip..."
pip install -U pip

echo "Installing wheel..."
pip install wheel

echo "Installing packages from requirements.txt..."
pip install -r requirements.txt

echo "Dependency install complete."
