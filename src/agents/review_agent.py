"""Final Review Agent for letter refinement."""
from typing import Dict, Any
from crewai import Task
from . import BaseLetterAgent

class ReviewAgent(BaseLetterAgent):
    """Agent responsible for final review and professional standards."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="Final Reviewer",
            role="Professional Document Reviewer",
            goal="Ensure the letter meets all professional standards and is ready for use",
            backstory="""I am a senior business communication expert with extensive
            experience in reviewing and finalizing professional documents. I ensure
            that business letters meet the highest standards of quality and
            professionalism before they are sent.""",
            verbose=verbose
        )
        
    def _create_task(self, text: str) -> Task:
        """Create a task for final document review."""
        return Task(
            description=f"""
            Perform a final review of the following business letter text.
            Ensure it meets all professional standards and is ready for use.
            Focus on:
            
            1. Overall professional quality
            2. Consistency in style and tone
            3. Appropriate business letter format
            4. Effectiveness of communication
            5. Final polish and refinement
            
            Original text:
            {text}
            
            Provide the final version, ensuring it meets the highest
            professional standards while maintaining the intended message.
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