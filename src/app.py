"""Main Streamlit application for letter refinement."""
import os
import tempfile
import streamlit as st
from src.crew import LetterRefinementCrew
from src.utils.docx_utils import read_docx, create_docx, compare_versions

st.set_page_config(
    page_title="Office Letter Refinement",
    page_icon="📝",
    layout="wide"
)

# Initialize session state for storing refined text
if 'refined_text' not in st.session_state:
    st.session_state.refined_text = None

st.title("📝 Office Letter Refinement System")
st.write("""
Upload your office letter draft and let our AI agents help you improve it.
We'll enhance grammar, spelling, tone, clarity, and structure while maintaining
your message's intent.
""")

# File upload
uploaded_file = st.file_uploader("Upload your letter (.docx)", type="docx")

if uploaded_file:
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        # Read the document
        original_text = read_docx(temp_path)
        
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except PermissionError:
            pass  # Ignore if file is still in use
        
        # Only process if we haven't already
        if st.session_state.refined_text is None:
            with st.spinner("Processing your letter..."):
                # Initialize crew and process the letter
                crew = LetterRefinementCrew(verbose=True)
                st.session_state.refined_text = crew.refine_letter(original_text)
                
                # Compare versions
                summary, changes = compare_versions(original_text, st.session_state.refined_text)
                st.session_state.summary = summary
                st.session_state.changes = changes
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Version")
            st.text_area(
                label="Original Text",
                value=original_text,
                height=300,
                label_visibility="collapsed"
            )
            
        with col2:
            st.subheader("Refined Version")
            st.text_area(
                label="Refined Text",
                value=st.session_state.refined_text,
                height=300,
                label_visibility="collapsed"
            )
        
        # Show changes
        st.subheader("Summary of Changes")
        st.write(st.session_state.summary)
        
        for change in st.session_state.changes:
            with st.expander(f"Changes in Paragraph {change['paragraph']}"):
                st.write("**Original:**")
                st.write(change["original"])
                st.write("**Refined:**")
                st.write(change["refined"])
        
        # Create download button
        if st.button("Generate Download"):
            try:
                # Create a unique filename
                output_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".docx",
                    prefix="refined_letter_"
                ).name
                
                # Create the document using the stored refined text
                create_docx(st.session_state.refined_text, output_file)
                
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

# Add a button to clear the session state and start over
if st.session_state.refined_text is not None:
    if st.button("Process New Document"):
        st.session_state.refined_text = None
        st.session_state.summary = None
        st.session_state.changes = None
        st.experimental_rerun()

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