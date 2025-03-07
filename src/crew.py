"""Letter refinement crew module."""
import re
from typing import List, Dict, Any, Optional
from crewai import Crew, Process, Task
from .agents import (
    GrammarAgent,
    ToneAgent,
    CoherenceAgent,
    ReviewAgent,
    ManagerAgent
)
from .utils.docx_utils import (
    TextElement,
    TableElement,
    ImageElement,
    DocumentElement
)

class LetterRefinementCrew:
    """Crew for refining office letters."""

    def __init__(self, verbose: bool = False):
        """Initialize the crew with agents."""
        self.grammar_agent = GrammarAgent(verbose=verbose)
        self.tone_agent = ToneAgent(verbose=verbose)
        self.coherence_agent = CoherenceAgent(verbose=verbose)
        self.review_agent = ReviewAgent(verbose=verbose)
        self.manager_agent = ManagerAgent(verbose=verbose)
        self._cached_result = None
        
        # Create the crew
        self.crew = Crew(
            agents=[
                self.grammar_agent,
                self.tone_agent,
                self.coherence_agent,
                self.review_agent
            ],  # Manager agent should not be in this list
            tasks=self.create_tasks(""),  # Placeholder tasks, will be replaced
            manager_agent=self.manager_agent,
            process=Process.hierarchical,
            verbose=verbose
        )

    def create_tasks(self, text: str) -> List[Task]:
        """Create tasks for the crew."""
        # This is a placeholder - actual tasks will be created by the manager
        return []
    
    def _get_agent_for_stage(self, stage: str):
        """Get the appropriate agent for a task stage."""
        agents = {
            "grammar": self.grammar_agent,
            "tone": self.tone_agent,
            "coherence": self.coherence_agent,
            "review": self.review_agent
        }
        return agents.get(stage, self.manager_agent)
    
    def _extract_text(self, elements: List[DocumentElement]) -> str:
        """Extract text from document elements."""
        text_parts = []
        table_count = 0
        
        for element in elements:
            if isinstance(element, TextElement):
                text_parts.append(element.text)
            elif isinstance(element, TableElement):
                # Add a unique table placeholder with ID
                table_id = table_count
                table_count += 1
                table_placeholder = f"[TABLE_ID_{table_id}: {len(element.rows)} rows x {len(element.columns)} columns]"
                text_parts.append(table_placeholder)
            elif isinstance(element, ImageElement):
                # Add a placeholder for images
                text_parts.append("[IMAGE]")
        
        return "\n\n".join(text_parts)
    
    def _clean_output(self, text: str) -> str:
        """Clean the output text from code blocks and other formatting."""
        if not text:
            return ""
            
        # Import re module for regex operations
        import re
        
        # Remove code block markers and common language specifiers
        text = re.sub(r'```[a-zA-Z]*\n', '', text)
        text = re.sub(r'```', '', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'__(.*?)__', r'\1', text)      # Bold
        text = re.sub(r'_(.*?)_', r'\1', text)        # Italic
        text = re.sub(r'~~(.*?)~~', r'\1', text)      # Strikethrough
        text = re.sub(r'^\s*#{1,6}\s+(.*?)$', r'\1', text, flags=re.MULTILINE)  # Headers
        
        # Remove list markers
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # Unordered lists
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # Ordered lists
        
        # Replace ", and" with " and"
        text = re.sub(r',\s*and\s+', ' and ', text)
        text = re.sub(r',\s*and\n', ' and\n', text)
        
        # Clean up any double spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Preserve paragraph structure
        paragraphs = text.split('\n\n')
        cleaned_paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return '\n\n'.join(cleaned_paragraphs)
    
    def _extract_result(self, result: Any) -> str:
        """Extract the result text from various result formats."""
        if isinstance(result, str):
            return self._clean_output(result)
        elif isinstance(result, dict) and "result" in result:
            return self._clean_output(result["result"])
        elif isinstance(result, list) and len(result) > 0:
            # Get the last result if it's a list
            last_result = result[-1]
            if isinstance(last_result, dict) and "result" in last_result:
                return self._clean_output(last_result["result"])
            return self._clean_output(str(last_result))
        return self._clean_output(str(result))
    
    def _merge_refined_text(self, elements: List[DocumentElement], refined_text: str) -> List[DocumentElement]:
        """Merge refined text with original document elements."""
        if not refined_text:
            return elements
            
        # Clean the refined text
        refined_text = self._clean_output(refined_text)
        
        # Split refined text into parts
        text_parts = refined_text.split("\n\n")
        
        # Map to track original tables by their placeholders
        table_map = {}
        for i, element in enumerate(elements):
            if isinstance(element, TableElement):
                # Create the same table placeholder as in _extract_text
                table_id = len(table_map)
                placeholder = f"[TABLE_ID_{table_id}: {len(element.rows)} rows x {len(element.columns)} columns]"
                table_map[placeholder] = element
        
        # Process the refined text parts
        result = []
        text_index = 0
        
        for element in elements:
            if isinstance(element, TextElement):
                # Skip table and image placeholders or find next text part
                while (text_index < len(text_parts) and 
                      (text_parts[text_index].startswith("[TABLE") or 
                       text_parts[text_index] == "[IMAGE]")):
                    text_index += 1
                
                if text_index < len(text_parts):
                    # Append refined text
                    result.append(TextElement(text_parts[text_index]))
                    text_index += 1
                else:
                    # Fallback to original if no more refined text
                    result.append(element)
            elif isinstance(element, TableElement):
                # Always preserve the original table structure
                result.append(element)
            elif isinstance(element, ImageElement):
                # Keep images as they are
                result.append(element)
        
        return result
    
    def _restore_format(self, original_text: str, refined_text: str) -> str:
        """Attempt to restore original formatting while keeping improvements."""
        # This is a placeholder for format restoration logic
        # For now, just return the refined text
        return refined_text
    
    def compare_versions(self, original_elements: List[DocumentElement], 
                         refined_elements: List[DocumentElement]) -> Dict[str, Any]:
        """Compare original and refined versions."""
        changes = {
            "text_changes": 0,
            "table_changes": 0,
            "total_elements": len(original_elements),
            "changed_elements": 0,
            "summary": ""
        }
        
        if len(original_elements) != len(refined_elements):
            changes["summary"] = f"Element count changed: {len(original_elements)} → {len(refined_elements)}"
            changes["changed_elements"] = max(len(original_elements), len(refined_elements))
            return changes
        
        for i, (orig, refined) in enumerate(zip(original_elements, refined_elements)):
            if type(orig) != type(refined):
                changes["changed_elements"] += 1
                continue
                
            if isinstance(orig, TextElement):
                # Normalize whitespace for comparison
                orig_text = re.sub(r'\s+', ' ', orig.text.strip())
                refined_text = re.sub(r'\s+', ' ', refined.text.strip())
                
                if orig_text != refined_text:
                    changes["text_changes"] += 1
                    changes["changed_elements"] += 1
            
            elif isinstance(orig, TableElement):
                # Compare tables cell by cell
                table_changed = False
                cell_changes = 0
                
                if len(orig.rows) != len(refined.rows) or len(orig.columns) != len(refined.columns):
                    table_changed = True
                else:
                    for r in range(len(orig.rows)):
                        for c in range(len(orig.columns)):
                            orig_cell = orig.rows[r][c].strip()
                            refined_cell = refined.rows[r][c].strip()
                            if orig_cell != refined_cell:
                                cell_changes += 1
                
                if table_changed or cell_changes > 0:
                    changes["table_changes"] += 1
                    changes["changed_elements"] += 1
        
        # Calculate percentage of text changes
        text_elements = sum(1 for e in original_elements if isinstance(e, TextElement))
        if text_elements > 0:
            text_change_percent = (changes["text_changes"] / text_elements) * 100
        else:
            text_change_percent = 0
            
        # Generate summary
        changes["summary"] = (
            f"Changed {changes['changed_elements']} of {changes['total_elements']} elements. "
            f"Text changes: {changes['text_changes']} ({text_change_percent:.1f}%). "
            f"Table changes: {changes['table_changes']}."
        )
        
        return changes
    
    def refine_letter(self, elements: List[DocumentElement]) -> Dict[str, Any]:
        """Refine a letter using the crew."""
        # Check if we already have a cached result
        if self._cached_result:
            return self._cached_result
            
        # Extract text from elements
        text = self._extract_text(elements)
        
        # Create tasks with the manager agent
        task_sequence = self.manager_agent.create_task_sequence(text)
        
        # Create a new crew with the tasks
        tasks = []
        current_text = text
        
        # Process each task in the sequence
        for task_info in task_sequence:
            stage = task_info["stage"]
            result = task_info["result"]
            
            # Store the result for the next stage
            current_text = result
        
        # Use the final result
        refined_text = current_text
        
        # Merge refined text with original elements
        refined_elements = self._merge_refined_text(elements, refined_text)
        
        # Compare versions
        comparison = self.compare_versions(elements, refined_elements)
        
        # Cache the result
        self._cached_result = {
            "refined_elements": refined_elements,
            "comparison": comparison
        }
        
        return self._cached_result 