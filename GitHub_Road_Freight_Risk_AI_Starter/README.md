# Road Freight Risk AI App

## 🌍 Overview
This app helps Nigerian freight drivers and authorities classify, report, and respond to road-related travel risks such as banditry, protests, and flooding.

## 📦 Modules
- `backend/`: FastAPI backend
- `frontend/streamlit/`: User and Admin dashboards
- `mobile/`: React Native (Expo) starter

## 🚀 Deployment
### Backend (Render)
1. Push to GitHub
2. Create a new Render web service
3. Use `uvicorn backend.main:app --host=0.0.0.0 --port=10000`

### Frontend (Streamlit)
1. Link GitHub repo
2. Set main file to `user_dashboard.py`

## 📱 Mobile App
Built with React Native + Expo (see `mobile/`)

## 📊 LGA Mapping
Based on Nigeria’s 774 LGAs using `nigeria_lgas.json`
