from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from llm import llm
from tools import available_tools, extract_complaint_id
import re

class LumiAgent:
    def __init__(self):
        self.llm = llm
        
        # System prompt for intelligent agent
        system_prompt = """You are Lumi, an intelligent AI assistant for Apple laptop customer support.

Your capabilities:
1. Search FAQ knowledge base for technical questions and troubleshooting
2. Create customer complaints when issues can't be resolved
3. Retrieve complaint details when customers provide complaint IDs

Decision-making process:
- If user asks technical questions, search FAQ first using rag_faq_search tool
- If FAQ doesn't have the answer or user wants to file complaint, use create_complaint tool
- If user mentions a complaint ID (8-character alphanumeric), use retrieve_complaint tool

Guidelines:
- Always think about the user's intent before responding
- Be empathetic and professional
- Provide complete, helpful responses
- When creating complaints, ensure you have all required info: name, phone, email, complaint details
- If information is missing, ask the user to provide all details in one message

Remember: Every response should be thoughtful and contextual. No generic or static responses."""

        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=available_tools,
            prompt=self.prompt
        )
        
        # Session storage
        self.sessions = {}
    
    def get_session(self, session_id: str):
        """Get or create session"""
        if session_id not in self.sessions:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                max_token_limit=1500
            )
            
            executor = AgentExecutor(
                agent=self.agent,
                tools=available_tools,
                memory=memory,
                verbose=True,
                max_iterations=3,
                early_stopping_method="generate"
            )
            
            self.sessions[session_id] = {
                'executor': executor,
                'memory': memory
            }
        
        return self.sessions[session_id]
    
    def process_message(self, user_message: str, session_id: str = "default") -> str:
        """Process user message with intelligent decision making"""
        try:
            session = self.get_session(session_id)
            
            # Let the agent think and decide what to do
            result = session['executor'].invoke({
                "input": user_message,
                "chat_history": session['memory'].chat_memory.messages
            })
            
            return result['output']
            
        except Exception as e:
            # Even error responses should be contextual
            return self._generate_error_response(str(e), user_message)
    
    def _generate_error_response(self, error: str, user_message: str) -> str:
        """Generate contextual error response"""
        try:
            error_prompt = f"""The user said: "{user_message}"
            
I encountered this error: {error}

Generate a helpful, empathetic response that:
1. Acknowledges the user's request
2. Explains there was a technical issue
3. Offers alternative help or asks them to try again
4. Stays in character as Lumi, the support assistant"""
            
            response = self.llm.invoke(error_prompt)
            return response.content
        except:
            return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
    
    def clear_session(self, session_id: str):
        """Clear session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def analyze_intent(self, message: str) -> str:
        """Analyze user intent for debugging"""
        complaint_id = extract_complaint_id(message)
        
        if complaint_id:
            return f"COMPLAINT_RETRIEVAL: {complaint_id}"
        
        complaint_keywords = ['complaint', 'issue', 'problem', 'not working', 'broken', 'defective']
        if any(keyword in message.lower() for keyword in complaint_keywords):
            return "COMPLAINT_CREATION"
        
        return "FAQ_SEARCH"

# Global agent instance
lumi_agent = LumiAgent()