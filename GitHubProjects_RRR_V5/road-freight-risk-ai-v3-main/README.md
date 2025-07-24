# 🚛 Road Freight Risk AI  
**Version 3 – Enhanced Security & Safety Features**

A comprehensive AI-powered platform that enables **real-time risk reporting, context-aware safety advice, and secure user management** for road freight hazards in Nigeria and beyond.

## 🆕 **New Features in V3**

### 🔐 **Enhanced Security**
- **Secure Password Reset**: JWT-based password reset with email verification
- **Email Registration**: User registration with email validation
- **Password Strength Validation**: Enforced strong password requirements
- **Session Management**: Secure user session handling

### 🛡️ **Context-Aware Safety Advice**
- **AI-Generated Advice**: Real-time safety recommendations based on risk type and location
- **Confirmation System**: Driver confirmation tracking for risk validation
- **Time-Specific Guidance**: Advice tailored to time of day and risk patterns
- **Severity Assessment**: Dynamic risk severity based on confirmations and recent reports

### 📋 **Enhanced Report Submission**
- **Confirmation Prompts**: Two-step submission process with user confirmation
- **File Upload Support**: Image and audio attachments (max 5MB)
- **"Other" Risk Type**: Custom risk descriptions with validation
- **GPS Integration**: Automatic location capture with manual fallback

### 📊 **Improved User Experience**
- **Real-time Feedback**: Immediate safety advice after report submission
- **Confirmation Tracking**: Visual display of driver confirmations
- **Enhanced Validation**: Comprehensive form validation with clear error messages
- **Mobile Optimization**: Responsive design for mobile devices

---

## 🧠 **System Overview**

Road Freight Risk AI leverages **machine learning**, **user reports**, **geolocation**, and **community confirmations** to classify and communicate incidents such as:

- 🚨 **Security Risks**: Armed robbery, banditry, kidnapping
- 🌊 **Environmental Hazards**: Flooding, road closures
- 📢 **Civil Unrest**: Protests, riots, strikes
- 🚗 **Traffic Incidents**: Accidents, congestion
- ⚠️ **Other Hazards**: Custom risk types with detailed descriptions

---

## 📁 **Project Structure**

```
road-freight-risk-ai-v3-main/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── routes/
│   │   ├── auth.py            # Authentication & password reset
│   │   ├── classify.py        # Risk classification AI
│   │   ├── report.py          # Report submission & management
│   │   ├── voice.py           # Voice processing
│   │   └── advice.py          # Safety advice generation
│   └── uploads/               # File upload storage
├── frontend/
│   ├── streamlit_app.py       # Main Streamlit application
│   ├── requirements.txt       # Frontend dependencies
│   ├── pages/
│   │   ├── login.py           # User login
│   │   ├── signup.py          # User registration
│   │   ├── forgot_password.py # Password reset request
│   │   ├── reset_password.py  # Password reset form
│   │   ├── report_submission.py # Enhanced report submission
│   │   ├── user_dashboard.py  # User dashboard
│   │   └── admin_dashboard.py # Admin dashboard
│   └── static/               # Static assets
├── mobile/                   # Mobile-optimized version
├── render.yaml              # Deployment configuration
└── RoadFreightRiskAI_V3.env.txt # Environment variables template
```

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- pip
- Git

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd road-freight-risk-ai-v3-main
```

### **2. Backend Setup**
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../RoadFreightRiskAI_V3.env.txt .env
# Edit .env with your configuration

# Test folium compatibility (optional)
python ../test_folium_compatibility.py

# Run the backend
python main.py
```

### **3. Frontend Setup**
```bash
cd frontend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../RoadFreightRiskAI_V3.env.txt .env
# Edit .env with your configuration

# Run the frontend
streamlit run streamlit_app.py
```

### **4. Access the Application**
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:8501

---

## ⚙️ **Configuration**

### **Environment Variables**

Create a `.env` file in both `backend/` and `frontend/` directories:

```env
# API Configuration
API_URL=http://localhost:8000
SECRET_KEY=your-super-secret-key

# Email Configuration (for password reset)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@roadriskai.com

# Database Configuration
USER_DB=users.db
REPORT_DB=reports.db

# Security Configuration
PASSWORD_MIN_LENGTH=8
RESET_TOKEN_EXPIRY_HOURS=1
MAX_FILE_SIZE=5242880
```

### **Email Setup (Gmail Example)**

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use the generated password in `SMTP_PASSWORD`

---

## 🔐 **Security Features**

### **Password Reset Flow**
1. User requests password reset via email
2. System validates email and generates JWT token
3. Reset link sent via email (expires in 1 hour)
4. User clicks link and sets new password
5. Token is invalidated after use

