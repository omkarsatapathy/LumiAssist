import PyPDF2
import requests
import re
import uuid
import sqlite3
from datetime import datetime
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field

class RAGSearchInput(BaseModel):
    query: str = Field(description="Search query for FAQ")

class ComplaintInput(BaseModel):
    complaint_data: str = Field(description="Complete complaint information including name, phone, email, and details")

class ComplaintRetrievalInput(BaseModel):
    complaint_id: str = Field(description="Complaint ID to retrieve")

# Initialize database
def init_db():
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            email TEXT NOT NULL,
            complaint_details TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@tool("rag_faq_search", args_schema=RAGSearchInput, return_direct=False)
def rag_faq_search(query: str) -> str:
    """Search Apple Laptop FAQ for relevant information"""
    try:
        # PDF path - update this to your FAQ PDF location
        pdf_path = '/Users/omkarsatapaphy/Downloads/Apple Laptop FAQ.pdf'
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            content = ""
            
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        
        # Search for relevant content
        query_words = query.lower().split()
        paragraphs = content.split('\n\n')
        relevant_content = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) > 50:  # Minimum paragraph length
                score = sum(1 for word in query_words if word in paragraph.lower())
                if score > 0:
                    relevant_content.append((score, paragraph))
        
        # Sort by relevance and return top results
        relevant_content.sort(key=lambda x: x[0], reverse=True)
        
        if relevant_content:
            return "\n\n".join([content[1] for content in relevant_content[:2]])
        else:
            return "No relevant information found in FAQ"
            
    except Exception as e:
        return f"Error accessing FAQ: {str(e)}"

@tool("create_complaint", args_schema=ComplaintInput, return_direct=False)
def create_complaint(complaint_data: str) -> str:
    """Create a new complaint from extracted customer information"""
    try:
        # Extract information from complaint_data
        info = extract_all_info(complaint_data)
        
        # Validate required fields
        required_fields = ['name', 'phone_number', 'email', 'complaint_details']
        missing = [field for field in required_fields if not info.get(field)]
        
        if missing:
            return f"Missing required information: {', '.join(missing)}. Please provide all details."
        
        # Validate email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', info['email']):
            return "Invalid email format provided."
        
        # Validate phone
        phone_clean = re.sub(r'[^\d]', '', info['phone_number'])
        if len(phone_clean) != 10:
            return "Invalid phone number. Must be 10 digits."
        
        # Generate complaint ID
        complaint_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
        
        # Store in database
        init_db()
        conn = sqlite3.connect('complaints.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO complaints (complaint_id, name, phone_number, email, complaint_details)
            VALUES (?, ?, ?, ?, ?)
        ''', (complaint_id, info['name'], phone_clean, info['email'], info['complaint_details']))
        conn.commit()
        conn.close()
        
        return f"Complaint successfully created! Your complaint ID is: {complaint_id}. Please save this ID for future reference."
        
    except Exception as e:
        return f"Error creating complaint: {str(e)}"

@tool("retrieve_complaint", args_schema=ComplaintRetrievalInput, return_direct=False)
def retrieve_complaint(complaint_id: str) -> str:
    """Retrieve complaint details by ID"""
    try:
        init_db()
        conn = sqlite3.connect('complaints.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM complaints WHERE complaint_id = ?', (complaint_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return f"No complaint found with ID: {complaint_id}"
        
        return f"""Complaint Details Found:
ID: {result[0]}
Name: {result[1]}
Phone: {result[2]}
Email: {result[3]}
Issue: {result[4]}
Created: {result[5]}"""
        
    except Exception as e:
        return f"Error retrieving complaint: {str(e)}"

def extract_all_info(text: str) -> dict:
    """Extract all customer information from text"""
    info = {}
    
    # Extract email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        info['email'] = email_match.group()
    
    # Extract phone number
    phone_match = re.search(r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
    if phone_match:
        info['phone_number'] = re.sub(r'[^\d]', '', phone_match.group())
    
    # Extract name (look for capitalized words)
    words = text.split()
    names = []
    for word in words:
        if (word.isalpha() and word[0].isupper() and len(word) > 1 and 
            word.lower() not in ['i', 'my', 'the', 'and', 'complaint', 'issue', 'problem']):
            names.append(word)
    
    if names:
        info['name'] = ' '.join(names[:2])
    
    # Rest as complaint details
    info['complaint_details'] = text
    
    return info

def extract_complaint_id(text: str) -> str:
    """Extract complaint ID from text"""
    match = re.search(r'\b[A-F0-9]{8}\b', text.upper())
    return match.group() if match else None

# List of available tools
available_tools = [rag_faq_search, create_complaint, retrieve_complaint]