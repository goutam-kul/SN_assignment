import streamlit as st
from src.agent_orchestrator.agent import DataAnalysisAgent
from src.llm_handler.data_analysis import DataAnalysisEngine
from src.file_processing.process_file import FileProcessor
import os 
import tempfile
import base64
from io import BytesIO

# Initialize session state variables
if 'agent' not in st.session_state:
    st.session_state.agent = DataAnalysisAgent()
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Set up the main page
st.set_page_config(page_title="Data Analysis Assistant", layout="wide")
st.title("Data Analysis Assistant")

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'json', 'txt'])
    
    if uploaded_file is not None:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Process the file
            file_id = uploaded_file.name
            processed_data = st.session_state.agent.process_file(tmp_path, file_id)
            st.session_state.agent.files[file_id] = processed_data
            st.success(f"File '{file_id}' processed successfully!")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
        finally:
            # Clean up the temporary file
            os.unlink(tmp_path)
    
    # Display currently loaded files
    if st.session_state.agent.files:
        st.write("Loaded files:")
        for file_id in st.session_state.agent.files.keys():
            st.write(f"- {file_id}")

# Main content area
st.header("Ask Questions About Your Data")

# Query input
query = st.text_input("Enter your question or visualization request:", placeholder="e.g., 'Show me a summary of the data' or 'Create a bar chart of sales by category'")

if query:
    try:
        # Get response from agent
        response = st.session_state.agent.ask(query)
        
        # Add to conversation history
        st.session_state.conversation.append({"query": query, "response": response})
        
        # Display response
        if response['type'] == 'visualization':
            # Convert base64 string to bytes
            image_bytes = base64.b64decode(response['data']['figure'])
            # Display image from bytes
            st.image(image_bytes)
            st.write(response['message'])
        else:
            st.write(response['message'])
            
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")

# Display conversation history
if st.session_state.conversation:
    st.header("Conversation History")
    for item in reversed(st.session_state.conversation):
        with st.expander(f"Q: {item['query']}", expanded=False):
            if item['response']['type'] == 'visualization':
                base64_image = item['response']['data']['figure']
                image_bytes = base64.b64decode(base64_image)
                st.image(image_bytes)
            st.write(item['response']['message'])

