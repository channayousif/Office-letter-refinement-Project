"""Base agent for letter refinement."""
from typing import Any, Dict
from crewai import Agent, Task, LLM
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class BaseLetterAgent(Agent):
    """Base class for letter refinement agents."""
    
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        tools: list = None,
        verbose: bool = False
    ):
        # Initialize the LLM
        llm = LLM(
            model="gemini/gemini-2.0-flash",
            api_key=GOOGLE_API_KEY,
            temperature=0.7
        )
        
        super().__init__(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools or [],
            verbose=verbose,
            llm=llm
        ) 