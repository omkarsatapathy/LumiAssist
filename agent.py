from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from llm import llm
from tools import available_tools
import json

class LumiAgent:
    def __init__(self):
        self.llm = llm
        
        system_prompt = """You are Lumi, an intelligent Apple support assistant.

            Your role is to help customers by:
            1. Answering technical questions using the FAQ search tool
            2. Creating support tickets when customers have unresolved issues
            3. Retrieving ticket information when customers provide ticket IDs

            Decision guidelines:
            - For technical questions, search the FAQ first
            - If FAQ doesn't resolve the issue OR customer explicitly wants to file a complaint/ticket, create one
            - If customer mentions an 8-character alphanumeric ID, retrieve that ticket
            - When creating tickets, ensure you have: name, phone, email, and issue description
            - Always be professional and helpful

            You decide when to create tickets based on customer needs, not keywords."""

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=available_tools,
            prompt=self.prompt
        )
        
        self.sessions = {}
    
    def get_session(self, session_id: str):
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
    
    def process_message(self, user_message: str, session_id: str = "default"):
        try:
            session = self.get_session(session_id)
            
            result = session['executor'].invoke({
                "input": user_message,
                "chat_history": session['memory'].chat_memory.messages
            })
            
            response_text = result['output']
            
            # Extract and print JSON if present
            try:
                if '{' in response_text and '}' in response_text:
                    # Find all JSON objects in the response
                    import re
                    json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text)
                    for json_str in json_matches:
                        try:
                            json_data = json.loads(json_str)
                            print("\n" + "="*50)
                            print("COMPLAINT JSON RESPONSE:")
                            print("="*50)
                            print(json.dumps(json_data, indent=2))
                            print("="*50 + "\n")
                            break
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"Error parsing JSON: {e}")
            
            return response_text
            
        except Exception as e:
            return f"I apologize, but I encountered a technical issue: {str(e)}. Please try again."
    
    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

lumi_agent = LumiAgent()