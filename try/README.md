<<<<<<< HEAD
# clause
=======
# ClauseWise - AI-Powered Legal Document Analysis

ClauseWise is a comprehensive Streamlit application that provides AI-powered analysis of legal documents using state-of-the-art Hugging Face models.

## Features

### 🔍 **Document Analysis**
- **Document Type Classification**: Automatically identify contract types, agreements, policies, etc.
- **Named Entity Recognition**: Extract persons, organizations, dates, monetary values, and obligations
- **Clause Extraction**: Identify and extract key clauses and terms
- **Clause Simplification**: Convert complex legal language to plain English

### 🤖 **AI-Powered Interactions**
- **Document Summarization**: Generate concise summaries using Google's Flan-T5-Large
- **Interactive Q&A**: Ask questions about your document using Google's Flan-UL2
- **Text-to-Speech**: Listen to document summaries with Nari Labs TTS

### 📊 **Visual Analytics**
- **Interactive Charts**: Visualize document analysis results
- **Entity Highlighting**: Color-coded highlighting of important entities
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile

### 📚 **Document Management**
- **Upload Support**: PDF, DOCX, and TXT files
- **History Tracking**: Keep track of all analyzed documents
- **Search & Filter**: Find documents quickly with advanced filtering

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd Desktop/genai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Hugging Face API**
   - The application uses the provided Hugging Face API key
   - No additional setup required for API access

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:8501`
   - The application will start with the Dashboard page

## Usage Guide

### 1. Dashboard Page
- **Upload Documents**: Drag and drop or browse for PDF, DOCX, or TXT files
- **File Processing**: Automatic text extraction and processing
- **Quick Navigation**: Access analysis and history from the dashboard

### 2. History Page
- **View Past Documents**: Browse all previously uploaded documents
- **Search & Filter**: Find specific documents by name or type
- **Quick Analysis**: Click any document to re-analyze

### 3. Analysis Page
- **Document Preview**: View your document with highlighted entities
- **Voice Summary**: Listen to AI-generated summaries
- **Interactive Chat**: Ask questions about your document
- **Key Insights**: View classification, entities, and key clauses
- **Visual Analytics**: Charts showing document analysis breakdown

## AI Models Used

| Feature | Model | Purpose |
|---------|-------|---------|
| Summarization | google/flan-t5-large | Generate document summaries |
| Text-to-Speech | nari-labs/Dia-1.6B | Convert summaries to speech |
| Document Q&A | google/flan-ul2 | Answer questions about documents |
| Classification | ibm-granite/granite-3.3-8b-instruct | Classify document types |
| Entity Recognition | ibm-granite/granite-3.3-8b-instruct | Extract named entities |
| Clause Analysis | ibm-granite/granite-3.3-8b-instruct | Simplify and extract clauses |

## File Structure

```
ClauseWise/
├── app.py                 # Main application file
├── utils.py              # Utility functions and API integrations
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── pages/               # Page modules
    ├── __init__.py
    ├── dashboard.py     # Dashboard page
    ├── history.py       # History page
    └── analysis.py      # Analysis page
```

## Technical Details

### Architecture
- **Frontend**: Streamlit with custom HTML/CSS
- **Backend**: Python with Hugging Face API integration
- **State Management**: Streamlit session state
- **File Processing**: pdfplumber, python-docx for text extraction

### Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Flexible Layouts**: Adapts to different screen sizes
- **Touch-Friendly**: Large buttons and touch targets

### Performance
- **Caching**: Efficient caching of API responses
- **Lazy Loading**: Load content as needed
- **Error Handling**: Robust error handling and user feedback

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install --upgrade streamlit
   ```

2. **API Timeouts**
   - The application includes retry logic for API calls
   - Models may take time to load initially

3. **File Upload Issues**
   - Ensure files are in supported formats (PDF, DOCX, TXT)
   - Check file size limits

### Support
For issues or questions, please check the error messages in the application interface.

## License
© 2025 ClauseWise. All rights reserved.

## Contributing
This is a demonstration application showcasing AI-powered document analysis capabilities.
>>>>>>> 15ee641 (First commit)
