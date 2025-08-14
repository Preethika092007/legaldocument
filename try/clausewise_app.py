import streamlit as st
import os
from datetime import datetime
import base64
from utils import (
    extract_text_from_file, save_document_to_history, get_file_type_icon,
    generate_summary, classify_document_type, extract_named_entities,
    simplify_clauses, extract_key_clauses, chatbot_response, text_to_speech,
    highlight_entities_in_text
)
import plotly.graph_objects as go

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
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Poppins', Arial, Helvetica, sans-serif;
        background-color: #F8F9FA;
    }
    
    .card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        margin-bottom: 2rem;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #007BFF, #20C997);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,123,255,0.4);
    }
    
    .footer {
        background-color: #F8F9FA;
        text-align: center;
        padding: 2rem;
        margin-top: 4rem;
        border-top: 1px solid #E9ECEF;
        color: #6C757D;
        font-size: 0.9rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Header component
def render_header():
    """Render the header"""
    st.markdown("""
    <div style="
        background: white;
        padding: 1rem 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border-radius: 12px;
    ">
        <h1 style="
            color: #007BFF;
            text-align: center;
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        ">📄 ClauseWise</h1>
        <p style="
            text-align: center;
            color: #6C757D;
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
        ">AI-Powered Legal Document Analysis</p>
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

def dashboard_page():
    """Dashboard page content"""
    st.markdown("## 📁 Upload Document")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_file is not None:
        # Process the uploaded file
        with st.spinner("Processing document..."):
            extracted_text = extract_text_from_file(uploaded_file)
            
            if extracted_text:
                # Save to session state
                st.session_state.uploaded_file = uploaded_file
                st.session_state.extracted_text = extracted_text
                
                # Save to history
                save_document_to_history(
                    uploaded_file.name,
                    uploaded_file.type,
                    extracted_text
                )
                
                st.success(f"✅ Successfully processed {uploaded_file.name}")

                # Show file info
                st.info(f"""
                **File:** {uploaded_file.name}
                **Type:** {uploaded_file.type}
                **Size:** {len(extracted_text)} characters
                **Preview:** {extracted_text[:200]}...
                """)

                # Add navigation button
                if st.button("🔍 Go to Analysis", key="goto_analysis"):
                    st.session_state.current_page = "Analysis"
                    st.rerun()

def history_page():
    """History page content"""
    st.markdown("## 📚 Document History")
    
    if not st.session_state.document_history:
        st.info("No documents uploaded yet. Go to Dashboard to upload your first document.")
        return
    
    # Display document history
    for i, doc in enumerate(st.session_state.document_history):
        with st.expander(f"{get_file_type_icon(doc['file_type'])} {doc['filename']} - {doc['upload_date']}"):
            st.write(f"**Type:** {doc['file_type']}")
            st.write(f"**Size:** {len(doc['text'])} characters")
            st.write(f"**Preview:** {doc['text'][:300]}...")
            
            if st.button(f"📖 Analyze", key=f"analyze_doc_{i}"):
                st.session_state.uploaded_file = None
                st.session_state.extracted_text = doc['text']
                st.session_state.current_page = "Analysis"
                st.success("✅ Document loaded! Redirecting to Analysis page...")
                st.rerun()

def analysis_page():
    """Analysis page content"""
    st.markdown("## 🔍 Document Analysis")
    
    if not st.session_state.extracted_text:
        st.warning("No document selected for analysis. Please upload a document first.")
        return
    
    # Document preview
    st.markdown("### 📖 Document Preview")
    with st.expander("View Document Text", expanded=False):
        st.text_area("Document Content", st.session_state.extracted_text, height=200)
    
    # Analysis sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Document Analysis")
        
        # Generate analysis if not done
        if 'document_analysis' not in st.session_state:
            with st.spinner("Analyzing document..."):
                st.session_state.document_analysis = {
                    'document_type': classify_document_type(st.session_state.extracted_text),
                    'key_clauses': extract_key_clauses(st.session_state.extracted_text),
                    'entities': extract_named_entities(st.session_state.extracted_text)
                }
        
        analysis = st.session_state.document_analysis
        
        st.info(f"**Document Type:** {analysis['document_type']}")
        st.success(f"**Key Clauses:** {analysis['key_clauses'][:200]}...")
        st.warning(f"**Named Entities:** {analysis['entities'][:200]}...")
    
    with col2:
        st.markdown("### 📄 Document Summary")
        
        # Generate summary if not done
        if 'document_summary' not in st.session_state:
            with st.spinner("Generating summary..."):
                st.session_state.document_summary = generate_summary(st.session_state.extracted_text)
        
        st.write(st.session_state.document_summary)
        
        # TTS controls
        if st.button("🎵 Generate Audio"):
            with st.spinner("Converting to speech..."):
                audio_data = text_to_speech(st.session_state.document_summary)
                if audio_data:
                    st.session_state.audio_data = audio_data
                    st.success("Audio generated!")
        
        if 'audio_data' in st.session_state:
            st.markdown(f"""
            <audio controls style="width: 100%;">
                <source src="data:audio/wav;base64,{st.session_state.audio_data}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
            """, unsafe_allow_html=True)
    
    # Chatbot section
    st.markdown("### 🤖 Ask Questions About Your Document")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI:** {message['content']}")
    
    # Chat input
    user_question = st.text_input("Ask a question about your document...")
    
    if st.button("Send") and user_question:
        # Add user message to chat history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_question
        })
        
        # Generate AI response
        with st.spinner("Thinking..."):
            ai_response = chatbot_response(user_question, st.session_state.extracted_text)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': ai_response
            })
        
        st.rerun()

def main():
    """Main application"""
    init_session_state()
    load_css()
    render_header()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")

        # Get current page index
        pages = ["Dashboard", "History", "Analysis"]
        current_index = pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0

        page = st.radio("Go to:", pages, index=current_index, key="nav_radio")

        # Update session state if page changed
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.rerun()

    # Show selected page
    if st.session_state.current_page == "Dashboard":
        dashboard_page()
    elif st.session_state.current_page == "History":
        history_page()
    elif st.session_state.current_page == "Analysis":
        analysis_page()
    
    render_footer()

if __name__ == "__main__":
    main()
