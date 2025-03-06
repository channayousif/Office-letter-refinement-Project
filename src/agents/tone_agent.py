"""Tone and Clarity Agent for letter refinement."""
from typing import Dict, Any
from crewai import Task
from . import BaseLetterAgent

class ToneAgent(BaseLetterAgent):
    """Agent responsible for improving tone and clarity."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="Tone Expert",
            role="Professional Tone and Clarity Editor",
            goal="Enhance the tone, professionalism, and clarity of business letters",
            backstory="""I am a professional editor specializing in business communication.
            My expertise lies in refining the tone of business letters to ensure they strike
            the perfect balance between professionalism, clarity, and effectiveness.""",
            verbose=verbose
        )
        
    def _create_task(self, text: str) -> Task:
        """Create a task for tone and clarity improvement."""
        return Task(
            description=f"""
            Review and enhance the following business letter text for tone
            and clarity while maintaining its professional nature. Focus on:
            
            1. Professional and appropriate tone
            2. Clear and concise language
            3. Effective communication of ideas
            4. Appropriate level of formality
            5. Positive and constructive messaging
            
            Original text:
            {text}
            
            Provide an enhanced version that maintains the original
            message while improving tone and clarity.
            """,
            expected_output="Text with improved tone and clarity",
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