import streamlit as st
from utils import get_file_type_icon

def show():
    """Display the history page"""
    
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #007BFF; text-align: center; margin-bottom: 1rem;">📚 Document History</h1>
        <p style="text-align: center; color: #6C757D; font-size: 1.1rem;">
            View and manage your previously analyzed documents
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if there are any documents in history
    if not st.session_state.document_history:
        render_empty_history()
    else:
        render_document_grid()

def render_empty_history():
    """Render empty state when no documents are in history"""
    st.markdown("""
    <div class="card" style="text-align: center; padding: 4rem 2rem;">
        <div style="font-size: 4rem; margin-bottom: 2rem;">📂</div>
        <h3 style="color: #6C757D; margin-bottom: 1rem;">No Documents Yet</h3>
        <p style="color: #6C757D; margin-bottom: 2rem;">
            Upload your first document to start building your analysis history
        </p>
    """, unsafe_allow_html=True)
    
    if st.button("📁 Upload Document", key="upload_from_history"):
        st.info("📍 Use the navigation menu to go to Dashboard page.")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_document_grid():
    """Render responsive grid of document history cards"""
    
    # Add search and filter options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search documents", placeholder="Search by filename...")
    
    with col2:
        file_type_filter = st.selectbox(
            "📄 Filter by type",
            ["All", "PDF", "DOCX", "TXT"]
        )
    
    with col3:
        sort_option = st.selectbox(
            "📅 Sort by",
            ["Newest First", "Oldest First", "Name A-Z", "Name Z-A"]
        )
    
    # Filter and sort documents
    filtered_docs = filter_and_sort_documents(search_term, file_type_filter, sort_option)
    
    if not filtered_docs:
        st.warning("No documents match your search criteria.")
        return
    
    # Display document count
    st.markdown(f"""
    <div style="margin: 2rem 0 1rem 0; color: #6C757D;">
        Showing {len(filtered_docs)} of {len(st.session_state.document_history)} documents
    </div>
    """, unsafe_allow_html=True)
    
    # Responsive grid layout
    st.markdown("""
    <style>
    .doc-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .doc-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .doc-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #007BFF;
    }
    
    .doc-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .doc-title {
        font-weight: 600;
        color: #333333;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        word-break: break-word;
    }
    
    .doc-meta {
        color: #6C757D;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .doc-preview {
        color: #6C757D;
        font-size: 0.85rem;
        line-height: 1.4;
        max-height: 60px;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    @media (max-width: 768px) {
        .doc-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create grid container
    st.markdown('<div class="doc-grid">', unsafe_allow_html=True)
    
    # Render document cards
    for i, doc in enumerate(filtered_docs):
        render_document_card(doc, i)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_document_card(doc, index):
    """Render individual document card"""
    file_icon = get_file_type_icon(doc['file_type'])
    preview_text = doc['text'][:150] + "..." if len(doc['text']) > 150 else doc['text']
    
    # Create a unique key for each card button
    card_key = f"doc_card_{doc['id']}_{index}"
    
    st.markdown(f"""
    <div class="doc-card" onclick="selectDocument({doc['id']})">
        <div class="doc-icon">{file_icon}</div>
        <div class="doc-title">{doc['filename']}</div>
        <div class="doc-meta">
            📅 {doc['upload_date']}<br>
            📊 {len(doc['text'])} characters
        </div>
        <div class="doc-preview">{preview_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Use columns to create invisible buttons for each card
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("📖 Analyze", key=f"analyze_{card_key}"):
            # Set the selected document in session state
            st.session_state.uploaded_file = None  # Clear current file
            st.session_state.extracted_text = doc['text']
            st.session_state.current_document = doc
            
            # Document loaded message
            st.success("✅ Document loaded! Use the navigation menu to go to Analysis page.")

def filter_and_sort_documents(search_term, file_type_filter, sort_option):
    """Filter and sort documents based on user criteria"""
    docs = st.session_state.document_history.copy()
    
    # Apply search filter
    if search_term:
        docs = [doc for doc in docs if search_term.lower() in doc['filename'].lower()]
    
    # Apply file type filter
    if file_type_filter != "All":
        filter_mapping = {
            "PDF": "pdf",
            "DOCX": "word",
            "TXT": "text"
        }
        filter_type = filter_mapping.get(file_type_filter, "")
        docs = [doc for doc in docs if filter_type in doc['file_type'].lower()]
    
    # Apply sorting
    if sort_option == "Newest First":
        docs.sort(key=lambda x: x['upload_date'], reverse=True)
    elif sort_option == "Oldest First":
        docs.sort(key=lambda x: x['upload_date'])
    elif sort_option == "Name A-Z":
        docs.sort(key=lambda x: x['filename'].lower())
    elif sort_option == "Name Z-A":
        docs.sort(key=lambda x: x['filename'].lower(), reverse=True)
    
    return docs

# Add JavaScript for card interactions
st.markdown("""
<script>
function selectDocument(docId) {
    // This would be handled by the Streamlit button clicks
    console.log('Selected document:', docId);
}
</script>
""", unsafe_allow_html=True)
