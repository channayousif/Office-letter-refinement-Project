"""Grammar and Spelling Agent for text refinement."""
from typing import Dict, Any
from crewai import Task
from . import BaseLetterAgent

class GrammarAgent(BaseLetterAgent):
    """Agent responsible for grammar and spelling corrections."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="Grammar Expert",
            role="Professional Grammar and Spelling Editor",
            goal="Ensure perfect grammar, spelling, and basic sentence structure in any text",
            backstory="""I am an expert editor specializing in grammar and spelling. 
            I identify and correct grammatical errors, spelling mistakes, and improve 
            sentence structure while maintaining the original message's intent.""",
            verbose=verbose
        )
        
    def _create_task(self, text: str) -> Task:
        """Create a task for grammar and spelling correction."""
        return Task(
            description=f"""
            Review and correct the following text for grammar and spelling.
            Maintain the original style and intent while ensuring:
            
            1. Perfect grammar and spelling
            2. Proper punctuation
            3. Correct verb tense agreement
            4. Natural sentence structure
            5. Consistent capitalization
            
            IMPORTANT: Do not add any formatting or structure that wasn't in the original.
            Only fix grammar, spelling, and basic sentence structure issues.
            Keep the text in its original format and style.
            
            Original text:
            {text}
            
            Provide the corrected version while maintaining the original
            meaning and style.
            """,
            expected_output="Corrected text with perfect grammar and spelling",
            agent=self
        )

    async def process_text(self, text: str) -> str:
        """
        Process the input text to correct grammar and spelling.
        
        Args:
            text: Input text to process
            
        Returns:
            str: Processed text with corrected grammar and spelling
        """
        task = self._create_task(text)
        result = await self.execute_task(task)
        return result.strip() 