import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class LLMConfig:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=self.api_key
        )
    
    def get_llm(self):
        return self.model
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using LLM"""
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"


llm_config = LLMConfig()
llm = llm_config.get_llm()