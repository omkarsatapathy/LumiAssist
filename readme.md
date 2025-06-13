# Lumi AI Assistant

Lumi is an intelligent Apple support chatbot designed to help customers with technical questions, complaint filing, and ticket management. Built with modern AI technologies and a sleek web interface, Lumi provides conversational support by searching through FAQ documents and managing customer service workflows.

## Project Overview

This project implements a complete AI assistant system with both backend API services and a user-friendly frontend interface. The assistant can understand natural language queries, search through Apple laptop documentation, create support tickets, and maintain conversation context across sessions.

## Core Features

**FAQ Search and Retrieval**
- Intelligent search through Apple laptop FAQ documents using RAG (Retrieval Augmented Generation)
- PDF document processing and content extraction
- Contextual answer generation based on official documentation

**Support Ticket Management**
- Create new support tickets with customer information validation
- Retrieve existing tickets using 8-character alphanumeric IDs
- Automatic data extraction from conversational input
- MongoDB storage for persistent ticket management

**Conversational AI Interface**
- Session-based conversation memory
- Natural language understanding using OpenAI GPT-3.5-turbo
- Streaming response capability for real-time interactions
- Context-aware decision making for when to search vs create tickets

**Modern Web Interface**
- Custom-designed Streamlit frontend with glassmorphism styling
- Fixed bottom input with smooth animations
- Responsive design with proper message threading
- Real-time typing indicators and message animations

## Technology Stack

**Backend Technologies**
- Python 3.x as the primary programming language
- Flask for REST API development and endpoint management
- LangChain for AI agent orchestration and tool integration
- OpenAI GPT-3.5-turbo for natural language processing
- PyPDF2 for PDF document processing and text extraction
- MongoDB with PyMongo for data persistence
- Pydantic for data validation and serialization

**Frontend Technologies**
- Streamlit for rapid web application development
- Custom CSS with glassmorphism design principles
- Google Fonts integration for typography
- Responsive layout with fixed positioning

**AI and ML Components**
- LangChain Agents for function calling and tool orchestration
- OpenAI Functions API for structured tool interactions
- Conversation memory management with token limits
- RAG implementation for document search and retrieval

## Project Structure

```
lumi-ai-assistant/
├── api.py              # Flask REST API with chat endpoints
├── agent.py            # LangChain agent configuration and session management
├── app.py              # Streamlit frontend with custom UI
├── llm.py              # OpenAI model configuration and streaming setup
├── tools.py            # RAG search, complaint management, and database tools
├── run.py              # Development launcher for both services
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
└── .gitignore         # Git ignore patterns
```

## Installation and Setup

**Prerequisites**
Before starting, ensure you have the following installed on your system:
- Python 3.8 or higher
- MongoDB Community Server
- Git for version control
- A text editor or IDE of your choice

**Step 1: Clone the Repository**
```bash
git clone https://github.com/yourusername/lumi-ai-assistant.git
cd lumi-ai-assistant
```

**Step 2: Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Environment Configuration**
Create a `.env` file in the project root:
```bash
touch .env
```

Add your OpenAI API key to the `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

**Step 5: MongoDB Setup**
Install and start MongoDB on your local machine:

For macOS with Homebrew:
```bash
brew install mongodb-community
brew services start mongodb-community
```

For Ubuntu/Debian:
```bash
sudo apt update
sudo apt install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

For Windows:
Download and install MongoDB Community Server from the official website, then start the MongoDB service.

**Step 6: FAQ Document Setup**
Place your Apple laptop FAQ PDF file in your Downloads folder or update the path in `tools.py`:
```python
self.pdf_path = '/path/to/your/Apple Laptop FAQ.pdf'
```

**Step 7: Verify Installation**
Check that all services can connect:
```bash
python run.py
```

This command will verify your OpenAI API key, MongoDB connection, and PDF file availability.

## Running the Application

**Option 1: Using the Launcher (Recommended)**
```bash
python run.py
```

This will start both the Flask API and Streamlit frontend automatically. The launcher performs environment checks and starts services in the correct order.

**Option 2: Manual Startup**
Start the Flask API in one terminal:
```bash
python api.py
```

