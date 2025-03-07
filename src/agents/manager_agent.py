"""Manager Agent for coordinating the letter refinement process."""
from typing import Dict, Any, List
from crewai import Task
from . import BaseLetterAgent

class ManagerAgent(BaseLetterAgent):
    """Agent responsible for managing and coordinating the letter refinement process."""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="Project Manager",
            role="Letter Refinement Manager",
            goal="Efficiently manage the letter refinement process and ensure high-quality results",
            backstory="""I am an expert project manager specializing in document refinement.
            I coordinate multiple specialized agents to ensure each document is improved
            effectively while maintaining its original intent and structure. I oversee
            the entire process from initial grammar checks to final polishing.""",
            verbose=verbose
        )
    
    def create_task_sequence(self, text: str) -> List[Dict[str, Any]]:
        """Create a sequence of tasks for letter refinement."""
        tasks = []
        current_text = text
        
        # Grammar task
        grammar_task = Task(
            description="Review and correct this text for grammar and spelling: " + 
                      current_text + 
                      "\n\nFocus on:\n" +
                      "1. Keep the original style and format\n" +
                      "2. Fix grammatical errors and typos\n" +
                      "3. Ensure proper punctuation and capitalization\n" +
                      "4. Correct verb tense agreements\n" +
                      "5. Maintain the original structure",
            expected_output="Corrected text with perfect grammar and spelling",
            agent=self
        )
        grammar_result = self.execute_task(grammar_task)
        tasks.append({
            "stage": "grammar",
            "result": grammar_result
        })
        current_text = grammar_result
        
        # Tone task
        tone_task = Task(
            description="Improve the clarity and tone of this text: " + 
                      current_text + 
                      "\n\nFocus on:\n" +
                      "1. Keep the corrected grammar and spelling\n" +
                      "2. Improve clarity and effectiveness\n" +
                      "3. Ensure natural language\n" +
                      "4. Maintain consistent tone\n" +
                      "5. Preserve original style",
            expected_output="Text with improved clarity and tone",
            agent=self
        )
        tone_result = self.execute_task(tone_task)
        tasks.append({
            "stage": "tone",
            "result": tone_result
        })
        current_text = tone_result
        
        # Coherence task
        coherence_task = Task(
            description="Improve the flow and coherence of this text: " + 
                      current_text + 
                      "\n\nFocus on:\n" +
                      "1. Keep all previous improvements\n" +
                      "2. Enhance logical connections\n" +
                      "3. Ensure smooth transitions\n" +
                      "4. Improve overall coherence\n" +
                      "5. Maintain original format",
            expected_output="Text with improved coherence and flow",
            agent=self
        )
        coherence_result = self.execute_task(coherence_task)
        tasks.append({
            "stage": "coherence",
            "result": coherence_result
        })
        current_text = coherence_result
        
        # Final review task
        review_task = Task(
            description="Perform final review and polish of this text: " + 
                      current_text + 
                      "\n\nFocus on:\n" +
                      "1. Verify all improvements\n" +
                      "2. Ensure overall quality\n" +
                      "3. Check format consistency\n" +
                      "4. Confirm natural flow\n" +
                      "5. Make final polish",
            expected_output="Final polished version of the text",
            agent=self
        )
        final_result = self.execute_task(review_task)
        tasks.append({
            "stage": "review",
            "result": final_result
        })
        
        return tasks
    
    def evaluate_task_result(self, original: str, result: str, stage: str) -> Dict[str, Any]:
        """Evaluate the results of a task stage."""
        eval_task = Task(
            description="Evaluate the following text transformation for the " + stage + " stage:\n\n" +
                      "Original text:\n" + original + "\n\n" +
                      "Transformed text:\n" + result + "\n\n" +
                      "Evaluate based on:\n" +
                      "1. Quality of improvements\n" +
                      "2. Consistency with original\n" +
                      "3. Format preservation\n" +
                      "4. Overall effectiveness\n\n" +
                      "Provide a detailed evaluation with scores (1-10) for each aspect.",
            expected_output="Detailed evaluation with scores",
            agent=self
        )
        
        evaluation = self.execute_task(eval_task)
        
        return {
            "stage": stage,
            "evaluation": evaluation,
            "maintains_format": self._check_format_consistency(original, result)
        }
    
    def _check_format_consistency(self, original: str, result: str) -> bool:
        """Check if the document formatting is maintained."""
        # Compare basic structural elements
        orig_lines = original.split('\n')
        result_lines = result.split('\n')
        
        # Check for similar paragraph structure
        orig_paragraphs = [line for line in orig_lines if line.strip()]
        result_paragraphs = [line for line in result_lines if line.strip()]
        
        # Basic format checks
        if len(orig_paragraphs) != len(result_paragraphs):
            return False
            
        # Check indentation and special characters
        for orig, res in zip(orig_paragraphs, result_paragraphs):
            orig_leading = len(orig) - len(orig.lstrip())
            res_leading = len(res) - len(res.lstrip())
            if orig_leading != res_leading:
                return False
        
        return True 