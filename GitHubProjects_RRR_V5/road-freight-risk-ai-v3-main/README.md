# 🚛 Road Freight Risk AI v3.0

A comprehensive road freight risk reporting and safety advice system built with FastAPI backend and Streamlit frontend, optimized for mobile and cloud deployment.

## 🌟 Features

### 🔐 Enhanced Security
- **Password Reset**: Email-based password recovery with JWT tokens
- **JWT Authentication**: Secure session management
- **Input Validation**: Comprehensive form validation and sanitization
- **Role-based Access**: User and admin roles with different permissions

### ⚡ Performance Optimized
- **Caching**: API calls and data processing cached for faster loading
- **Optimized Imports**: Streamlined dependencies for cloud deployment
- **Mobile Responsive**: Optimized UI for mobile devices
- **Streamlit Cloud Ready**: Pre-configured for seamless cloud deployment

### 🗺️ Interactive Maps
- **Folium 0.14.0**: Stable and compatible map visualization
- **GPS Integration**: Automatic location detection
- **Risk Visualization**: Color-coded markers for different risk types
- **Real-time Updates**: Live map updates with new reports

### 🤖 AI-Powered Features
- **Safety Advice Generation**: Context-aware safety recommendations
- **Risk Classification**: AI-powered risk type detection
- **Voice Processing**: Audio report support
- **Community Confirmations**: User-driven risk verification

### 📱 Mobile Support
- **Responsive Design**: Works seamlessly on mobile devices
- **GPS Integration**: Automatic location detection
- **Touch-friendly UI**: Optimized for touch interactions
- **Offline Capabilities**: Basic functionality without internet

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ibrahimlabaranali/RRR2.git
   cd RRR2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp RoadFreightRiskAI_V3.env.txt .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   # Start backend
   cd backend
   uvicorn main:app --reload
   
   # Start frontend (in new terminal)
   cd frontend
   streamlit run streamlit_app.py
   ```

## ☁️ Streamlit Cloud Deployment

### Step 1: Deploy Backend
1. Go to [Render](https://render.com/) or [Railway](https://railway.app/)
2. Connect your GitHub repository
3. Deploy the backend with:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 2: Deploy Frontend
1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Connect your GitHub repository
3. Configure:
   - **Repository**: `ibrahimlabaranali/RRR2`
   - **Main file**: `streamlit_app.py`
   - **Branch**: `main`

### Step 3: Configure Secrets
Add these to Streamlit Cloud secrets:
```toml
[API_URL]
API_URL = "https://your-backend-url.com"

[EMAIL]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
FROM_EMAIL = "your-email@gmail.com"

[SECURITY]
SECRET_KEY = "your-secret-key-here"
JWT_SECRET_KEY = "your-jwt-secret-key"
```

## 📁 Project Structure

```
RRR2/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Backend dependencies
│   └── routes/
│       ├── auth.py          # Authentication endpoints
│       ├── report.py        # Report management
│       ├── advice.py        # Safety advice generation
│       ├── classify.py      # Risk classification
│       └── voice.py         # Voice processing
├── frontend/
│   ├── pages/               # Streamlit pages
│   │   ├── user_dashboard.py
│   │   ├── report_submission.py
│   │   ├── login.py
│   │   └── ...
│   └── static/              # Static assets
└── mobile/                  # Mobile-specific components
```

## 🔧 Configuration

### Environment Variables
- `API_URL`: Backend API URL
- `SMTP_SERVER`: Email server for password reset
- `SMTP_USERNAME`: Email username
- `SMTP_PASSWORD`: Email password
- `SECRET_KEY`: Application secret key
- `JWT_SECRET_KEY`: JWT token secret

### Streamlit Configuration
- `maxUploadSize = 5`: 5MB file upload limit
- `enableCORS = true`: Cross-origin resource sharing
- `showErrorDetails = true`: Detailed error messages

## 🛠️ API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset

### Reports
- `POST /reports/submit` - Submit risk report
- `GET /reports/all` - Get all reports
- `GET /reports/user/{username}` - Get user reports
- `DELETE /reports/{report_id}` - Delete report

### Safety Advice
- `POST /advice/generate` - Generate safety advice
- `POST /advice/confirm` - Confirm risk report
- `GET /advice/confirmations/{risk_type}` - Get confirmations

## 🐛 Troubleshooting

### Common Issues

**ModuleNotFoundError: dotenv**
- Ensure `python-dotenv==1.0.1` is in requirements.txt
- Check that requirements are properly installed

**Map Display Issues**
- Verify `folium==0.14.0` and `streamlit-folium==0.16.0`
- Check browser console for JavaScript errors

**API Connection Errors**
- Verify backend is running and accessible
- Check API_URL in environment variables
- Ensure CORS is properly configured

**File Upload Issues**
- Check `.streamlit/config.toml` has `maxUploadSize = 5`
- Verify file type and size restrictions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the deployment guides

## 🚀 Future Roadmap

- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Machine learning risk prediction
- [ ] Multi-language support
- [ ] Offline mode improvements
- [ ] API rate limiting
- [ ] Advanced security features

---

**Built with ❤️ for safer road transportation** 