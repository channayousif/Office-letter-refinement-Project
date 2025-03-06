"""Coherence and Structure Agent for letter refinement."""
from typing import Dict, Any
from crewai import Task
from . import BaseLetterAgent

class CoherenceAgent(BaseLetterAgent):
    """Agent responsible for improving coherence and structure."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="Structure Expert",
            role="Professional Document Structure Editor",
            goal="Ensure logical flow and proper structure in business letters",
            backstory="""I am an expert in document organization and structure.
            I specialize in ensuring business letters flow logically, maintain
            coherence throughout, and follow professional formatting standards.""",
            verbose=verbose
        )
        
    def _create_task(self, text: str) -> Task:
        """Create a task for coherence and structure improvement."""
        return Task(
            description=f"""
            Review and enhance the following business letter text for
            coherence and structure. Focus on:
            
            1. Logical flow between paragraphs
            2. Clear paragraph structure
            3. Appropriate transitions
            4. Consistent formatting
            5. Professional document organization
            
            Original text:
            {text}
            
            Provide an enhanced version that improves the document's
            structure while maintaining its content and message.
            """,
            expected_output="Text with improved coherence and structure",
            agent=self
        )

    async def process_text(self, text: str) -> str:
        """
        Process the input text to improve coherence and structure.
        
        Args:
            text: Input text to process
            
        Returns:
            str: Processed text with improved coherence and structure
        """
        task = self._create_task(text)
        result = await self.execute_task(task)
        return result.strip() 