"""Orchestration Agent for coordinating text refinement workflow."""
from typing import Dict, Any
from crewai import Task
from . import BaseLetterAgent

class OrchestratorAgent(BaseLetterAgent):
    """Agent responsible for coordinating the text refinement workflow."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="Workflow Orchestrator",
            role="Text Refinement Coordinator",
            goal="Coordinate and optimize the text refinement process across all specialized agents",
            backstory="""I am an expert text improvement coordinator. I ensure that each 
            refinement stage builds upon the previous ones effectively while maintaining 
            the original style and format of the text.""",
            verbose=verbose
        )
        
    def create_task_prompt(self, text: str, stage: str, previous_feedback: str = None) -> str:
        """Create a context-aware prompt for the current refinement stage."""
        base_prompts = {
            "grammar": """
                Focus on grammar and spelling corrections:
                1. Keep the original style and format
                2. Fix grammatical errors and typos
                3. Ensure proper punctuation and capitalization
                4. Correct verb tense agreements
                5. Maintain the original structure
                
                IMPORTANT: Do not add any formatting or structure that wasn't in the original.
                
                Original text:
                {text}
                """,
            "tone": """
                Building on the grammatical improvements, enhance clarity:
                1. Keep the corrected grammar and spelling
                2. Improve clarity and effectiveness
                3. Ensure natural language
                4. Maintain consistent tone
                5. Preserve original style
                
                IMPORTANT: Do not change the format or structure.
                
                Previous version:
                {text}
                
                Previous feedback:
                {feedback}
                """,
            "coherence": """
                With improved grammar and clarity, focus on flow:
                1. Keep all previous improvements
                2. Enhance logical connections
                3. Ensure smooth transitions
                4. Improve overall coherence
                5. Maintain original format
                
                IMPORTANT: Keep the original style and structure.
                
                Previous version:
                {text}
                
                Previous feedback:
                {feedback}
                """,
            "review": """
                Perform final review and refinement:
                1. Verify all improvements
                2. Ensure overall quality
                3. Check format consistency
                4. Confirm natural flow
                5. Make final polish
                
                IMPORTANT: Preserve the original style and format.
                
                Previous version:
                {text}
                
                Previous feedback:
                {feedback}
                """
        }
        
        prompt = base_prompts[stage]
        return prompt.format(
            text=text,
            feedback=previous_feedback if previous_feedback else "No previous feedback available."
        )
        
    def evaluate_result(self, original: str, refined: str, stage: str) -> Dict[str, Any]:
        """Evaluate the results of each refinement stage."""
        evaluation_prompts = {
            "grammar": "Evaluate grammar and spelling improvements while noting any format changes.",
            "tone": "Assess clarity improvements, ensuring original style is preserved.",
            "coherence": "Evaluate flow improvements and coherence, checking format preservation.",
            "review": "Perform final quality check, verifying style and format consistency."
        }
        
        return {
            "stage": stage,
            "evaluation_prompt": evaluation_prompts[stage],
            "original": original,
            "refined": refined,
            "maintains_format": self._check_format_consistency(original, refined)
        }
    
    def _check_format_consistency(self, original: str, refined: str) -> bool:
        """Check if the document formatting is maintained."""
        # Compare basic structural elements
        orig_lines = original.split('\n')
        refined_lines = refined.split('\n')
        
        # Check for similar paragraph structure
        orig_paragraphs = [line for line in orig_lines if line.strip()]
        refined_paragraphs = [line for line in refined_lines if line.strip()]
        
        # Basic format checks
        format_consistent = (
            len(orig_paragraphs) == len(refined_paragraphs)
            and all(
                self._has_similar_structure(orig, ref)
                for orig, ref in zip(orig_paragraphs, refined_paragraphs)
            )
        )
        
        return format_consistent
    
    def _has_similar_structure(self, original: str, refined: str) -> bool:
        """Check if two text blocks have similar structural elements."""
        # Check for common structural elements
        structural_elements = [
            ('- ', '- '),  # List items
            ('\t', '\t'),  # Tabs
            ('•', '•'),    # Bullets
            (':', ':'),    # Colons
            ('. ', '. '),  # Sentence breaks
        ]
        
        return all(
            (elem[0] in original) == (elem[1] in refined)
            for elem in structural_elements
        ) 