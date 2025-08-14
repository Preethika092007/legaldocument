import streamlit as st
import os
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="ClauseWise",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    if 'document_history' not in st.session_state:
        st.session_state.document_history = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = {}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

# Global CSS styling
def load_css():
    """Load custom CSS styling"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global styles */
    .main {
        font-family: 'Inter', Arial, Helvetica, sans-serif;
        background-color: #F8F9FA;
        min-height: 100vh;
    }

    .stApp {
        background-color: #F8F9FA;
    }

    /* Header styles */
    .header {
        position: sticky;
        top: 0;
        z-index: 1000;
        background: white;
        padding: 1rem 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        border-bottom: 1px solid #E9ECEF;
    }

    .logo {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-decoration: none;
        letter-spacing: -0.5px;
    }

    .nav-menu {
        display: flex;
        gap: 1rem;
    }

    .nav-item {
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        text-decoration: none;
        color: #4a5568;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .nav-item:hover {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }

    .nav-item.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    /* Card styles */
    .card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        margin-bottom: 2rem;
        border: 1px solid #E9ECEF;
        position: relative;
    }

    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(135deg, #007BFF, #20C997);
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    /* Button styles */
    .btn-primary {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 1rem 2.5rem;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 1rem;
        letter-spacing: 0.5px;
    }

    .btn-primary:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8, #6b46c1);
    }

    /* Footer styles */
    .footer {
        background-color: #F8F9FA;
        text-align: center;
        padding: 2rem;
        margin-top: 4rem;
        border-top: 1px solid #E9ECEF;
        color: #6C757D;
        font-size: 0.9rem;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Streamlit specific styling */
    .stFileUploader > div > div > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(102, 126, 234, 0.5);
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }

    .stFileUploader > div > div > div > div:hover {
        border-color: #667eea;
        background: rgba(255, 255, 255, 0.15);
    }

    .stButton > button {
        background: linear-gradient(135deg, #007BFF, #20C997) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 10px rgba(0, 123, 255, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0, 123, 255, 0.4) !important;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .header {
            flex-direction: column;
            gap: 1rem;
            padding: 1rem;
        }

        .nav-menu {
            flex-direction: column;
            width: 100%;
            text-align: center;
            gap: 0.5rem;
        }

        .card {
            padding: 1.5rem;
            margin: 1rem;
        }

        .logo {
            font-size: 1.8rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Header component
def render_header():
    """Render the sticky header with navigation"""
    current_page = st.session_state.get('current_page', 'Dashboard')
    
    st.markdown(f"""
    <div class="header">
        <div class="logo">ClauseWise</div>
        <nav class="nav-menu">
            <a href="?page=dashboard" class="nav-item {'active' if current_page == 'Dashboard' else ''}">Dashboard</a>
            <a href="?page=history" class="nav-item {'active' if current_page == 'History' else ''}">History</a>
            <a href="?page=analysis" class="nav-item {'active' if current_page == 'Analysis' else ''}">Live Analysis</a>
        </nav>
    </div>
    """, unsafe_allow_html=True)

# Footer component
def render_footer():
    """Render the footer"""
    st.markdown("""
    <div class="footer">
        © 2025 ClauseWise. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

# Navigation logic
def handle_navigation():
    """Handle page navigation"""
    # Use sidebar for navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")

        # Get current page index based on session state
        pages = ["Dashboard", "History", "Analysis"]
        current_index = pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0

        page = st.radio(
            "Go to:",
            pages,
            index=current_index,
            key="nav_radio"
        )

        # Update session state if page changed
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.rerun()

    # Show the selected page based on session state
    if st.session_state.current_page == 'Dashboard':
        from pages import dashboard
        dashboard.show()
    elif st.session_state.current_page == 'History':
        from pages import history
        history.show()
    elif st.session_state.current_page == 'Analysis':
        from pages import analysis
        analysis.show()
    else:
        from pages import dashboard
        dashboard.show()

# Main application
def main():
    """Main application entry point"""
    init_session_state()
    load_css()
    render_header()
    
    # Handle navigation
    handle_navigation()
    
    render_footer()

if __name__ == "__main__":
    main()
