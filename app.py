import streamlit as st
from utils import run_agent_sync

st.set_page_config(page_title="MCP POC", page_icon="🤖", layout="wide")

st.title("Model Context Protocol(MCP) - Learning Path Generator")

# Initialize session state for progress
if 'current_step' not in st.session_state:
    st.session_state.current_step = ""
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'last_section' not in st.session_state:
    st.session_state.last_section = ""
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False

# Sidebar for API and URL configuration
st.sidebar.header("Configuration")

# API Key input
google_api_key = st.sidebar.text_input("Google API Key", type="password")

with st.sidebar.expander("🧠 How to get Gemini API Key", expanded=False):
    st.markdown("""
    1. Visit [Google AI Studio](https://makersuite.google.com/app)  
    2. Log in with your Google account  
    3. Click **“Get API Key”** in the left sidebar  
    4. Then click **“Create API Key”** at the top right  
    5. If needed, choose “Create in New Project”  
    6. Once generated, **click Copy** and paste it here  
    """)


# Pipedream URLs
# YouTube Pipedream
youtube_pipedream_url = st.sidebar.text_input("YouTube URL (Required)", 
    placeholder="Enter your Pipedream YouTube URL")

with st.sidebar.expander("▶️ How to get YouTube Pipedream URL", expanded=False):
    st.markdown("""
    1. Go to [Pipedream](https://pipedream.com) and sign in  
    2. Create an Account: Sign up for a Pipedream account if you haven't already
    3. Search for the Tool: Use the search bar to find the tool you want to integrate (e.g., Youtube).
    4. Connect Account: Click Connect Account and authenticate the desired tool.
    5. In the Configuration:
        - Connect with your Google account and give all required permissions to access
        - Copy the MCP server URL
    6. Paste that here as your **Pipedream URL**
    """)

    

# Secondary tool selection
secondary_tool = st.sidebar.radio(
    "Select Secondary Tool:",
    ["Drive", "Notion"]
)

# Initialize URLs to None
drive_pipedream_url = None
notion_pipedream_url = None

# Drive selected
if secondary_tool == "Drive":
    drive_pipedream_url = st.sidebar.text_input(
        "Drive URL", 
        placeholder="Enter your Pipedream Drive URL"
    )

    with st.sidebar.expander("🔄 How to get Drive Pipedream URL", expanded=False):
        st.markdown("""
        1. Go to [Pipedream](https://pipedream.com) and sign in  
    2. Create an Account: Sign up for a Pipedream account if you haven't already
    3. Search for the Tool: Use the search bar to find the tool you want to integrate (e.g., Drive).
    4. Connect Account: Click Connect Account and authenticate the desired tool.
    5. In the Configuration:
        - Connect with your Google account and give all required permissions to access
        - Copy the MCP server URL
    6. Paste that here as your **Pipedream URL**
        """)

# Notion selected
elif secondary_tool == "Notion":
    notion_pipedream_url = st.sidebar.text_input(
        "Notion URL", 
        placeholder="Enter your Pipedream Notion URL"
    )

    with st.sidebar.expander("📝 How to get Notion Pipedream URL", expanded=False):
        st.markdown("""
        1. Go to [Pipedream](https://pipedream.com) and sign in  
    2. Create an Account: Sign up for a Pipedream account if you haven't already
    3. Search for the Tool: Use the search bar to find the tool you want to integrate (e.g., Notion).
    4. Connect Account: Click Connect Account and authenticate the desired tool.
    5. In the Configuration:
        - Connect with your Google account and give all required permissions to access
        - Copy the MCP server URL
    6. Paste that here as your **Pipedream URL**
        """)

  


# Quick guide before goal input
st.info("""
**Quick Guide:**
1. Enter your Google API key and YouTube URL (required)
2. Select and configure your secondary tool (Drive or Notion)
3. Enter a clear learning goal, for example:
    - "I want to learn python basics in 3 days"
    - "I want to learn data science basics in 10 days"
""")


# Main content area
st.header("Enter Your Goal")
user_goal = st.text_input("Enter your learning goal:",
                        help="Describe what you want to learn, and we'll generate a structured path using YouTube content and your selected tool.")

# Progress area
progress_container = st.container()
progress_bar = st.empty()

def update_progress(message: str):
    """Update progress in the Streamlit UI"""
    st.session_state.current_step = message
    
    # Determine section and update progress
    if "Setting up agent with tools" in message:
        section = "Setup"
        st.session_state.progress = 0.1
    elif "Added Google Drive integration" in message or "Added Notion integration" in message:
        section = "Integration"
        st.session_state.progress = 0.2
    elif "Creating AI agent" in message:
        section = "Setup"
        st.session_state.progress = 0.3
    elif "Generating your learning path" in message:
        section = "Generation"
        st.session_state.progress = 0.5
    elif "Learning path generation complete" in message:
        section = "Complete"
        st.session_state.progress = 1.0
        st.session_state.is_generating = False
    else:
        section = st.session_state.last_section or "Progress"
    
    st.session_state.last_section = section
    
    # Show progress bar
    progress_bar.progress(st.session_state.progress)
    
    # Update progress container with current status
    with progress_container:
        # Show section header if it changed
        if section != st.session_state.last_section and section != "Complete":
            st.write(f"**{section}**")
        
        # Show message with tick for completed steps
        if message == "Learning path generation complete!":
            st.success("All steps completed! 🎉")
        else:
            prefix = "✓" if st.session_state.progress >= 0.5 else "→"
            st.write(f"{prefix} {message}")

# Generate Learning Path button
if st.button("Generate Learning Path", type="primary", disabled=st.session_state.is_generating):
    if not google_api_key:
        st.error("Please enter your Google API key in the sidebar.")
    elif not youtube_pipedream_url:
        st.error("YouTube URL is required. Please enter your Pipedream YouTube URL in the sidebar.")
    elif (secondary_tool == "Drive" and not drive_pipedream_url) or (secondary_tool == "Notion" and not notion_pipedream_url):
        st.error(f"Please enter your Pipedream {secondary_tool} URL in the sidebar.")
    elif not user_goal:
        st.warning("Please enter your learning goal.")
    else:
        try:
            # Set generating flag
            st.session_state.is_generating = True
            
            # Reset progress
            st.session_state.current_step = ""
            st.session_state.progress = 0
            st.session_state.last_section = ""
            
            result = run_agent_sync(
                google_api_key=google_api_key,
                youtube_pipedream_url=youtube_pipedream_url,
                drive_pipedream_url=drive_pipedream_url,
                notion_pipedream_url=notion_pipedream_url,
                user_goal=user_goal,
                progress_callback=update_progress
            )
            
            # Display results
            st.header("Your Learning Path")
            # print(result)
            if result and "messages" in result:
                for msg in result["messages"]:
                    st.markdown(f"📚 {msg.content}")

            else:
                st.error("No results were generated. Please try again.")
                st.session_state.is_generating = False
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Please check your API keys and URLs, and try again.")
            st.session_state.is_generating = False
