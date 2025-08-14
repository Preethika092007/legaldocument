import streamlit as st
import requests
import json
import os
import io
import base64
from datetime import datetime
import pdfplumber
from docx import Document
import time

# Hugging Face API configuration
HF_API_KEY = "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"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# Model URLs - Using Hugging Face Audio Course recommended models
MODEL_URLS = {
    "summarization": "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
    "tts": "https://api-inference.huggingface.co/models/microsoft/speecht5_tts",
    "tts_alternative": "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits",
    "tts_bark": "https://api-inference.huggingface.co/models/suno/bark",
    "tts_fastspeech": "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech",
    "chatbot": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
    "granite": "https://api-inference.huggingface.co/models/ibm-granite/granite-3.0-8b-instruct",
    "detailed_analysis": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
}

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file based on file type"""
    try:
        file_type = uploaded_file.type
        
        if file_type == "application/pdf":
            return extract_text_from_pdf(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_docx(uploaded_file)
        elif file_type == "text/plain":
            return extract_text_from_txt(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload PDF, DOCX, or TXT files.")
            return None
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return None

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF file"""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX file"""
    doc = Document(uploaded_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(uploaded_file):
    """Extract text from TXT file"""
    return str(uploaded_file.read(), "utf-8")

def query_huggingface_api(url, payload, max_retries=3):
    """Query Hugging Face API with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=HF_HEADERS, json=payload, timeout=30)

            if response.status_code == 503:
                # Model is loading, wait and retry
                st.info(f"Model is loading, please wait... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(15)
                continue
            elif response.status_code == 404:
                st.error(f"Model not found (404). Please check the model URL: {url}")
                return None
            elif response.status_code == 401:
                st.error("Authentication failed. Please check your Hugging Face API key.")
                return None
            elif response.status_code == 200:
                return response.json()
            else:
                st.warning(f"API returned status {response.status_code}. Retrying...")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                else:
                    st.error(f"API Error after {max_retries} attempts: {response.status_code}")
                    return None
        except requests.exceptions.Timeout:
            st.warning(f"Request timeout (Attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                st.error("Request timed out after multiple attempts")
                return None
        except Exception as e:
            st.warning(f"Request failed: {str(e)} (Attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                st.error(f"Request failed after {max_retries} attempts")
                return None
    return None

def generate_summary(text, max_length=150):
    """Generate summary using Facebook BART CNN model"""
    payload = {
        "inputs": text[:1000],  # Limit input length for BART
        "parameters": {
            "max_length": max_length,
            "min_length": 30,
            "do_sample": False
        }
    }

    result = query_huggingface_api(MODEL_URLS["summarization"], payload)
    if result and isinstance(result, list) and len(result) > 0:
        return result[0].get("summary_text", result[0].get("generated_text", "AI-generated summary not available"))

    # Enhanced fallback: Create a more detailed extractive summary
    sentences = text.split('. ')[:5]
    fallback_summary = '. '.join(sentences) + '.' if sentences else "Document uploaded successfully. Summary generation temporarily unavailable."
    return fallback_summary

def generate_detailed_summary(text):
    """Generate detailed document analysis with bullet points"""
    import re

    # Extract key information
    dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', text)
    monetary_values = re.findall(r'\$[\d,]+\.?\d*|\b\d+\s*(?:dollars?|USD|cents?)\b', text, re.IGNORECASE)

    # Create detailed summary structure
    detailed_info = {
        "key_points": [],
        "important_dates": dates[:5] if dates else ["No specific dates found"],
        "monetary_values": monetary_values[:5] if monetary_values else ["No monetary values found"],
        "document_length": f"{len(text.split())} words, {len(text.split('.'))} sentences"
    }

    # Extract key sentences (first and last few sentences of each paragraph)
    paragraphs = [p.strip() for p in text.split('\n') if p.strip() and len(p.strip()) > 50]

    for i, paragraph in enumerate(paragraphs[:3]):  # Analyze first 3 paragraphs
        sentences = paragraph.split('.')
        if sentences:
            key_sentence = sentences[0].strip()
            if len(key_sentence) > 20:
                detailed_info["key_points"].append(f"• {key_sentence}")

    # Format the detailed summary
    summary_parts = [
        "**📋 Document Overview:**",
        f"• Document contains {detailed_info['document_length']}",
        "",
        "**🔑 Key Points:**"
    ]

    summary_parts.extend(detailed_info["key_points"][:5])

    summary_parts.extend([
        "",
        "**📅 Important Dates:**"
    ])

    for date in detailed_info["important_dates"]:
        summary_parts.append(f"• {date}")

    summary_parts.extend([
        "",
        "**💰 Financial Information:**"
    ])

    for value in detailed_info["monetary_values"]:
        summary_parts.append(f"• {value}")

    return "\n".join(summary_parts)

def classify_document_type(text):
    """Enhanced document type classification using IBM Granite model with fallback"""
    # Try IBM Granite model first
    try:
        prompt = f"""Analyze the following legal document and classify its type. Choose from these categories:
- Legal Contract
- Insurance Policy
- Lease Agreement
- Employment Document
- Legal Will
- Non-Disclosure Agreement
- Service Agreement
- Purchase Agreement
- Partnership Agreement
- License Agreement
- Court Document
- Legal Notice
- Terms & Conditions
- General Legal Document

Document text: {text[:800]}

Classification:"""

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 50,
                "temperature": 0.1,
                "do_sample": False
            }
        }

        result = query_huggingface_api(MODEL_URLS["granite"], payload)
        if result and isinstance(result, list) and len(result) > 0:
            classification = result[0].get("generated_text", "").replace(prompt, "").strip()
            if classification and len(classification) < 100:
                return f"{classification} (IBM Granite AI Classification)"
    except Exception as e:
        st.info(f"IBM Granite classification failed, using fallback: {str(e)[:50]}")

    # Fallback to keyword-based classification
    text_lower = text.lower()

    classifications = {
        "Legal Contract": ["contract", "agreement", "party", "whereas", "hereby", "covenant", "obligations"],
        "Insurance Policy": ["policy", "coverage", "premium", "deductible", "claim", "insured", "beneficiary"],
        "Lease Agreement": ["lease", "rent", "tenant", "landlord", "premises", "rental", "occupancy"],
        "Employment Document": ["employment", "employee", "employer", "salary", "compensation", "benefits", "termination"],
        "Legal Will": ["will", "testament", "beneficiary", "estate", "inheritance", "executor", "bequest"],
        "Non-Disclosure Agreement": ["confidential", "nda", "proprietary", "disclosure", "confidentiality"],
        "Service Agreement": ["services", "provider", "client", "deliverables", "scope", "performance"],
        "Purchase Agreement": ["purchase", "sale", "buyer", "seller", "goods", "merchandise", "delivery"],
        "Partnership Agreement": ["partnership", "partner", "joint", "venture", "collaboration", "profit sharing"],
        "License Agreement": ["license", "licensing", "intellectual property", "rights", "usage", "royalty"],
        "Court Document": ["court", "judge", "plaintiff", "defendant", "lawsuit", "hearing", "verdict"],
        "Legal Notice": ["notice", "notification", "inform", "hereby notify", "warning", "demand"],
        "Terms & Conditions": ["terms", "conditions", "service", "privacy", "user agreement", "acceptable use"]
    }

    scores = {}
    for doc_type, keywords in classifications.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            scores[doc_type] = score

    if scores:
        best_match = max(scores, key=scores.get)
        confidence = scores[best_match]
        return f"{best_match} (Keyword-based: {confidence} matches)"
    else:
        return "General Legal Document (No specific type identified)"

def extract_named_entities(text):
    """Enhanced named entity extraction with detailed categorization"""
    import re

    entities = {
        'dates': [],
        'monetary': [],
        'organizations': [],
        'persons': [],
        'locations': [],
        'legal_terms': [],
        'contact_info': [],
        'obligations': []
    }

    # Enhanced date extraction
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
    ]

    for pattern in date_patterns:
        entities['dates'].extend(re.findall(pattern, text, re.IGNORECASE))

    # Enhanced monetary value extraction
    money_patterns = [
        r'\$[\d,]+\.?\d*',
        r'\b\d+\s*(?:dollars?|USD|cents?|EUR|GBP)\b',
        r'\b(?:USD|EUR|GBP)\s*[\d,]+\.?\d*\b'
    ]

    for pattern in money_patterns:
        entities['monetary'].extend(re.findall(pattern, text, re.IGNORECASE))

    # Enhanced organization detection
    org_patterns = [
        r'\b\w+(?:\s+\w+)*\s+(?:Inc\.?|LLC|Corp\.?|Company|Corporation|Ltd\.?|LLP|LP)\b',
        r'\b(?:The\s+)?\w+(?:\s+\w+)*\s+(?:Bank|Insurance|Group|Holdings|Enterprises)\b'
    ]

    for pattern in org_patterns:
        entities['organizations'].extend(re.findall(pattern, text, re.IGNORECASE))

    # Location extraction
    location_patterns = [
        r'\b\w+,\s*[A-Z]{2}\b',  # City, State
        r'\b\d+\s+\w+(?:\s+\w+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)\b'
    ]

    for pattern in location_patterns:
        entities['locations'].extend(re.findall(pattern, text, re.IGNORECASE))

    # Legal terms extraction
    legal_terms = [
        'whereas', 'hereby', 'covenant', 'indemnify', 'liability', 'breach', 'termination',
        'confidential', 'proprietary', 'intellectual property', 'force majeure', 'arbitration'
    ]

    for term in legal_terms:
        if term.lower() in text.lower():
            entities['legal_terms'].append(term.title())

    # Contact information
    contact_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
        r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b'  # Phone with area code
    ]

    for pattern in contact_patterns:
        entities['contact_info'].extend(re.findall(pattern, text))

    # Obligations and requirements
    obligation_patterns = [
        r'(?:shall|must|required to|obligated to|responsible for)\s+[^.]{10,100}',
        r'(?:agrees to|undertakes to|commits to)\s+[^.]{10,100}'
    ]

    for pattern in obligation_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities['obligations'].extend([match.strip() for match in matches])

    # Person name detection (improved)
    person_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
    potential_persons = re.findall(person_pattern, text)

    # Filter out common legal terms and organizations
    exclude_terms = [
        'Legal Notice', 'Terms Conditions', 'Privacy Policy', 'User Agreement',
        'United States', 'New York', 'Los Angeles', 'San Francisco'
    ]
    entities['persons'] = [name for name in potential_persons if name not in exclude_terms]

    # Remove duplicates and limit results
    for key in entities:
        entities[key] = list(set(entities[key]))[:10]  # Limit to 10 items per category

    return entities

