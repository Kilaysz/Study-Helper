import streamlit as st
import os
import shutil
# from src.utils.pdf_loader import load_pdf_content

# Page Configuration
st.set_page_config(
    page_title="Study Partner Agent",
    page_icon="🎓",
    layout="wide"
)

# --- HEADER ---
st.title("🎓 Study Partner Agent")
st.markdown("""
I am your AI study assistant. I can **Summarize** documents, **Validate** facts against academic papers, 
and **Query** the web for real-time answers.
""")

# --- SIDEBAR & CONFIG ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. Mode Selection
    mode = st.selectbox(
        "Select Capability",
        ["Query (Web Search)", "Summarize (Document)", "Validate (Fact Check)"],
        index=0
    )
    
    # 2. File Uploader
    st.subheader("📂 Document Context")
    uploaded_file = st.file_uploader("Upload PDF or PPT", type=["pdf", "pptx"])
    
    # 3. API Keys (Optional: You can rely on .env instead)
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = st.text_input("OpenAI API Key", type="password")

    st.divider()
    if st.button("Clear Chat History", type="primary"):
        st.session_state.messages = []
        st.session_state.file_text = ""
        st.rerun()

# --- STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_text" not in st.session_state:
    st.session_state.file_text = ""

# --- FILE PROCESSING LOGIC ---
if uploaded_file:
    # 1. Ensure 'data' directory exists
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # 2. Save the file to disk
    file_path = os.path.join(data_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # 3. Load content (Only if we haven't already processed this exact file)
    # Simple check: if file text is empty or filename changed (logic simplified for demo)
    if not st.session_state.file_text:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            extracted_text = load_pdf_content(file_path)
            st.session_state.file_text = extracted_text
            st.sidebar.success("✅ File Processed")

# --- CHAT UI ---
# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle Input
if prompt := st.chat_input("Ask a question or request a summary..."):
    
    # 1. Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # --- CONNECTING TO YOUR LANGGRAPH ---
        try:
            # We import here to avoid loading the heavy graph at startup
            from src.graph import build_graph
            
            # Initialize Graph
            app = build_graph()
            
            # Prepare Inputs
            inputs = {
                "messages": st.session_state.messages,
                "file_content": st.session_state.file_text,
                "mode": mode
            }
            
            # Stream the output
            full_response = ""
            # The app.stream method returns events. We look for the final message.
            with st.spinner(f"Running {mode.split()[0]} Agent..."):
                for event in app.stream(inputs):
                    # Inspect the event to find the AI's response message
                    # This logic depends on your specific Node output structure.
                    # Generally, we look for the last message added to state.
                    for node_name, values in event.items():
                        if "messages" in values:
                            last_msg = values["messages"][-1]
                            # Simple streaming simulation for the UI
                            full_response = last_msg.content
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error running the agent: {e}")
            st.info("Tip: Make sure you have filled in `src/graph.py` and your `.env` file.")