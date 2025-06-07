@echo off
setlocal

REM --- Set paths ---
set PROJECT_DIR=C:\Users\dribr\OneDrive\Dokumentumok\Road Freight Risk AI\GitHub_Road_Freight_Risk_AI_Starter\frontend
set VENV_DIR=%PROJECT_DIR%\venv
set REQ_FILE=%PROJECT_DIR%\requirements.txt

REM --- Step 1: Create virtual environment if it doesn't exist ---
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

REM --- Step 2: Activate virtual environment ---
call "%VENV_DIR%\Scripts\activate.bat"

REM --- Step 3: Install requirements ---
echo Installing dependencies from requirements.txt...
pip install --upgrade pip
pip install -r "%REQ_FILE%"

echo.
echo ✅ Environment is ready. You can now run your Streamlit app.
echo 💡 Use: streamlit run frontend\streamlit_app.py

pause
endlocal
