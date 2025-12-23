@echo off
title SV Temple Bot Test Suite
echo 🕉 Starting Sri Venkateswara Temple Bot Test Suite...
echo.

:: Navigate to your project directory
cd /d "C:\My_Projects\sv-temple-assistant"

:: Run the script using the full path
python "Test\comprehensive_test_suite.py"

echo.
echo ============================================================
echo Tests Finished. Press any key to close this window.
echo ============================================================
pause