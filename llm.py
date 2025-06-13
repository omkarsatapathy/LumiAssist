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
            openai_api_key=self.api_key,
            streaming=True
        )
    
    def get_llm(self):
        return self.model
    
    def stream_response(self, prompt: str):
        try:
            for chunk in self.model.stream(prompt):
                if hasattr(chunk, 'content'):
                    yield chunk.content
        except Exception as e:
            yield f"Error: {str(e)}"

llm_config = LLMConfig()
llm = llm_config.get_llm()