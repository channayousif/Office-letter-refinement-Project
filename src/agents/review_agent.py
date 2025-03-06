"""Final Review Agent for text refinement."""
from typing import Dict, Any
from crewai import Task
from . import BaseLetterAgent

class ReviewAgent(BaseLetterAgent):
    """Agent responsible for final review and quality."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="Final Reviewer",
            role="Text Quality Reviewer",
            goal="Ensure the text meets high quality standards while preserving its original style",
            backstory="""I am an expert in reviewing and finalizing text.
            I ensure that writing is clear, effective, and polished while
            maintaining its original style and intended message.""",
            verbose=verbose
        )
        
    def _create_task(self, text: str) -> Task:
        """Create a task for final text review."""
        return Task(
            description=f"""
            Perform a final review of the following text. Focus on:
            
            1. Overall clarity and effectiveness
            2. Consistency in style
            3. Grammar and spelling accuracy
            4. Natural flow and coherence
            5. Final polish and refinement
            
            IMPORTANT: Do not change the format or add structure that wasn't present.
            Only make final improvements while preserving the original style.
            
            Original text:
            {text}
            
            Provide the final version, ensuring high quality while
            maintaining the original style and format.
            """,
            expected_output="Final polished version of the text",
            agent=self
        )

    async def process_text(self, text: str) -> str:
        """
        Process the input text for final review.
        
        Args:
            text: Input text to process
            
        Returns:
            str: Final reviewed and polished text
        """
        task = self._create_task(text)
        result = await self.execute_task(task)
        return result.strip() 