#!/bin/bash

echo "📦 Setting up your Flask environment..."

# Step 1: Ensure python3-venv is installed
echo "🔧 Ensuring 'python3-venv' and 'build-essential' are installed..."
sudo apt update
sudo apt install -y python3-venv build-essential libssl-dev libffi-dev python3-dev

# Step 2: Create virtual environment if it doesn't exist
if [ ! -d "myenv" ]; then
    echo "🐍 Creating virtual environment in 'myenv'..."
    python3 -m venv myenv
else
    echo "✅ Virtual environment already exists."
fi

# Step 3: Activate virtual environment
echo "📥 Activating virtual environment..."
source myenv/bin/activate

# Step 4: Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --break-system-packages

# Step 5: Install all necessary Python packages
echo "📦 Installing Flask and other critical packages..."
pip install --break-system-packages \
    Flask \
    Flask-WTF \
    Pillow \
    Flask-SQLAlchemy \
    WTForms \
    email-validator \
    python-dotenv \
    PyMySQL \
    cryptography

# Step 6: Confirm installation
echo "✅ All dependencies installed and environment ready!"
