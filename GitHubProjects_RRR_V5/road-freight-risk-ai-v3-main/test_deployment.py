#!/usr/bin/env python3
"""
Test file to verify Streamlit Cloud deployment compatibility
Run this locally to ensure all imports work before deploying
"""

def test_imports():
    """Test all required imports"""
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
        
        import requests
        print("✅ requests imported successfully")
        
        import pandas as pd
        print("✅ pandas imported successfully")
        
        import numpy as np
        print("✅ numpy imported successfully")
        
        import os
        print("✅ os imported successfully")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
        
        print("\n🎉 All imports successful! Ready for Streamlit Cloud deployment.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    test_imports() 