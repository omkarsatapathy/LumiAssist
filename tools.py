import PyPDF2
import re
import uuid
import sqlite3
import json
from datetime import datetime
from langchain.tools import tool
from pydantic import BaseModel, Field

class RAGConfig:
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.top_k = 2
        self.pdf_path = '/Users/omkarsatapaphy/Downloads/Apple Laptop FAQ.pdf'
        self.min_paragraph_length = 50

class RAGSearchInput(BaseModel):
    query: str = Field(description="Search query for FAQ")

class ComplaintInput(BaseModel):
    complaint_data: str = Field(description="Complete complaint information including name, phone, email, and details")

class ComplaintRetrievalInput(BaseModel):
    complaint_id: str = Field(description="Complaint ID to retrieve")

rag_config = RAGConfig()

def init_db():
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(complaints)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'complaints' not in [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        cursor.execute('''
            CREATE TABLE complaints (
                complaint_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                email TEXT NOT NULL,
                complaint_details TEXT NOT NULL,
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    elif 'status' not in columns:
        cursor.execute('ALTER TABLE complaints ADD COLUMN status TEXT DEFAULT "created"')
    
    conn.commit()
    conn.close()

@tool("rag_faq_search", args_schema=RAGSearchInput, return_direct=False)
def rag_faq_search(query: str) -> str:
    """Search Apple Laptop FAQ for relevant information"""
    try:
        with open(rag_config.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            content = ""
            
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        
        query_words = query.lower().split()
        paragraphs = content.split('\n\n')
        relevant_content = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) > rag_config.min_paragraph_length: 
                score = sum(1 for word in query_words if word in paragraph.lower())
                if score > 0:
                    relevant_content.append((score, paragraph))
        
        relevant_content.sort(key=lambda x: x[0], reverse=True)
        
        if relevant_content:
            return "\n\n".join([content[1] for content in relevant_content[:rag_config.top_k]])
        else:
            return "No relevant information found in FAQ"
            
    except Exception as e:
        return f"Error accessing FAQ: {str(e)}"

@tool("create_complaint", args_schema=ComplaintInput, return_direct=False)
def create_complaint(complaint_data: str) -> str:
    """Create a new complaint from extracted customer information"""
    try:
        info = extract_all_info(complaint_data)
        
        required_fields = ['name', 'phone_number', 'email', 'complaint_details']
        missing = [field for field in required_fields if not info.get(field)]
        
        if missing:
            return f"Missing required information: {', '.join(missing)}. Please provide all details."
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, info['email']):
            return "Invalid email format provided."
        
        phone_clean = re.sub(r'[^\d]', '', info['phone_number'])
        if len(phone_clean) != 10:
            return "Invalid phone number. Must be 10 digits."
        
        db_data = {
            "name": info['name'],
            "phone_number": phone_clean,
            "email": info['email'],
            "complaint_details": info['complaint_details']
        }
        
        print("\n" + "="*60)
        print("DATABASE INSERT DATA:")
        print("="*60)
        print(json.dumps(db_data, indent=2))
        print("="*60 + "\n")
        
        complaint_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
        
        init_db()
        conn = sqlite3.connect('complaints.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO complaints (complaint_id, name, phone_number, email, complaint_details, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (complaint_id, info['name'], phone_clean, info['email'], info['complaint_details'], 'created'))
        conn.commit()
        conn.close()
        
        print(f"✅ SUCCESS: Complaint {complaint_id} created in database\n")
        
        response_json = {
            "complaint_id": complaint_id,
            "message": "Complaint created successfully",
            "name": info['name'],
            "phone_number": phone_clean,
            "email": info['email'],
            "complaint_details": info['complaint_details']
        }
        
        return f"Complaint successfully created! Your complaint ID is: {complaint_id}.\n\nJSON_START{json.dumps(response_json)}JSON_END"
        
    except Exception as e:
        print(f"ERROR: Failed to create complaint - {str(e)}\n")
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
        
        response_json = {
            "complaint_id": result[0],
            "name": result[1],
            "phone_number": result[2],
            "email": result[3],
            "complaint_details": result[4],
            "status": result[5],
            "created_at": result[6]
        }
        
        return f"""Complaint Details Found:
                ID: {result[0]}
                Name: {result[1]}
                Phone: {result[2]}
                Email: {result[3]}
                Issue: {result[4]}
                Status: {result[5]}
                Created: {result[6]}

                JSON_START{json.dumps(response_json)}JSON_END"""
        
    except Exception as e:
        return f"Error retrieving complaint: {str(e)}"

def extract_all_info(text: str) -> dict:
    info = {}
    
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        info['email'] = email_match.group()
    
    phone_match = re.search(r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
    if phone_match:
        info['phone_number'] = re.sub(r'[^\d]', '', phone_match.group())
    
    name_patterns = [
        r'[Nn]ame:\s*([A-Za-z\s]+?)(?:[,\n]|$)',
        r'[Ii]\'?m\s+([A-Za-z\s]+?)(?:[,\n]|$)',
        r'[Mm]y name is\s+([A-Za-z\s]+?)(?:[,\n]|$)',
        r'[Tt]his is\s+([A-Za-z\s]+?)(?:[,\n]|$)'
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, text)
        if name_match:
            name = name_match.group(1).strip()
            if len(name) > 1:
                info['name'] = name
                break
    
    if 'name' not in info:
        words = text.split()
        names = []
        for word in words:
            if (word.isalpha() and word[0].isupper() and len(word) > 1 and 
                word.lower() not in ['i', 'my', 'the', 'and', 'complaint', 'issue', 'problem', 'name', 'phone', 'email']):
                names.append(word)
        
        if names:
            info['name'] = ' '.join(names[:2])
    
    info['complaint_details'] = text
    
    return info

def extract_complaint_id(text: str) -> str:
    match = re.search(r'\b[A-F0-9]{8}\b', text.upper())
    return match.group() if match else None

available_tools = [rag_faq_search, create_complaint, retrieve_complaint]