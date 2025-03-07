"""Main Streamlit application for letter refinement."""
import os
import tempfile
import streamlit as st
import pandas as pd
from src.crew import LetterRefinementCrew
from src.utils.docx_utils import (
    extract_document_elements,
    create_docx_from_elements,
    TextElement,
    TableElement,
    ImageElement
)

st.set_page_config(
    page_title="Office Letter Refinement",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = 0
if 'refined_elements' not in st.session_state:
    st.session_state.refined_elements = None
if 'original_elements' not in st.session_state:
    st.session_state.original_elements = None
if 'comparison' not in st.session_state:
    st.session_state.comparison = None

def reset_app():
    """Reset the app state completely."""
    st.session_state.refined_elements = None
    st.session_state.original_elements = None
    st.session_state.comparison = None
    st.session_state.session_id += 1
    st.rerun()

def display_elements(elements, container):
    """Display document elements in a Streamlit container."""
    for element in elements:
        if isinstance(element, TextElement):
            # Clean any markdown from text
            import re
            clean_text = element.text
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_text)
            clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)
            container.write(clean_text)
            
        elif isinstance(element, TableElement):
            # Display table as a pandas DataFrame
            if len(element.rows) > 0:
                try:
                    # Process table to handle merged cells
                    # We'll indicate merged cells by using MultiIndex columns
                    import pandas as pd
                    import numpy as np
                    
                    # Use first row as header
                    headers = element.columns if element.columns else element.rows[0]
                    
                    # Ensure column names are unique and not empty
                    processed_headers = []
                    for i, header in enumerate(headers):
                        # Replace empty headers with a placeholder
                        if not header or header.strip() == '':
                            header = f"Column_{i+1}"
                        
                        # Handle duplicate headers by adding a suffix
                        if header in processed_headers:
                            suffix = 1
                            while f"{header}_{suffix}" in processed_headers:
                                suffix += 1
                            header = f"{header}_{suffix}"
                        
                        processed_headers.append(header)
                    
                    # Process data rows - detect and handle merged cells
                    # For UI, we'll keep merged cells but mark duplicates
                    data_rows = []
                    if len(element.rows) > 1:  # If there's at least one data row
                        for i in range(1, len(element.rows)):
                            row = element.rows[i]
                            # Ensure row has right number of cells
                            processed_row = list(row)
                            while len(processed_row) < len(processed_headers):
                                processed_row.append("")
                            
                            # Truncate if too long
                            if len(processed_row) > len(processed_headers):
                                processed_row = processed_row[:len(processed_headers)]
                                
                            data_rows.append(processed_row)
                    
                    # Create DataFrame with the processed data
                    if data_rows:
                        df = pd.DataFrame(data_rows, columns=processed_headers)
                        
                        # Format the display - highlight potential merged cells
                        # We'll use DataFrame styling for this
                        def highlight_duplicates(s):
                            # Create a mask for duplicate adjacent values in a series
                            mask = s.duplicated(keep='first') & ~s.isna() & (s != "")
                            return ['background-color: #e6f3ff' if v else '' for v in mask]
                        
                        # Apply styling
                        styled_df = df.style.apply(highlight_duplicates)
                        
                        # Display with styling
                        container.write("**Table:**")
                        container.dataframe(styled_df, use_container_width=True)
                    else:
                        # Just headers, no data
                        df = pd.DataFrame(columns=processed_headers)
                        container.write("**Table (Headers Only):**")
                        container.dataframe(df, use_container_width=True)
                    
                except Exception as e:
                    # Fallback to simple display if any error occurs
                    container.write("**Table:** (Error displaying formatted table)")
                    container.write(f"{len(element.rows)} rows x {len(element.columns)} columns")
            else:
                container.write("[Empty Table]")
                
        elif isinstance(element, ImageElement):
            container.write("[IMAGE]")
            
        # Add spacing between elements
        container.write("")

