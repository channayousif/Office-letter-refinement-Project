"""Coherence and Structure Agent for text refinement."""
from typing import Dict, Any
from crewai import Task
from . import BaseLetterAgent

class CoherenceAgent(BaseLetterAgent):
    """Agent responsible for improving coherence and structure."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="Structure Expert",
            role="Text Structure Editor",
            goal="Ensure logical flow and coherence in any text",
            backstory="""I am an expert in text organization and flow.
            I help ensure ideas connect logically while maintaining
            the original style and format of the text.""",
            verbose=verbose
        )
        
    def _create_task(self, text: str) -> Task:
        """Create a task for coherence improvement."""
        return Task(
            description=f"""
            Review and enhance the following text for coherence and flow.
            Focus on:
            
            1. Logical connection of ideas
            2. Natural flow of thoughts
            3. Clear relationships between parts
            4. Smooth transitions
            5. Overall coherence
            
            IMPORTANT: Do not change the format or add structure that wasn't present.
            Only improve the logical flow and connections while keeping the original style.
            
            Original text:
            {text}
            
            Provide an enhanced version that improves coherence while
            maintaining the original style and format.
            """,
            expected_output="Text with improved coherence",
            agent=self
        )

    async def process_text(self, text: str) -> str:
        """
        Process the input text to improve coherence.
        
        Args:
            text: Input text to process
            
        Returns:
            str: Processed text with improved coherence
        """
        task = self._create_task(text)
        result = await self.execute_task(task)
        return result.strip() 