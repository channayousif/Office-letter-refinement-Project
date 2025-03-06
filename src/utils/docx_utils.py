"""Utility functions for handling .docx files."""
from typing import Tuple, List, Dict
from docx import Document
from docx.shared import Inches

def read_docx(file_path: str) -> str:
    """
    Read content from a .docx file.
    
    Args:
        file_path: Path to the .docx file
        
    Returns:
        str: Extracted text content
    """
    doc = Document(file_path)
    full_text = []
    
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)
            
    return "\n\n".join(full_text)

def create_docx(content: str, output_path: str) -> None:
    """
    Create a new .docx file with the given content.
    
    Args:
        content: Text content to write
        output_path: Path where to save the .docx file
    """
    doc = Document()
    
    # Set up document margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    # Split content into paragraphs
    paragraphs = content.split("\n\n")
    
    # Add each paragraph to the document
    for para_text in paragraphs:
        if para_text.strip():
            doc.add_paragraph(para_text.strip())
    
    # Save the document
    doc.save(output_path)

def compare_versions(original: str, refined: str) -> Tuple[str, List[Dict]]:
    """
    Compare original and refined versions of the text.
    
    Args:
        original: Original text content
        refined: Refined text content
        
    Returns:
        Tuple[str, list]: Summary of changes and list of specific modifications
    """
    # Split into paragraphs
    original_paras = original.split("\n\n")
    refined_paras = refined.split("\n\n")
    
    changes = []
    summary_points = []
    
    # Compare paragraphs
    for i, (orig, ref) in enumerate(zip(original_paras, refined_paras)):
        if orig.strip() != ref.strip():
            changes.append({
                "paragraph": i + 1,
                "original": orig.strip(),
                "refined": ref.strip()
            })
            
            # Generate a summary point for this change
            if len(orig) != len(ref):
                if len(ref) > len(orig):
                    summary_points.append(f"Paragraph {i + 1}: Expanded for clarity and detail")
                else:
                    summary_points.append(f"Paragraph {i + 1}: Condensed for conciseness")
            else:
                summary_points.append(f"Paragraph {i + 1}: Refined for improved clarity and professionalism")
    
    # Handle case where no changes were made
    if not summary_points:
        summary = "No significant changes were required. The document already meets professional standards."
    else:
        summary = "The following improvements were made:\n- " + "\n- ".join(summary_points)
    
    return summary, changes 