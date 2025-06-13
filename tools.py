import PyPDF2
import re
import uuid
import json
from datetime import datetime
from langchain.tools import tool
from pydantic import BaseModel, Field
from pymongo import MongoClient

class RAGConfig:
    def __init__(self):
        self.chunk_size = 500
        self.chunk_overlap = 100
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

def get_mongo_client():
    client = MongoClient('mongodb://localhost:27017/')
    return client.complaints_db.complaints

def init_db():
    try:
        collection = get_mongo_client()
        collection.create_index("complaint_id", unique=True)
        print("MongoDB connection established")
    except Exception as e:
        print(f"MongoDB connection error: {e}")

@tool
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

@tool
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
        
        complaint_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
        
        document = {
            "complaint_id": complaint_id,
            "name": info['name'],
            "phone_number": phone_clean,
            "email": info['email'],
            "complaint_details": info['complaint_details'],
            "status": "created",
            "created_at": datetime.now()
        }
        
        print("\n" + "="*60)
        print("MONGODB INSERT DOCUMENT:")
        print("="*60)
        print(json.dumps(document, indent=2, default=str))
        print("="*60 + "\n")
        
        collection = get_mongo_client()
        result = collection.insert_one(document)
        
        print(f"✅ SUCCESS: Complaint {complaint_id} created in MongoDB\n")
        
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

@tool
def retrieve_complaint(complaint_id: str) -> str:
    """Retrieve complaint details by ID"""
    try:
        collection = get_mongo_client()
        result = collection.find_one({"complaint_id": complaint_id})
        
        if not result:
            return f"No complaint found with ID: {complaint_id}"
        
        response_json = {
            "complaint_id": result['complaint_id'],
            "name": result['name'],
            "phone_number": result['phone_number'],
            "email": result['email'],
            "complaint_details": result['complaint_details'],
            "status": result['status'],
            "created_at": str(result['created_at'])
        }
        
        return f"""Complaint Details Found:
                ID: {result['complaint_id']}
                Name: {result['name']}
                Phone: {result['phone_number']}
                Email: {result['email']}
                Issue: {result['complaint_details']}
                Status: {result['status']}
                Created: {result['created_at']}

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