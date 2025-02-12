import streamlit as st
from bedrock_service import BedrockService
from agents import FeasibilityAnalysisSupervisor
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import textwrap

# Load environment variables
load_dotenv()

# Initialize services
bedrock_service = BedrockService()
feasibility_supervisor = FeasibilityAnalysisSupervisor(bedrock_service)

# Default feasibility report template
DEFAULT_REPORT_TEMPLATE = """1. Requirement Overview
   - Brief description of the requirement
   - Key objectives and goals
   
2. Technical Feasibility
   - Technical approach and architecture
   - Required technologies and components
   - Integration points with existing systems
   
3. Resource Requirements
   - Development team composition
   - Infrastructure needs
   - Third-party services or dependencies
   
4. Potential Risks and Challenges
   - Technical risks
   - Business risks
   - Mitigation strategies
   
5. Timeline Estimation
   - High-level project phases
   - Estimated duration for each phase
   - Key milestones
   
6. Recommendations
   - Go/No-go recommendation
   - Alternative approaches if applicable
   - Next steps"""

def init_session_state():
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = bedrock_service.default_system_prompt
    if 'report_template' not in st.session_state:
        st.session_state.report_template = DEFAULT_REPORT_TEMPLATE

def format_size(size):
    """Format file size to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"

def format_datetime(dt):
    """Format datetime to human readable format"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_text_block(text):
    """Format text block for better readability"""
    # Remove excessive newlines
    text = '\n'.join(line for line in text.splitlines() if line.strip())
    # Wrap long lines
    text = '\n'.join(
        textwrap.fill(line, width=100) if len(line) > 100 else line
        for line in text.splitlines()
    )
    return text

def display_kb_results(chunks):
    """Display KB retrieval results in a collapsible section"""
    with st.expander("📚 Retrieved Knowledge", expanded=False):
        if not chunks:
            st.info("No relevant information found in the knowledge base.")
            return
        
        for i, chunk in enumerate(chunks, 1):
            st.markdown(f"### Source {i}")
            st.markdown(f"**Score:** {chunk['score']:.2f}")
            if chunk.get('location'):
                st.markdown(f"**File:** {chunk['location'].get('filename', 'Unknown')}")
            
            # Display the complete text for this source
            st.markdown("**Retrieved Content:**")
            st.markdown(f"```\n{chunk['text']}\n```")
            st.markdown("---")

def display_raw_request(raw_request):
    """Display raw model request in a collapsible section"""
    with st.expander("🔍 Raw Model Request", expanded=False):
        st.code(raw_request, language='json')

