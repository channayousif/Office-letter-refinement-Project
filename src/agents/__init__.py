"""Base agent and agent initialization."""
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
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True
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
        
    async def process_text(self, text: str) -> str:
        """
        Process the input text according to the agent's specific role.
        
        Args:
            text: Input text to process
            
        Returns:
            str: Processed text
        """
        task = self._create_task(text)
        result = await self.execute_task(task)
        return result.strip()
        
    def _create_task(self, text: str) -> Task:
        """
        Create a CrewAI Task object.
        
        Args:
            text: Input text to process
            
        Returns:
            Task: CrewAI Task object
        """
        raise NotImplementedError("Subclasses must implement _create_task method")

"""Agent initialization and exports."""
from .base import BaseLetterAgent
from .grammar_agent import GrammarAgent
from .tone_agent import ToneAgent
from .coherence_agent import CoherenceAgent
from .review_agent import ReviewAgent
from .orchestrator_agent import OrchestratorAgent

__all__ = [
    'BaseLetterAgent',
    'GrammarAgent',
    'ToneAgent',
    'CoherenceAgent',
    'ReviewAgent',
    'OrchestratorAgent'
] 