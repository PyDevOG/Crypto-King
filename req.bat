@echo off
rem Install required packages for Python
pip install requests
pip install numpy
pip install scikit-learn
rem Check if tkinter is already installed
python -c "import tkinter" 2> NUL
if %errorlevel% neq 0 (
    rem If tkinter is not installed, install it using the appropriate package manager
    pip install tk
)
rem Additional packages
pip install json-logging-py