def main():
    st.title("Product Manager Assistant")
    
    # Initialize session state
    init_session_state()
    
    # Sidebar for feature selection
    feature = st.sidebar.selectbox(
        "Select Feature",
        ["Product Knowledge Q&A", "Feasibility Report Generator", "Document Management"]
    )
    
    if feature == "Product Knowledge Q&A":
        st.header("Product Knowledge Q&A")
        st.info("Ask questions about the product using our knowledge base. Your conversation history will be maintained.")
        
        # System prompt configuration
        with st.sidebar:
            st.subheader("Assistant Configuration")
            new_prompt = st.text_area(
                "System Prompt",
                value=st.session_state.system_prompt,
                help="Customize how the assistant should behave"
            )
            if new_prompt != st.session_state.system_prompt:
                st.session_state.system_prompt = new_prompt
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                # Display processing details for assistant messages
                if message["role"] == "assistant" and "details" in message:
                    display_kb_results(message["details"].get("kb_chunks", []))
                    if message["details"].get("raw_request"):
                        display_raw_request(message["details"]["raw_request"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about the product:"):
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.conversation_history.append(prompt)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = bedrock_service.get_product_qa(
                        prompt, 
                        st.session_state.conversation_history,
                        st.session_state.system_prompt
                    )
                    st.write(result['response'])
                    
                    # Display processing details
                    display_kb_results(result['kb_chunks'])
                    if result.get('raw_request'):
                        display_raw_request(result['raw_request'])
            
            # Add assistant response to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": result['response'],
                "details": result
            })
            st.session_state.conversation_history.append(result['response'])
        
        # Clear chat button
        if st.sidebar.button("Clear Chat History"):
            st.session_state.conversation_history = []
            st.session_state.messages = []
            st.rerun()
                
    elif feature == "Feasibility Report Generator":
        st.header("Feasibility Report Generator")
        st.info("Generate a detailed feasibility report for new requirements using our multi-agent system.")
        
        # Configuration sidebar
        with st.sidebar:
            st.subheader("Report Configuration")
            
            # Report template configuration
            st.markdown("### Report Template")
            st.markdown("Customize the sections and requirements for the feasibility report:")
            
            new_template = st.text_area(
                "Report Template",
                value=st.session_state.report_template,
                height=400,
                help="Define the structure and requirements for the feasibility report"
            )
            
            if new_template != st.session_state.report_template:
                st.session_state.report_template = new_template
            
            # Reset template button
            if st.button("Reset to Default Template"):
                st.session_state.report_template = DEFAULT_REPORT_TEMPLATE
                st.rerun()
        
        # Input for new requirement
        requirement = st.text_area("Describe the new requirement:", height=200)
        
        if st.button("Generate Report"):
            if requirement:
                # Create status containers for each agent
                requirement_status = st.status("🔍 Requirements Analysis")
                technical_status = st.status("💻 Technical Analysis")
                timeline_status = st.status("📅 Timeline Analysis")
                synthesis_status = st.status("📊 Final Synthesis")
                
                try:
                    # Start requirement analysis
                    with requirement_status:
                        requirement_status.update(label="🔍 Requirements Analysis - In Progress")
                        st.write("Analyzing business requirements and stakeholder needs...")
                        requirement_analysis = feasibility_supervisor.requirement_analyst.analyze_requirement(requirement)
                        st.write("✅ Requirements analysis completed")
                        st.markdown("### Requirements Analysis")
                        st.markdown(requirement_analysis)
                        requirement_status.update(label="🔍 Requirements Analysis - Complete", state="complete")
                    
                    # Start technical analysis
                    with technical_status:
                        technical_status.update(label="💻 Technical Analysis - In Progress")
                        st.write("Analyzing technical feasibility and architecture...")
                        technical_analysis = feasibility_supervisor.technical_analyst.analyze_technical_feasibility(
                            requirement,
                            requirement_analysis
                        )
                        st.write("✅ Technical analysis completed")
                        st.markdown("### Technical Analysis")
                        st.markdown(technical_analysis)
                        technical_status.update(label="💻 Technical Analysis - Complete", state="complete")
                    
                    # Start timeline analysis
                    with timeline_status:
                        timeline_status.update(label="📅 Timeline Analysis - In Progress")
                        st.write("Analyzing project timeline and resource requirements...")
                        timeline_analysis = feasibility_supervisor.timeline_analyst.analyze_timeline(
                            requirement,
                            requirement_analysis,
                            technical_analysis
                        )
                        st.write("✅ Timeline analysis completed")
                        st.markdown("### Timeline Analysis")
                        st.markdown(timeline_analysis)
                        timeline_status.update(label="📅 Timeline Analysis - Complete", state="complete")
                    
                    # Start final synthesis
                    with synthesis_status:
                        synthesis_status.update(label="📊 Final Synthesis - In Progress")
                        st.write("Synthesizing final feasibility report...")
                        result = feasibility_supervisor.generate_feasibility_report(requirement)
                        st.write("✅ Final synthesis completed")
                        st.markdown("### Final Feasibility Report")
                        st.markdown(result['response'])
                        synthesis_status.update(label="📊 Final Synthesis - Complete", state="complete")
                    
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
            else:
                st.warning("Please enter a requirement description.")
    
    else:  # Document Management
        st.header("Document Management")
        
        # Create tabs for upload and list
        tab1, tab2 = st.tabs(["Upload Document", "Document List"])
        
        with tab1:
            st.info("Upload product documentation to enhance the knowledge base. Supported formats: TXT, MD, PDF")
            
            uploaded_file = st.file_uploader("Choose a file", type=['txt', 'md', 'pdf'])
            
            if uploaded_file is not None:
                # Read file content
                try:
                    file_content = uploaded_file.read()
                    
                    # Convert bytes to string for text files
                    if uploaded_file.type in ['text/plain', 'text/markdown']:
                        file_content = file_content.decode('utf-8')
                    
                    if st.button("Upload to Knowledge Base"):
                        with st.spinner("Uploading document..."):
                            success, message = bedrock_service.upload_to_kb(
                                file_content,
                                uploaded_file.name
                            )
                            
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
        
        with tab2:
            st.info("View and manage documents in the knowledge base")
            
            # Add refresh button
            if st.button("Refresh Document List"):
                st.rerun()
            
            # List documents
            documents = bedrock_service.list_documents()
            
            if not documents:
                st.warning("No documents found in the knowledge base.")
            else:
                # Create a table of documents
                for doc in documents:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.write(doc['filename'])
                        with col2:
                            st.write(format_size(doc['size']))
                        with col3:
                            st.write(format_datetime(doc['last_modified']))
                        with col4:
                            if st.button("Delete", key=doc['key']):
                                with st.spinner("Deleting document..."):
                                    success, message = bedrock_service.delete_document(doc['key'])
                                    if success:
                                        st.success(message)
                                        st.rerun()
                                    else:
                                        st.error(message)

if __name__ == "__main__":
    main()
