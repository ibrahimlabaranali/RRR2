@echo off
setlocal

REM --- Set paths ---
set PROJECT_DIR=C:\Users\dribr\OneDrive\Dokumentumok\Road Freight Risk AI\GitHub_Road_Freight_Risk_AI_Starter\frontend
set VENV_DIR=%PROJECT_DIR%\venv
set APP_FILE=%PROJECT_DIR%\streamlit_app.py

REM --- Step 1: Activate virtual environment ---
call "%VENV_DIR%\Scripts\activate.bat"

REM --- Step 2: Run Streamlit app ---
echo 🚀 Starting Road Freight Risk AI App...
streamlit run "%APP_FILE%"

endlocal
