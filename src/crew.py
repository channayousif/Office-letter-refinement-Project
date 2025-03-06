"""Crew configuration for letter refinement."""
from typing import List, Dict, Any
from crewai import Crew, Task
from src.agents import (
    GrammarAgent,
    ToneAgent,
    CoherenceAgent,
    ReviewAgent,
    OrchestratorAgent
)

class LetterRefinementCrew:
    """Manages the letter refinement crew and their tasks."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the crew with all required agents."""
        self.verbose = verbose
        self.orchestrator = OrchestratorAgent(verbose=verbose)
        self.grammar_agent = GrammarAgent(verbose=verbose)
        self.tone_agent = ToneAgent(verbose=verbose)
        self.coherence_agent = CoherenceAgent(verbose=verbose)
        self.review_agent = ReviewAgent(verbose=verbose)
        self.feedback = {}
        self._cached_result = None  # Cache for the final result
        
    def create_tasks(self, letter_text: str) -> List[Task]:
        """Create tasks for each stage of letter refinement."""
        tasks = []
        
        # Task 1: Grammar and Spelling
        grammar_task = Task(
            description=self.orchestrator.create_task_prompt(letter_text, "grammar"),
            expected_output="A grammatically correct and properly structured version of the letter",
            agent=self.grammar_agent
        )
        tasks.append(grammar_task)
        
        # Task 2: Tone and Clarity
        tone_task = Task(
            description=self.orchestrator.create_task_prompt(
                "{{grammar_task.output}}", 
                "tone",
                self.feedback.get("grammar")
            ),
            expected_output="A version of the letter with improved tone and clarity",
            agent=self.tone_agent,
            context=[grammar_task]
        )
        tasks.append(tone_task)
        
        # Task 3: Coherence and Structure
        coherence_task = Task(
            description=self.orchestrator.create_task_prompt(
                "{{tone_task.output}}", 
                "coherence",
                self.feedback.get("tone")
            ),
            expected_output="A well-structured and coherent version of the letter",
            agent=self.coherence_agent,
            context=[tone_task]
        )
        tasks.append(coherence_task)
        
        # Task 4: Final Review
        review_task = Task(
            description=self.orchestrator.create_task_prompt(
                "{{coherence_task.output}}", 
                "review",
                self.feedback.get("coherence")
            ),
            expected_output="A final, polished version of the letter meeting all professional standards",
            agent=self.review_agent,
            context=[coherence_task]
        )
        tasks.append(review_task)
        
        return tasks
    
    def _clean_output(self, text: str) -> str:
        """Clean the output text by removing code blocks and unnecessary formatting."""
        # Remove code block markers
        text = text.replace('```', '')
        
        # Remove common language specifiers that might appear at the start
        common_prefixes = ['text', 'markdown', 'docx', 'doc']
        lines = text.split('\n')
        if lines and lines[0].lower().strip() in common_prefixes:
            lines = lines[1:]
        text = '\n'.join(lines)
        
        # Remove any remaining markdown formatting
        text = text.replace('*', '').replace('_', '').replace('#', '')
        
        # Clean up extra whitespace while preserving paragraph structure
        paragraphs = [p.strip() for p in text.split('\n\n')]
        text = '\n\n'.join(p for p in paragraphs if p)
        
        return text.strip()
    
    def _extract_result(self, result: Any) -> str:
        """Extract and clean the final text from various result formats."""
        if hasattr(result, 'output'):
            text = str(result.output)
        elif hasattr(result, 'raw_output'):
            text = str(result.raw_output)
        elif isinstance(result, (list, tuple)) and len(result) > 0:
            text = str(result[-1])
        elif isinstance(result, str):
            text = result
        elif isinstance(result, dict) and 'output' in result:
            text = str(result['output'])
        else:
            text = str(result)
        
        return self._clean_output(text)
    
    def refine_letter(self, letter_text: str) -> str:
        """Process the letter through all agents in sequence."""
        # If we have a cached result, return it
        if self._cached_result is not None:
            return self._cached_result
        
        # Create tasks
        tasks = self.create_tasks(letter_text)
        
        # Create crew
        crew = Crew(
            agents=[
                self.orchestrator,
                self.grammar_agent,
                self.tone_agent,
                self.coherence_agent,
                self.review_agent
            ],
            tasks=tasks,
            verbose=self.verbose
        )
        
        # Execute tasks and get the final result
        try:
            result = crew.kickoff()
            final_text = self._extract_result(result)
            
            # Evaluate the final result
            evaluation = self.orchestrator.evaluate_result(letter_text, final_text, "review")
            if not evaluation['maintains_format']:
                # If format is not maintained, try to restore it while keeping improvements
                final_text = self._restore_format(letter_text, final_text)
            
            # Cache the result
            self._cached_result = final_text
            return final_text
            
        except Exception as e:
            raise ValueError(f"Error processing tasks: {str(e)}")
    
    def _restore_format(self, original: str, refined: str) -> str:
        """Attempt to restore original formatting while keeping content improvements."""
        # Split into paragraphs
        orig_paras = original.split('\n\n')
        refined_paras = refined.split('\n\n')
        
        # Ensure we have the same number of paragraphs
        min_paras = min(len(orig_paras), len(refined_paras))
        result_paras = []
        
        for i in range(min_paras):
            # Get the original paragraph's formatting
            orig_para = orig_paras[i]
            refined_para = refined_paras[i]
            
            # Preserve indentation and special characters
            orig_leading_space = len(orig_para) - len(orig_para.lstrip())
            orig_trailing_space = len(orig_para) - len(orig_para.rstrip())
            
            # Apply original formatting to refined content
            formatted_para = (
                ' ' * orig_leading_space +
                refined_para.strip() +
                ' ' * orig_trailing_space
            )
            
            result_paras.append(formatted_para)
        
        # Join paragraphs with original spacing
        return '\n\n'.join(result_paras) 