def simplify_clauses(text):
    """Simplify legal clauses using Granite model"""
    payload = {
        "inputs": f"Simplify the following legal text into plain English while maintaining the legal meaning: {text[:1000]}",
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.2
        }
    }
    
    result = query_huggingface_api(MODEL_URLS["granite"], payload)
    if result and isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "Clause simplification failed")
    return "Clause simplification failed"

def extract_key_clauses(text):
    """Extract key clauses using keyword analysis"""
    import re

    # Look for common legal clause indicators
    key_phrases = []

    # Find sentences with key legal terms
    sentences = text.split('.')

    for sentence in sentences[:20]:  # Check first 20 sentences
        sentence = sentence.strip()
        if len(sentence) > 20:  # Ignore very short sentences
            if any(keyword in sentence.lower() for keyword in [
                'shall', 'must', 'required', 'obligation', 'responsible',
                'agree', 'covenant', 'warrant', 'represent', 'undertake',
                'payment', 'fee', 'compensation', 'penalty', 'damages',
                'termination', 'breach', 'default', 'violation'
            ]):
                key_phrases.append(sentence.strip())

    if key_phrases:
        return "Key clauses identified: " + " | ".join(key_phrases[:5])
    else:
        return "Document contains standard legal language with obligations, agreements, and terms requiring review by legal counsel."

