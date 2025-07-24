#!/bin/bash
# Setup script for Streamlit Cloud deployment

echo "🚀 Setting up Road Freight Risk AI..."

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads
mkdir -p logs

echo "✅ Setup complete!" 