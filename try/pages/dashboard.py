import streamlit as st
import time
from utils import extract_text_from_file, save_document_to_history, get_file_type_icon

def show():
    """Display the dashboard page"""
    
    # Image slider section
    render_image_slider()
    
    # Main content section
    render_upload_section()

def render_image_slider():
    """Render the horizontal image slider"""
    st.markdown("""
    <div style="margin-bottom: 3rem;">
        <div id="imageSlider" style="
            position: relative;
            width: 100%;
            height: 300px;
            overflow: hidden;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <div class="slider-container" style="
                display: flex;
                width: 300%;
                height: 100%;
                transition: transform 0.5s ease-in-out;
            ">
                <div class="slide" style="
                    width: 33.333%;
                    height: 100%;
                    background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), 
                               url('https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800') center/cover;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 2rem;
                    font-weight: bold;
                ">
                    Legal Document Analysis
                </div>
                <div class="slide" style="
                    width: 33.333%;
                    height: 100%;
                    background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), 
                               url('https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800') center/cover;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 2rem;
                    font-weight: bold;
                ">
                    AI-Powered Insights
                </div>
                <div class="slide" style="
                    width: 33.333%;
                    height: 100%;
                    background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), 
                               url('https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800') center/cover;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 2rem;
                    font-weight: bold;
                ">
                    Smart Contract Review
                </div>
            </div>
            
            <!-- Navigation arrows -->
            <button onclick="previousSlide()" style="
                position: absolute;
                left: 20px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(255,255,255,0.8);
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                cursor: pointer;
                font-size: 1.5rem;
                transition: all 0.3s ease;
            " onmouseover="this.style.background='rgba(255,255,255,1)'" 
               onmouseout="this.style.background='rgba(255,255,255,0.8)'">‹</button>
            
            <button onclick="nextSlide()" style="
                position: absolute;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(255,255,255,0.8);
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                cursor: pointer;
                font-size: 1.5rem;
                transition: all 0.3s ease;
            " onmouseover="this.style.background='rgba(255,255,255,1)'" 
               onmouseout="this.style.background='rgba(255,255,255,0.8)'">›</button>
        </div>
    </div>
    
    <script>
    let currentSlide = 0;
    const totalSlides = 3;
    
    function showSlide(n) {
        const slider = document.querySelector('.slider-container');
        if (slider) {
            slider.style.transform = `translateX(-${n * 33.333}%)`;
        }
    }
    
    function nextSlide() {
        currentSlide = (currentSlide + 1) % totalSlides;
        showSlide(currentSlide);
    }
    
    function previousSlide() {
        currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
        showSlide(currentSlide);
    }
    
    // Auto-advance slides
    setInterval(nextSlide, 5000);
    </script>
    """, unsafe_allow_html=True)

def render_upload_section():
    """Render the file upload section"""
    st.markdown("""
    <div class="card" style="text-align: center; min-height: 500px; display: flex; flex-direction: column; justify-content: center; position: relative;">
        <div style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 60px; height: 4px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 2px;"></div>
        <div style="margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">📁</div>
            <h2 style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1rem; font-weight: 700; font-size: 2.2rem;">Upload Document</h2>
            <p style="color: #6B7280; margin-bottom: 2rem; font-size: 1.1rem; line-height: 1.6;">
                Transform your legal documents with AI-powered analysis<br>
                <span style="font-size: 0.9rem; opacity: 0.8;">Supports PDF, DOCX, and TXT formats</span>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    # File type icons with enhanced hover effects
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 1.5rem; margin: 2.5rem 0;">
        <div style="text-align: center; padding: 1.5rem; border-radius: 16px; background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05)); border: 2px solid rgba(239, 68, 68, 0.2); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;"
             onmouseover="this.style.transform='translateY(-5px) scale(1.05)'; this.style.boxShadow='0 20px 40px rgba(239, 68, 68, 0.2)'"
             onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='none'">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📄</div>
            <div style="color: #EF4444; font-weight: 600; font-size: 0.9rem;">PDF</div>
        </div>
        <div style="text-align: center; padding: 1.5rem; border-radius: 16px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05)); border: 2px solid rgba(59, 130, 246, 0.2); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;"
             onmouseover="this.style.transform='translateY(-5px) scale(1.05)'; this.style.boxShadow='0 20px 40px rgba(59, 130, 246, 0.2)'"
             onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='none'">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📝</div>
            <div style="color: #3B82F6; font-weight: 600; font-size: 0.9rem;">DOCX</div>
        </div>
        <div style="text-align: center; padding: 1.5rem; border-radius: 16px; background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(34, 197, 94, 0.05)); border: 2px solid rgba(34, 197, 94, 0.2); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;"
             onmouseover="this.style.transform='translateY(-5px) scale(1.05)'; this.style.boxShadow='0 20px 40px rgba(34, 197, 94, 0.2)'"
             onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='none'">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📋</div>
            <div style="color: #22C55E; font-weight: 600; font-size: 0.9rem;">TXT</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
                
                # Show analyze button
                if st.button("🔍 Analyze Document", key="analyze_btn"):
                    st.session_state.current_page = "Analysis"
                    st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)