def chatbot_response(question, context):
    """Generate chatbot response using simple keyword matching"""
    question_lower = question.lower()
    context_lower = context.lower()

    # Simple keyword-based responses
    if any(word in question_lower for word in ['summary', 'summarize', 'what is', 'about']):
        sentences = context.split('.')[:3]
        return f"Based on the document: {'. '.join(sentences)}."

    elif any(word in question_lower for word in ['date', 'when', 'time']):
        import re
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', context)
        if dates:
            return f"I found these dates in the document: {', '.join(dates[:3])}"
        else:
            return "I couldn't find specific dates in the document."

    elif any(word in question_lower for word in ['money', 'cost', 'price', 'fee', 'payment']):
        import re
        money = re.findall(r'\$[\d,]+\.?\d*|\b\d+\s*dollars?\b', context, re.IGNORECASE)
        if money:
            return f"I found these monetary amounts: {', '.join(money[:3])}"
        else:
            return "I couldn't find specific monetary amounts in the document."

    elif any(word in question_lower for word in ['who', 'party', 'parties', 'person']):
        return "The document appears to involve multiple parties. Please review the document for specific names and roles."

    else:
        # Try to find relevant sentences containing keywords from the question
        words = question_lower.split()
        relevant_sentences = []
        for sentence in context.split('.'):
            if any(word in sentence.lower() for word in words if len(word) > 3):
                relevant_sentences.append(sentence.strip())

        if relevant_sentences:
            return f"Based on your question, here's what I found: {relevant_sentences[0]}"
        else:
            return "I understand your question, but I need more specific information to provide a detailed answer. Could you please rephrase or ask about specific terms in the document?"

