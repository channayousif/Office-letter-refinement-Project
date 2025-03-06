"""Tone and Clarity Agent for text refinement."""
from typing import Dict, Any
from crewai import Task
from . import BaseLetterAgent

class ToneAgent(BaseLetterAgent):
    """Agent responsible for improving tone and clarity."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="Tone Expert",
            role="Professional Tone and Clarity Editor",
            goal="Enhance the clarity and effectiveness of any text",
            backstory="""I am an expert in improving text clarity and tone.
            I help make writing more effective while preserving the author's
            intended style and message.""",
            verbose=verbose
        )
        
    def _create_task(self, text: str) -> Task:
        """Create a task for tone and clarity improvement."""
        return Task(
            description=f"""
            Review and enhance the following text for clarity while preserving
            its original style. Focus on:
            
            1. Clear and natural language
            2. Effective communication
            3. Appropriate word choice
            4. Consistent tone
            5. Meaningful expression
            
            IMPORTANT: Do not change the format or add structure that wasn't present.
            Only improve clarity and tone while keeping the original style.
            
            Original text:
            {text}
            
            Provide an enhanced version that maintains the original
            style while improving clarity.
            """,
            expected_output="Text with improved clarity",
            agent=self
        )

    async def process_text(self, text: str) -> str:
        """
        Process the input text to improve tone and clarity.
        
        Args:
            text: Input text to process
            
        Returns:
            str: Processed text with improved tone and clarity
        """
        task = self._create_task(text)
        result = await self.execute_task(task)
        return result.strip() 