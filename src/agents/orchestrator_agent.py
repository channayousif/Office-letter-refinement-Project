"""Orchestration Agent for coordinating letter refinement workflow."""
from typing import Dict, Any
from crewai import Task
from . import BaseLetterAgent

class OrchestratorAgent(BaseLetterAgent):
    """Agent responsible for coordinating the letter refinement workflow."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="Workflow Orchestrator",
            role="Document Refinement Coordinator",
            goal="Coordinate and optimize the letter refinement process across all specialized agents",
            backstory="""I am an expert document workflow coordinator with deep understanding 
            of business communication standards and document processing. I ensure that each 
            refinement stage builds upon the previous ones effectively while maintaining 
            document formatting and professional standards.""",
            verbose=verbose
        )
        
    def create_task_prompt(self, letter_text: str, stage: str, previous_feedback: str = None) -> str:
        """Create a context-aware prompt for the current refinement stage."""
        base_prompts = {
            "grammar": """
                As the workflow coordinator, I need you to focus on grammar and spelling corrections:
                1. Maintain the original document structure and formatting
                2. Fix grammatical errors and typos
                3. Ensure proper punctuation and capitalization
                4. Correct verb tense agreements
                5. Keep all formatting elements intact (headers, lists, etc.)
                
                Original text:
                {text}
                """,
            "tone": """
                Building on the grammatical improvements, enhance the tone and clarity:
                1. Maintain the corrected grammar and spelling
                2. Improve professional language and tone
                3. Enhance clarity while keeping the message
                4. Ensure consistent formality level
                5. Preserve all document formatting
                
                Previous version:
                {text}
                
                Previous feedback:
                {feedback}
                """,
            "coherence": """
                With improved grammar and tone, focus on document coherence:
                1. Maintain all previous improvements
                2. Enhance paragraph flow and transitions
                3. Ensure logical structure progression
                4. Strengthen overall document organization
                5. Keep formatting consistent with business standards
                
                Previous version:
                {text}
                
                Previous feedback:
                {feedback}
                """,
            "review": """
                Perform final review and refinement:
                1. Verify all previous improvements are preserved
                2. Ensure consistent professional standards
                3. Validate document formatting integrity
                4. Confirm proper business letter structure
                5. Make final polish while maintaining format
                
                Previous version:
                {text}
                
                Previous feedback:
                {feedback}
                """
        }
        
        prompt = base_prompts[stage]
        return prompt.format(
            text=letter_text,
            feedback=previous_feedback if previous_feedback else "No previous feedback available."
        )
        
    def evaluate_result(self, original: str, refined: str, stage: str) -> Dict[str, Any]:
        """Evaluate the results of each refinement stage."""
        evaluation_prompts = {
            "grammar": "Evaluate grammar and spelling improvements while noting any formatting concerns.",
            "tone": "Assess tone improvements and clarity enhancements, ensuring format preservation.",
            "coherence": "Evaluate structural improvements and document flow, checking format consistency.",
            "review": "Perform final quality assessment, verifying all formatting and professional standards."
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