def text_to_speech(text):
    """Convert text to speech using multiple approaches for maximum reliability"""
    # Clean and prepare text for TTS
    clean_text = text.replace("**", "").replace("•", "").replace("*", "")
    clean_text = clean_text.replace("\n", " ").replace("\r", " ")

    # Remove all emojis and special characters
    import re
    clean_text = re.sub(r'[^\w\s.,!?-]', '', clean_text)
    clean_text = " ".join(clean_text.split())
    clean_text = clean_text[:150]  # Keep it shorter for better success rate

    if not clean_text.strip():
        st.warning("No text available for audio conversion.")
        return None

    st.info(f"🎙️ Converting to speech: '{clean_text[:50]}...'")

    # Try the most reliable TTS approach first
    return try_simple_tts(clean_text)

def try_simple_tts(text):
    """Try a simple, reliable TTS approach"""
    try:
        # First, let's try without authentication to see if that's the issue
        payload = {"inputs": text}

        st.info("🔄 Trying TTS without authentication...")
        response = requests.post(
            "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits",
            json=payload,
            timeout=30
        )

        st.info(f"Response status: {response.status_code}")
        st.info(f"Response content length: {len(response.content)}")

        if response.status_code == 200 and len(response.content) > 100:
            audio_base64 = base64.b64encode(response.content).decode()
            st.success("✅ Audio generated successfully (no auth)!")
            return audio_base64

        # If that fails, try with authentication
        st.info("🔄 Trying with authentication...")
        headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

        response = requests.post(
            "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits",
            headers=headers,
            json=payload,
            timeout=30
        )

        st.info(f"Auth response status: {response.status_code}")
        st.info(f"Auth response content length: {len(response.content)}")

        if response.status_code == 200:
            if len(response.content) > 100:
                audio_base64 = base64.b64encode(response.content).decode()
                st.success("✅ Audio generated successfully (with auth)!")
                return audio_base64
            else:
                st.warning(f"⚠️ Received small response: {len(response.content)} bytes")

        elif response.status_code == 503:
            st.info("🔄 Model is loading, trying alternative approach...")
            return try_alternative_simple_tts(text)

        elif response.status_code == 401:
            st.error("❌ Authentication failed. API key may be invalid.")
            return create_simple_audio_file(text)

        elif response.status_code == 404:
            st.warning("❌ Model not found, trying alternative...")
            return try_alternative_simple_tts(text)

        else:
            st.warning(f"⚠️ Unexpected status {response.status_code}")
            if len(response.text) < 200:
                st.text(f"Response: {response.text}")
            return try_alternative_simple_tts(text)

    except Exception as e:
        st.error(f"❌ TTS error: {str(e)}")
        return create_simple_audio_file(text)

def try_alternative_simple_tts(text):
    """Try alternative TTS models with simple approach"""
    alternative_models = [
        "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech",
        "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"
    ]

    for model_url in alternative_models:
        try:
            st.info(f"🔄 Trying alternative model: {model_url.split('/')[-1]}")

            payload = {"inputs": text}
            response = requests.post(
                model_url,
                headers={"Authorization": f"Bearer {HF_API_KEY}"},
                json=payload,
                timeout=30
            )

            if response.status_code == 200 and len(response.content) > 100:
                audio_base64 = base64.b64encode(response.content).decode()
                st.success(f"✅ Audio generated with alternative model!")
                return audio_base64

        except Exception as e:
            st.warning(f"Alternative model failed: {str(e)[:50]}")
            continue

    return create_browser_tts_fallback(text)

