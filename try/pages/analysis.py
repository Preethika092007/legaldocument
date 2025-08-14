import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import base64
from utils import (
    generate_summary, generate_detailed_summary, classify_document_type, extract_named_entities,
    simplify_clauses, extract_key_clauses, chatbot_response, text_to_speech,
    highlight_entities_in_text, test_tts_connection, test_granite_model
)

def show():
    """Display the analysis page"""
    
    # Check if there's a document to analyze
    if not st.session_state.extracted_text:
        render_no_document()
        return
    
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #007BFF; text-align: center; margin-bottom: 1rem;">🔍 Document Analysis</h1>
        <p style="text-align: center; color: #6C757D; font-size: 1.1rem;">
            AI-powered insights and analysis of your legal document
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Top section - Split view
    render_split_view()
    
    # Middle section - Chatbot
    render_chatbot_section()
    
    # Bottom section - Key points and analysis
    render_analysis_section()
    
    # Document summary section
    render_summary_section()

def render_no_document():
    """Render when no document is available for analysis"""
    st.markdown("""
    <div class="card" style="text-align: center; padding: 4rem 2rem;">
        <div style="font-size: 4rem; margin-bottom: 2rem;">📄</div>
        <h3 style="color: #6C757D; margin-bottom: 1rem;">No Document Selected</h3>
        <p style="color: #6C757D; margin-bottom: 2rem;">
            Please upload a document first to start the analysis
        </p>
    """, unsafe_allow_html=True)
    
    if st.button("📁 Upload Document", key="upload_from_analysis"):
        st.info("📍 Use the navigation menu to go to Dashboard page.")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_split_view():
    """Render the split view with document preview and voice-over panel"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_document_preview()
    
    with col2:
        render_voice_panel()

def render_document_preview():
    """Render scrollable document preview with highlights"""
    st.markdown("""
    <div class="card">
        <h3 style="color: #007BFF; margin-bottom: 1rem;">📖 Document Preview</h3>
        <div style="margin-bottom: 1rem;">
            <small style="color: #6C757D;">
                🟡 Obligations | 🟢 Dates | 🔴 Monetary Values
            </small>
        </div>
    """, unsafe_allow_html=True)
    
    # Get highlighted text
    if 'highlighted_text' not in st.session_state:
        with st.spinner("Analyzing document for entities..."):
            entities = extract_named_entities(st.session_state.extracted_text)
            st.session_state.highlighted_text = highlight_entities_in_text(
                st.session_state.extracted_text, entities
            )
    
    # Display highlighted text in scrollable container
    st.markdown(f"""
    <div style="
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: #F8F9FA;
        border-radius: 8px;
        border: 1px solid #E9ECEF;
        line-height: 1.6;
        font-size: 0.9rem;
    ">
        {st.session_state.highlighted_text}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_voice_panel():
    """Render voice-over panel with summary and TTS"""
    st.markdown("""
    <div class="card">
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            <div style="font-size: 2rem; margin-right: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">🔊</div>
            <h3 style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; font-weight: 700;">Voice Summary</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Generate enhanced summary if not already done
    if 'document_summary' not in st.session_state:
        with st.spinner("Generating enhanced summary with SmolDocling..."):
            st.session_state.document_summary = generate_summary(st.session_state.extracted_text, max_length=200)
    
    # Display summary
    st.markdown(f"""
    <div style="
        background: #F8F9FA;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #20C997;
    ">
        {st.session_state.document_summary}
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced TTS controls with debugging
    st.markdown("### 🎵 Audio Generation Options")
    st.markdown("*Using models from [Hugging Face Audio Course Chapter 6](https://huggingface.co/learn/audio-course/chapter6/pre-trained_models)*")

    # Add model testing section
    with st.expander("🔧 Model Testing & Debugging", expanded=False):
        col_test1, col_test2, col_test3 = st.columns(3)

        with col_test1:
            if st.button("🧪 Test TTS Connection", key="test_tts"):
                with st.spinner("Testing TTS connection..."):
                    test_result = test_tts_connection()

                    if test_result.get("success"):
                        st.success("✅ TTS connection working!")
                        st.json(test_result)
                    else:
                        st.error("❌ TTS connection failed")
                        st.json(test_result)

        with col_test2:
            if st.button("🎵 Test Simple Audio", key="test_simple_audio"):
                with st.spinner("Testing simple audio generation..."):
                    test_audio = text_to_speech("Hello, this is a test of the text to speech system.")
                    if test_audio:
                        st.success("✅ Test audio generated!")
                        st.markdown(f"""
                        <audio controls style="width: 100%;">
                            <source src="data:audio/wav;base64,{test_audio}" type="audio/wav">
                        </audio>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Test audio failed")

        with col_test3:
            if st.button("🧠 Test IBM Granite", key="test_granite"):
                with st.spinner("Testing IBM Granite model..."):
                    test_result = test_granite_model()

                    if test_result.get("success"):
                        st.success("✅ IBM Granite working!")
                        st.json(test_result)
                    else:
                        st.error("❌ IBM Granite failed")
                        st.json(test_result)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🤖 AI-Generated Audio (HF Audio Course Models)**")
        st.markdown("*Models: SpeechT5, VITS, Bark, FastSpeech2*")

        if st.button("🎵 Generate High-Quality Audio", key="generate_tts", help="Uses Hugging Face Audio Course recommended TTS models"):
            summary_text = st.session_state.document_summary

            # Show preview of text that will be converted
            with st.expander("📝 Text to be converted to audio", expanded=False):
                st.text_area("Summary content:", summary_text, height=100, disabled=True)

            st.info(f"🎙️ Converting summary to speech using HF Audio Course models...")

            audio_data = text_to_speech(summary_text)
            if audio_data:
                st.session_state.audio_data = audio_data
                st.balloons()
                st.success("🎉 Audio generated! Play it below.")

    with col2:
        st.markdown("**🗣️ Instant Browser Speech**")
        if st.button("🗣️ Speak Now", key="browser_tts", help="Instant speech using your browser"):
            summary_text = st.session_state.document_summary
            clean_text = summary_text.replace("**", "").replace("•", "").replace("*", "")
            clean_text = clean_text.replace("\n", " ").strip()

            # Create a unique ID for this speech instance
            import time
            speech_id = int(time.time() * 1000)

            st.markdown(f"""
            <div id="speech-{speech_id}">
                <script>
                (function() {{
                    const text = `{clean_text[:400]}`;
                    if ('speechSynthesis' in window) {{
                        // Stop any ongoing speech
                        speechSynthesis.cancel();

                        const utterance = new SpeechSynthesisUtterance(text);
                        utterance.rate = 0.9;
                        utterance.pitch = 1.0;
                        utterance.volume = 1.0;

                        utterance.onstart = function() {{
                            console.log('Speech started');
                        }};

                        utterance.onend = function() {{
                            console.log('Speech ended');
                        }};

                        speechSynthesis.speak(utterance);
                    }} else {{
                        alert('Speech synthesis not supported in your browser');
                    }}
                }})();
                </script>
            </div>
            """, unsafe_allow_html=True)

            st.success("🗣️ Speaking now! Adjust your volume if needed.")

    # Audio player section
    st.markdown("---")
    st.markdown("### 🎧 Audio Player")

    if True:  # Always show this section
        if 'audio_data' in st.session_state:
            st.markdown("""
            <div style="
                padding: 1.5rem;
                background: linear-gradient(135deg, #E3F2FD, #F3E5F5);
                border-radius: 15px;
                border: 2px solid #007BFF;
                box-shadow: 0 4px 15px rgba(0, 123, 255, 0.2);
            ">
                <div style="
                    margin-bottom: 1rem;
                    font-weight: 700;
                    color: #007BFF;
                    font-size: 1.1rem;
                    text-align: center;
                ">🎧 Document Summary Audio</div>
                <div style="
                    margin-bottom: 0.5rem;
                    font-size: 0.9rem;
                    color: #6C757D;
                    text-align: center;
                ">Click play to listen to your document summary</div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <audio controls style="
                width: 100%;
                border-radius: 8px;
                margin-top: 0.5rem;
                outline: none;
            " preload="auto">
                <source src="data:audio/wav;base64,{st.session_state.audio_data}" type="audio/wav">
                <source src="data:audio/mpeg;base64,{st.session_state.audio_data}" type="audio/mpeg">
                <source src="data:audio/ogg;base64,{st.session_state.audio_data}" type="audio/ogg">
                Your browser does not support the audio element.
            </audio>
            </div>
            """, unsafe_allow_html=True)

            # Add download option
            st.download_button(
                label="📥 Download Audio",
                data=base64.b64decode(st.session_state.audio_data),
                file_name="document_summary_audio.wav",
                mime="audio/wav",
                help="Download the audio file to your device"
            )
        else:
            st.markdown("""
            <div style="
                padding: 1.5rem;
                background: #F8F9FA;
                border-radius: 15px;
                border: 2px dashed #6C757D;
                text-align: center;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎵</div>
                <div style="color: #6C757D; font-weight: 500;">
                    Click "Generate Audio" to create<br>
                    speech from your document summary
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_chatbot_section():
    """Render the chatbot Q&A section"""
    st.markdown("""
    <div class="card">
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            <div style="font-size: 2rem; margin-right: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">🤖</div>
            <h3 style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; font-weight: 700;">AI Document Assistant</h3>
        </div>
        <p style="color: #6B7280; margin-bottom: 1.5rem; font-size: 1rem;">Ask questions about your document and get instant AI-powered answers</p>
    """, unsafe_allow_html=True)
    
    # Display chat history
    if st.session_state.chat_history:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.markdown(f"""
                <div style="
                    text-align: right;
                    margin: 1rem 0;
                ">
                    <div style="
                        display: inline-block;
                        background: #E9ECEF;
                        padding: 0.75rem 1rem;
                        border-radius: 18px 18px 4px 18px;
                        max-width: 70%;
                        color: #333333;
                    ">
                        {message['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    text-align: left;
                    margin: 1rem 0;
                ">
                    <div style="
                        display: inline-block;
                        background: linear-gradient(135deg, #007BFF, #20C997);
                        color: white;
                        padding: 0.75rem 1rem;
                        border-radius: 18px 18px 18px 4px;
                        max-width: 70%;
                    ">
                        {message['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_question = st.text_input(
            "Ask a question about your document...",
            key="chat_input",
            placeholder="e.g., What are the key obligations in this contract?"
        )
    
    with col2:
        send_button = st.button("Send", key="send_chat")
    
    if send_button and user_question:
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

    
    st.markdown("</div>", unsafe_allow_html=True)

def render_analysis_section():
    """Render key points and analysis with charts"""
    st.markdown("""
    <div class="card">
        <h3 style="color: #007BFF; margin-bottom: 1rem;">📊 Key Analysis & Insights</h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Generate enhanced analysis if not done
        if 'document_analysis' not in st.session_state:
            with st.spinner("Performing detailed document analysis..."):
                st.session_state.document_analysis = {
                    'document_type': classify_document_type(st.session_state.extracted_text),
                    'key_clauses': extract_key_clauses(st.session_state.extracted_text),
                    'entities': extract_named_entities(st.session_state.extracted_text)
                }
        
        analysis = st.session_state.document_analysis
        
        # Document type
        st.markdown(f"""
        <div style="
            background: #E3F2FD;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid #007BFF;
        ">
            <strong>📋 Document Type:</strong><br>
            {analysis['document_type']}
        </div>
        """, unsafe_allow_html=True)
        
        # Key clauses
        st.markdown(f"""
        <div style="
            background: #E8F5E8;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid #20C997;
        ">
            <strong>🔑 Key Clauses:</strong><br>
            {analysis['key_clauses']}
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Named entities display
        st.markdown("**🏷️ Named Entities & Details:**")

        entities = analysis['entities']
        if isinstance(entities, dict):
            # Create expandable sections for different entity types
            with st.expander("📅 Important Dates", expanded=True):
                if entities.get('dates'):
                    for date in entities['dates'][:5]:
                        st.markdown(f"• {date}")
                else:
                    st.info("No specific dates found")

            with st.expander("💰 Financial Information"):
                if entities.get('monetary'):
                    for money in entities['monetary'][:5]:
                        st.markdown(f"• {money}")
                else:
                    st.info("No monetary values found")

            with st.expander("🏢 Organizations"):
                if entities.get('organizations'):
                    for org in entities['organizations'][:5]:
                        st.markdown(f"• {org}")
                else:
                    st.info("No organizations found")

            with st.expander("👤 Persons"):
                if entities.get('persons'):
                    for person in entities['persons'][:5]:
                        st.markdown(f"• {person}")
                else:
                    st.info("No person names found")

            with st.expander("📍 Locations"):
                if entities.get('locations'):
                    for location in entities['locations'][:5]:
                        st.markdown(f"• {location}")
                else:
                    st.info("No locations found")

            with st.expander("⚖️ Legal Terms"):
                if entities.get('legal_terms'):
                    for term in entities['legal_terms'][:5]:
                        st.markdown(f"• {term}")
                else:
                    st.info("No specific legal terms found")
        else:
            # Fallback for string format
            st.markdown(f"""
            <div style="
                background: #FFF3E0;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                border-left: 4px solid #FFC107;
            ">
                {entities}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Create a simple analysis chart
        render_analysis_chart()
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_analysis_chart():
    """Render analysis visualization chart"""
    # Sample data for demonstration
    categories = ['Obligations', 'Dates', 'Monetary', 'Parties', 'Terms']
    values = [15, 8, 5, 3, 12]  # These would be calculated from actual analysis
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=['#007BFF', '#20C997', '#FFC107', '#DC3545', '#6F42C1']
        )
    ])
    
    fig.update_layout(
        title="Document Analysis Overview",
        xaxis_title="Categories",
        yaxis_title="Count",
        height=300,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_summary_section():
    """Render enhanced complete document summary section"""
    st.markdown("""
    <div class="card">
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            <div style="font-size: 2rem; margin-right: 1rem; background: linear-gradient(135deg, #007BFF, #20C997); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">📄</div>
            <h3 style="background: linear-gradient(135deg, #007BFF, #20C997); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; font-weight: 700;">Complete Document Analysis</h3>
        </div>
    """, unsafe_allow_html=True)

    # Generate detailed summary if not done
    if 'detailed_summary' not in st.session_state:
        with st.spinner("Generating detailed analysis with bullet points..."):
            st.session_state.detailed_summary = generate_detailed_summary(st.session_state.extracted_text)

    # Display the detailed summary with better formatting
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #F8F9FA, #FFFFFF);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #E9ECEF;
        max-height: 400px;
        overflow-y: auto;
        line-height: 1.8;
        font-size: 1rem;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
    ">
        {st.session_state.detailed_summary.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

    # Add TTS option for detailed summary
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🎵 Convert Detailed Summary to Audio", key="detailed_tts", help="Convert the detailed summary to speech"):
            with st.spinner("🎙️ Converting detailed summary to speech..."):
                detailed_text = st.session_state.detailed_summary
                audio_data = text_to_speech(detailed_text)
                if audio_data:
                    st.session_state.detailed_audio_data = audio_data
                    st.success("🎉 Detailed summary audio generated!")
                else:
                    st.warning("🎵 TTS service is temporarily unavailable.")

    with col2:
        if 'detailed_audio_data' in st.session_state:
            st.markdown(f"""
            <div style="text-align: center; margin-top: 1rem;">
                <div style="margin-bottom: 0.5rem; font-weight: 600; color: #007BFF;">🎧 Detailed Summary Audio</div>
                <audio controls style="width: 100%;">
                    <source src="data:audio/wav;base64,{st.session_state.detailed_audio_data}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
            </div>
            """, unsafe_allow_html=True)

    # Add document statistics
    col1, col2, col3 = st.columns(3)

    with col1:
        word_count = len(st.session_state.extracted_text.split())
        st.metric("📊 Word Count", f"{word_count:,}")

    with col2:
        char_count = len(st.session_state.extracted_text)
        st.metric("📝 Character Count", f"{char_count:,}")

    with col3:
        sentence_count = len([s for s in st.session_state.extracted_text.split('.') if s.strip()])
        st.metric("📋 Sentences", f"{sentence_count:,}")

    st.markdown("</div>", unsafe_allow_html=True)
