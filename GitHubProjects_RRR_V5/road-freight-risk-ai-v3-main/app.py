import streamlit as st

st.set_page_config(
    page_title="🚛 Road Freight Risk AI",
    page_icon="🚛",
    layout="wide"
)

st.title("🚛 Road Freight Risk AI")
st.markdown("### 📱 Mobile-Optimized Risk Reporting System")

st.success("✅ **Deployment Successful!** Your app is now running on Streamlit Cloud.")

# Simple form
with st.form("risk_form"):
    st.header("📍 Submit Risk Report")
    
    location = st.text_input("Location")
    risk_type = st.selectbox("Risk Type", ["Flooding", "Robbery", "Protest", "Road Block", "Other"])
    description = st.text_area("Description")
    
    submitted = st.form_submit_button("Submit Report")
    
    if submitted:
        if location and description:
            st.success("✅ Report submitted successfully!")
        else:
            st.error("❌ Please fill all required fields.")

# Footer
st.markdown("---")
st.markdown("🚛 Road Freight Risk AI v3.0 | Optimized for Streamlit Cloud") 