def create_simple_audio_file(text):
    """Create a simple audio file using basic synthesis"""
    try:
        import io
        import wave
        import struct
        import math

        st.info("🔧 Creating simple audio file...")

        # Simple beep pattern to indicate TTS attempt
        sample_rate = 22050
        duration = 2.0  # 2 seconds
        frequency = 440  # A4 note

        # Generate a simple tone
        samples = []
        for i in range(int(sample_rate * duration)):
            t = float(i) / sample_rate
            # Create a simple tone that fades in and out
            amplitude = 0.3 * math.sin(2 * math.pi * frequency * t) * math.exp(-t)
            samples.append(int(amplitude * 32767))

        # Create WAV file in memory
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)

            # Write samples
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))

        # Get the audio data
        buffer.seek(0)
        audio_data = buffer.read()
        audio_base64 = base64.b64encode(audio_data).decode()

        st.info("🔔 Created notification tone (TTS models unavailable)")
        return audio_base64

    except Exception as e:
        st.error(f"❌ Could not create audio file: {str(e)}")
        return create_browser_tts_fallback(text)

def create_browser_tts_fallback(text):
    """Create a browser-based TTS fallback"""
    st.info("🗣️ Creating browser-based speech fallback...")

    # Store the text for browser TTS
    if 'tts_fallback_text' not in st.session_state:
        st.session_state.tts_fallback_text = text

    st.markdown(f"""
    <div style="
        background: #E3F2FD;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    ">
        <strong>🎵 TTS Alternative Available</strong><br>
        AI models are currently unavailable, but you can use browser speech below.
    </div>
    """, unsafe_allow_html=True)

    return None

def test_tts_connection():
    """Test TTS connection and API key"""
    try:
        test_text = "Hello, this is a test."
        payload = {"inputs": test_text}

        response = requests.post(
            "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json=payload,
            timeout=10
        )

        return {
            "status_code": response.status_code,
            "content_length": len(response.content),
            "headers": dict(response.headers),
            "success": response.status_code == 200 and len(response.content) > 100
        }

    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def test_granite_model():
    """Test IBM Granite model connection"""
    try:
        test_prompt = "Classify this document: This is a rental agreement between landlord and tenant."
        payload = {
            "inputs": test_prompt,
            "parameters": {
                "max_new_tokens": 20,
                "temperature": 0.1
            }
        }

        response = requests.post(
            MODEL_URLS["granite"],
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json=payload,
            timeout=30
        )

        return {
            "status_code": response.status_code,
            "content_length": len(response.content),
            "response_text": response.text[:200] if response.text else "No response text",
            "success": response.status_code == 200
        }

    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def save_document_to_history(filename, file_type, text):
    """Save document to history"""
    document_entry = {
        "filename": filename,
        "file_type": file_type,
        "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text,
        "id": len(st.session_state.document_history)
    }
    
    st.session_state.document_history.append(document_entry)
    return document_entry

def get_file_type_icon(file_type):
    """Get appropriate icon for file type"""
    if "pdf" in file_type.lower():
        return "📄"
    elif "word" in file_type.lower() or "docx" in file_type.lower():
        return "📝"
    elif "text" in file_type.lower():
        return "📋"
    else:
        return "📁"

def highlight_entities_in_text(text, entities):
    """Highlight named entities in text"""
    # This is a simplified version - in a real app, you'd use more sophisticated NLP
    highlighted_text = text
    
    # Simple highlighting based on common patterns
    import re
    
    # Highlight dates (simple pattern)
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
    highlighted_text = re.sub(date_pattern, r'<span style="background-color: #90EE90;">\g<0></span>', highlighted_text)
    
    # Highlight monetary values
    money_pattern = r'\$[\d,]+\.?\d*|\b\d+\s*dollars?\b'
    highlighted_text = re.sub(money_pattern, r'<span style="background-color: #FFB6C1;">\g<0></span>', highlighted_text)
    
    # Highlight obligations (simple keywords)
    obligation_keywords = ['shall', 'must', 'required', 'obligation', 'duty', 'responsible']
    for keyword in obligation_keywords:
        pattern = r'\b' + keyword + r'\b'
        highlighted_text = re.sub(pattern, r'<span style="background-color: #FFFF99;">\g<0></span>', highlighted_text, flags=re.IGNORECASE)
    
    return highlighted_text
