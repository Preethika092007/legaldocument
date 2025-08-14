#!/usr/bin/env python3
"""
Test script for ClauseWise application

This script tests the basic functionality of the ClauseWise application
to ensure all components are working correctly.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError:
        print("❌ Failed to import Streamlit")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError:
        print("❌ Failed to import Requests")
        return False
    
    try:
        import pdfplumber
        print("✅ PDFPlumber imported successfully")
    except ImportError:
        print("❌ Failed to import PDFPlumber")
        return False
    
    try:
        from docx import Document
        print("✅ Python-docx imported successfully")
    except ImportError:
        print("❌ Failed to import Python-docx")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError:
        print("❌ Failed to import Plotly")
        return False
    
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        "app.py",
        "utils.py",
        "requirements.txt",
        "README.md",
        "pages/__init__.py",
        "pages/dashboard.py",
        "pages/history.py",
        "pages/analysis.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_utils_functions():
    """Test utility functions"""
    print("\nTesting utility functions...")
    
    try:
        from utils import MODEL_URLS, HF_API_KEY, HF_HEADERS
        print("✅ Configuration variables loaded")
        
        # Test if API key is set
        if HF_API_KEY and HF_API_KEY.startswith("hf_"):
            print("✅ Hugging Face API key is properly configured")
        else:
            print("❌ Hugging Face API key not properly configured")
            return False
        
        # Test if model URLs are configured
        if len(MODEL_URLS) == 4:
            print("✅ All model URLs configured")
        else:
            print("❌ Model URLs not properly configured")
            return False
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import utils: {e}")
        return False

def test_pages():
    """Test if page modules can be imported"""
    print("\nTesting page modules...")
    
    try:
        from pages import dashboard, history, analysis
        print("✅ All page modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import page modules: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 ClauseWise Application Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("File Structure Test", test_file_structure),
        ("Utils Functions Test", test_utils_functions),
        ("Page Modules Test", test_pages)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ClauseWise is ready to run.")
        print("🚀 Run 'python run.py' or 'streamlit run app.py' to start the application.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