def elements_to_text(elements):
    """Convert document elements to text for display."""
    text_parts = []
    for element in elements:
        if isinstance(element, TextElement):
            # Clean any remaining markdown from the text
            clean_text = element.text
            # Remove common markdown formatting
            import re
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_text)  # Bold
            clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)      # Italic
            clean_text = re.sub(r'__(.*?)__', r'\1', clean_text)      # Bold
            clean_text = re.sub(r'_(.*?)_', r'\1', clean_text)        # Italic
            text_parts.append(clean_text)
        elif isinstance(element, TableElement):
            # Create a text representation of the table that mimics how it will appear in the document
            table_text = []
            table_text.append(f"[TABLE: {len(element.rows)} rows x {len(element.columns)} columns]")
            
            # Add a sample of the table content - format as a simple ASCII table
            if len(element.rows) > 0 and len(element.columns) > 0:
                # Show up to 3 rows as a preview
                max_preview_rows = min(3, len(element.rows))
                
                # Get max width for each column for proper alignment
                col_widths = [0] * len(element.columns)
                for i in range(max_preview_rows):
                    for j in range(len(element.columns)):
                        if j < len(element.rows[i]):
                            col_widths[j] = max(col_widths[j], len(str(element.rows[i][j])))
                
                # Create header
                header = "| "
                for j in range(len(element.columns)):
                    header += f"{element.columns[j]:{col_widths[j]}} | "
                table_text.append(header)
                
                # Create separator
                separator = "|-"
                for width in col_widths:
                    separator += "-" * width + "-|-"
                table_text.append(separator)
                
                # Create rows
                for i in range(max_preview_rows):
                    row_text = "| "
                    for j in range(len(element.columns)):
                        if j < len(element.rows[i]):
                            cell_text = str(element.rows[i][j])
                            row_text += f"{cell_text:{col_widths[j]}} | "
                        else:
                            row_text += " " * col_widths[j] + " | "
                    table_text.append(row_text)
                
                if len(element.rows) > max_preview_rows:
                    table_text.append("| ... (more rows) ... |")
            
            text_parts.append("\n".join(table_text))
        elif isinstance(element, ImageElement):
            # Add image placeholder with caption if available
            image_text = "[IMAGE]"
            if element.caption:
                image_text += f": {element.caption}"
            text_parts.append(image_text)
    return "\n\n".join(text_parts)

st.title("📝 Office Letter Refinement System")
st.write("""
Upload your office letter draft and let our AI agents help you improve it.
We'll enhance grammar, spelling, tone, clarity, and structure while maintaining
your message's intent.
""")

# File upload with session-based key to force reset
uploaded_file = st.file_uploader(
    "Upload your letter (.docx)",
    type="docx",
    key=f"uploader_{st.session_state.session_id}"
)

if uploaded_file:
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        # Extract document elements
        original_elements = extract_document_elements(temp_path)
        st.session_state.original_elements = original_elements
        
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except PermissionError:
            pass  # Ignore if file is still in use
        
        # Only process if we haven't already
        if st.session_state.refined_elements is None:
            with st.spinner("Processing your letter..."):
                # Initialize crew and process the letter
                crew = LetterRefinementCrew(verbose=True)
                result = crew.refine_letter(original_elements)
                st.session_state.refined_elements = result["refined_elements"]
                st.session_state.comparison = result["comparison"]
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Version")
            display_elements(st.session_state.original_elements, col1)
            
        with col2:
            st.subheader("Refined Version")
            display_elements(st.session_state.refined_elements, col2)
        
        # Show changes
        st.subheader("Summary of Changes")
        st.write(st.session_state.comparison["summary"])
        
        # Create download button
        if st.button("Generate Download"):
            try:
                # Create a unique filename
                output_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".docx",
                    prefix="refined_letter_"
                ).name
                
                # Create the document using the stored refined elements
                create_docx_from_elements(st.session_state.refined_elements, output_file)
                
                # Read the file for download
                with open(output_file, "rb") as f:
                    file_contents = f.read()
                
                # Clean up the file
                try:
                    os.unlink(output_file)
                except PermissionError:
                    # Schedule file for deletion on reboot if can't delete now
                    try:
                        import ctypes
                        ctypes.windll.kernel32.MoveFileExW(
                            output_file, None, 
                            ctypes.windll.kernel32.MOVEFILE_DELAY_UNTIL_REBOOT
                        )
                    except:
                        pass  # Ignore if can't schedule for deletion
                
                # Create download button
                st.download_button(
                    label="Download Refined Letter",
                    data=file_contents,
                    file_name="refined_letter.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"Error generating download: {str(e)}")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

# Add a button to reset the app
if st.session_state.refined_elements is not None:
    if st.button("Process New Document"):
        reset_app()

st.sidebar.title("About")
st.sidebar.write("""
This tool uses AI agents to improve your office letters by:
- Correcting grammar and spelling
- Enhancing tone and clarity
- Improving structure and coherence
- Ensuring professional standards
""")

st.sidebar.info("""
💡 **Tip:** For best results, ensure your letter is in .docx format and contains
clear paragraphs.
""") 