Start the Streamlit frontend in another terminal:
```bash
streamlit run app.py --server.port=8501
```

**Access Points**
- Frontend Interface: http://localhost:8501
- API Documentation: http://localhost:5001
- Health Check: http://localhost:5001/health

## API Endpoints

**POST /chat**
Standard chat endpoint for single request-response interactions
```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I reset my MacBook?", "session_id": "user123"}'
```

**POST /chat-stream**
Streaming chat endpoint for real-time response generation
```bash
curl -X POST http://localhost:5001/chat-stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a ticket for battery issues", "session_id": "user123"}'
```

**GET /health**
Service health and status check
```bash
curl http://localhost:5001/health
```

**POST /session/{session_id}/clear**
Clear conversation history for a specific session
```bash
curl -X POST http://localhost:5001/session/user123/clear
```

## Usage Examples

**FAQ Search Query**
```
User: "My MacBook won't turn on, what should I do?"
Lumi: [Searches FAQ and provides relevant troubleshooting steps]
```

**Complaint Creation**
```
User: "I need to file a complaint. My name is John Smith, phone 5551234567, email john@email.com. My laptop screen is flickering constantly."
Lumi: [Creates ticket and returns complaint ID: ABC12345]
```

**Ticket Retrieval**
```
User: "What's the status of ticket ABC12345?"
Lumi: [Retrieves and displays ticket information]
```

## Configuration Options

**Model Configuration**
Modify `llm.py` to change AI model settings:
- Model version (currently GPT-3.5-turbo)
- Temperature for response creativity
- Streaming capabilities

**Agent Behavior**
Adjust `agent.py` for conversation handling:
- Memory token limits
- Maximum iterations per query
- Tool selection logic

**Database Settings**
Update `tools.py` for MongoDB configuration:
- Connection string and database name
- Collection indexing and validation
- Data retention policies

## Development and Testing

**Running Tests**
```bash
python -m pytest tests/  # If you add tests
```

**Debug Mode**
Set debug flags in the respective files:
- Flask: `app.run(debug=True)` in `api.py`
- Verbose agent: `verbose=True` in `agent.py`

**Database Management**
Access MongoDB directly:
```bash
mongo
use complaints_db
db.complaints.find()  # View all complaints
```

## Troubleshooting

**Common Issues and Solutions**

MongoDB Connection Failed:
- Ensure MongoDB is running: `brew services list | grep mongodb`
- Check connection string in `tools.py`
- Verify MongoDB is listening on port 27017

OpenAI API Errors:
- Verify API key in `.env` file
- Check API key validity and usage limits
- Ensure proper environment variable loading

PDF Not Found:
- Update path in `tools.py` to match your file location
- Ensure PDF is accessible and not corrupted
- Check file permissions

Port Already in Use:
- Change ports in `api.py` (Flask) or `app.py` (Streamlit)
- Kill existing processes: `lsof -ti:5001 | xargs kill -9`

Streamlit Import Errors:
- Reinstall requirements: `pip install -r requirements.txt`
- Check Python version compatibility
- Verify virtual environment activation

## Contributing

When contributing to this project:

1. Fork the repository and create a feature branch
2. Follow Python PEP 8 style guidelines
3. Add appropriate error handling and logging
4. Test your changes with various input types
5. Update documentation for new features
6. Submit a pull request with a clear description

## Performance Considerations

**Memory Management**
- Conversation memory is limited to 1500 tokens per session
- Large PDF files may impact initial loading time
- MongoDB queries are indexed for faster retrieval

**Scalability Notes**
- Session storage is in-memory (consider Redis for production)
- PDF processing happens on each query (consider caching)
- API rate limits depend on OpenAI plan

## Security Notes

- API keys are stored in environment variables
- No authentication is implemented (add for production)
- Input validation is performed on complaint data
- MongoDB runs without authentication (secure for production)

## Future Enhancements

Potential improvements and features:
- User authentication and authorization system
- Enhanced PDF processing with better chunking strategies
- Integration with additional knowledge sources
- Voice interface capabilities
- Analytics dashboard for support metrics
- Automated ticket routing and escalation

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support and Contact

For questions, issues, or contributions, please create an issue on the GitHub repository or contact the development team.