### **Data Protection**
- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Comprehensive validation on all inputs
- **File Upload Security**: Type and size validation
- **SQL Injection Protection**: Parameterized queries

### **User Privacy**
- **Email Privacy**: Reset emails don't reveal if email exists
- **Location Data**: GPS coordinates stored securely
- **Report Anonymity**: Optional anonymous reporting

---

## 📊 **API Endpoints**

### **Authentication**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

### **Reports**
- `POST /reports/submit` - Submit risk report
- `POST /reports/submit-with-file` - Submit report with file
- `GET /reports/all` - Get all reports (admin)
- `GET /reports/user/{username}` - Get user reports
- `GET /reports/{report_id}` - Get specific report

### **Safety Advice**
- `POST /advice/generate` - Generate safety advice
- `POST /advice/confirm` - Confirm risk report
- `GET /advice/confirmations/{risk_type}` - Get confirmations
- `GET /advice/trending` - Get trending risks

### **Classification**
- `POST /classify/text` - Classify risk from text
- `POST /voice/upload` - Process voice reports

---

## 🛡️ **Safety Advice System**

### **Context-Aware Generation**
The system generates safety advice based on:
- **Risk Type**: Specific guidance for each risk category
- **Location**: Geographic context and local conditions
- **Time of Day**: Time-specific risk patterns
- **Confirmation Count**: Community validation level
- **Recent Reports**: Frequency of similar incidents

### **Advice Categories**
- **High Severity**: Critical warnings with immediate action required
- **Medium Severity**: Cautionary advice with alternative routes
- **Low Severity**: General safety reminders

### **Example Advice**
```
🚨 CRITICAL: Avoid this route immediately. Armed robbery reported.
🛡️ Use alternative routes and travel in convoy if possible.
📱 Contact local authorities and report suspicious activity.
⏰ Avoid travel during early morning (4-6 AM) and late evening (8-10 PM).
✅ Confirmed by 3 other drivers
📊 2 recent reports in this area
```

---

## 📱 **Mobile Support**

The application is fully responsive and optimized for mobile devices:
- **Touch-friendly interface**
- **GPS integration**
- **Voice reporting**
- **Offline capability** (PWA features)
- **Push notifications** (future feature)

---

## 🚀 **Deployment**

### **Render Deployment**
1. Fork the repository
2. Connect to Render
3. Configure environment variables
4. Deploy automatically

### **Local Production**
```bash
# Backend
cd backend
pip install -r requirements.txt
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8501
```

---

## 🧪 **Testing**

### **API Testing**
```bash
cd backend
pytest tests/
```

### **Manual Testing**
1. **User Registration**: Test email validation and password strength
2. **Password Reset**: Test complete reset flow
3. **Report Submission**: Test with and without files
4. **Safety Advice**: Verify context-aware advice generation
5. **Confirmation System**: Test risk confirmation flow

---

## 🔧 **Troubleshooting**

### **Common Issues**

**Email Not Sending**
- Check SMTP credentials
- Verify 2FA is enabled for Gmail
- Check firewall settings

**File Upload Fails**
- Verify file size < 5MB
- Check file type is supported
- Ensure upload directory exists

**Map Display Issues**
- Run `python test_folium_compatibility.py` to verify folium installation
- Ensure folium version is 0.14.0: `pip show folium`
- Check that branca 0.6.0 is installed: `pip show branca`

**GPS Not Working**
- Check browser permissions
- Verify HTTPS for production
- Test with manual coordinates

**Database Errors**
- Check file permissions
- Verify database path
- Ensure SQLite is installed

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### **Development Guidelines**
- Follow PEP 8 style guide
- Add type hints
- Include docstrings
- Write unit tests
- Update documentation

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 **Support**

- **Documentation**: Check this README and API docs
- **Issues**: Report bugs via GitHub Issues
- **Email**: support@roadriskai.com

---

## 🔮 **Future Roadmap**

- **Real-time Notifications**: Push notifications for new risks
- **Social Media Integration**: Risk sharing on social platforms
- **Advanced AI**: Machine learning for risk prediction
- **Mobile App**: Native iOS/Android applications
- **Analytics Dashboard**: Advanced reporting and analytics
- **Multi-language Support**: Localization for different regions

## 🗺️ **Map Compatibility**

The application uses **folium 0.14.0** for map visualization, which provides:
- **Stable Performance**: Well-tested version with minimal breaking changes
- **Wide Compatibility**: Works across different Python versions and platforms
- **Feature Rich**: Supports markers, heatmaps, popups, and custom styling
- **Streamlit Integration**: Seamless integration with streamlit-folium 0.16.0

### **Testing Map Compatibility**
Run the compatibility test to verify your installation:
```bash
python test_folium_compatibility.py
```

This will test all folium features used in the application and ensure everything works correctly.

---

**Built with ❤️ for safer roads**

