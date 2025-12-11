"""
AI Chat Assistant
Natural language interface to explore campaign finance data
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_all_data

# Page config
st.set_page_config(page_title="AI Chat", page_icon="🤖", layout="wide")

# Load data
@st.cache_data
def load_data():
    return load_all_data()

data = load_data()

# Helper function for demo responses
def generate_demo_response(question, data):
    """Generate demo responses based on question keywords"""
    import numpy as np
    import re

    question_lower = question.lower()

    # Top donors question
    if any(word in question_lower for word in ['top donor', 'biggest donor', 'megadonor', 'richest']):
        if 'donors' in data and not data['donors'].empty:
            df_donors = data['donors']
            if 'TOTAL_CONTRIB' in df_donors.columns and 'NAME_CLEAN' in df_donors.columns:
                top_5 = df_donors.nlargest(5, 'TOTAL_CONTRIB')[['NAME_CLEAN', 'TOTAL_CONTRIB', 'STATE']]

                response = "**Top 5 Donors by Total Contributions:**\n\n"
                for idx, row in top_5.iterrows():
                    response += f"{top_5.index.get_loc(idx) + 1}. **{row['NAME_CLEAN']}** - ${row['TOTAL_CONTRIB'] / 1e6:.1f}M"
                    if 'STATE' in row and pd.notna(row['STATE']):
                        response += f" ({row['STATE']})"
                    response += "\n"

                return response

    # Party spending question
    elif any(word in question_lower for word in ['democrat', 'republican', 'party', 'dem vs rep']):
        if 'candidates' in data and not data['candidates'].empty:
            df_cand = data['candidates']
            if 'CAND_PTY_AFFILIATION' in df_cand.columns and 'TTL_DISB' in df_cand.columns:
                party_totals = df_cand.groupby('CAND_PTY_AFFILIATION')['TTL_DISB'].sum().sort_values(ascending=False).head(5)

                response = "**Campaign Spending by Party:**\n\n"
                for party, total in party_totals.items():
                    response += f"- **{party}**: ${total / 1e9:.2f}B\n"

                return response

    # State question
    elif 'state' in question_lower:
        if 'candidates' in data and not data['candidates'].empty:
            df_cand = data['candidates']
            if 'CAND_OFFICE_ST' in df_cand.columns and 'TTL_DISB' in df_cand.columns:
                state_totals = df_cand.groupby('CAND_OFFICE_ST')['TTL_DISB'].sum().sort_values(ascending=False).head(10)

                response = "**Top 10 States by Campaign Spending:**\n\n"
                for state, total in state_totals.items():
                    response += f"- **{state}**: ${total / 1e9:.2f}B\n"

                return response

    # Gini coefficient question
    elif 'gini' in question_lower or 'inequality' in question_lower:
        if 'donors' in data and not data['donors'].empty:
            df_donors = data['donors']
            if 'TOTAL_CONTRIB' in df_donors.columns:
                # Calculate Gini
                sorted_values = np.sort(df_donors['TOTAL_CONTRIB'].values)
                n = len(sorted_values)
                index = np.arange(1, n + 1)
                gini = (2 * np.sum(index * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n

                response = f"""**Wealth Distribution Analysis:**

- **Gini Coefficient**: {gini:.4f}
- **Interpretation**: {'Extreme inequality' if gini > 0.9 else 'High inequality' if gini > 0.7 else 'Moderate inequality'}

The Gini coefficient measures wealth concentration on a scale from 0 (perfect equality) to 1 (perfect inequality). A value of {gini:.4f} indicates that campaign finance contributions are highly concentrated among a small number of wealthy donors.
"""
                return response

    # Candidate spending question
    elif 'candidate' in question_lower and any(word in question_lower for word in ['spent', 'spending', 'raised']):
        if 'candidates' in data and not data['candidates'].empty:
            df_cand = data['candidates']
            if 'TTL_DISB' in df_cand.columns and 'CAND_NAME' in df_cand.columns:
                # Extract threshold if mentioned
                numbers = re.findall(r'\$?(\d+)[mM]', question_lower)
                threshold = int(numbers[0]) * 1e6 if numbers else 10e6  # Default $10M

                high_spenders = df_cand[df_cand['TTL_DISB'] >= threshold].nlargest(10, 'TTL_DISB')

                response = f"**Candidates with spending over ${threshold / 1e6:.0f}M:**\n\n"
                if len(high_spenders) > 0:
                    for idx, row in high_spenders.iterrows():
                        response += f"- **{row['CAND_NAME']}**: ${row['TTL_DISB'] / 1e6:.1f}M"
                        if 'OFFICE_NAME' in row:
                            response += f" ({row['OFFICE_NAME']})"
                        response += "\n"
                else:
                    response = f"No candidates found with spending over ${threshold / 1e6:.0f}M in the filtered data."

                return response

    # Super PAC question
    elif 'super pac' in question_lower or 'committee type' in question_lower:
        if 'committees' in data and not data['committees'].empty:
            df_comm = data['committees']
            if 'CATEGORY' in df_comm.columns:
                category_counts = df_comm['CATEGORY'].value_counts()

                response = "**Committee Distribution by Category:**\n\n"
                for category, count in category_counts.items():
                    response += f"- **{category}**: {count:,} committees\n"

                return response

    # Default response
    return f"""**Question received:** {question}

🔧 **Demo Mode Response**

I understand you're asking about: *{question}*

To get a detailed AI-powered answer, you can:
1. Switch to OpenAI or Anthropic in the sidebar and provide an API key
2. Browse the other dashboard pages for interactive visualizations:
   - **Committee Analysis**: Explore 12,370+ PACs and committees
   - **Candidate Analysis**: Analyze 3,861 federal candidates
   - **Oligarchy Analysis**: Deep dive into donor concentration
   - **Hypothesis Testing**: Statistical analysis of campaign finance patterns

**Available Data:**
- {len(data.get('committees', [])):,} committees
- {len(data.get('candidates', [])):,} candidates
- {len(data.get('donors', [])):,} donors
- ${data.get('totals', pd.DataFrame()).get('Amount', [0])[0] / 1e9:.2f}B total spending
"""

# Page header
st.title("🤖 AI Chat Assistant")
st.markdown("**Ask questions about campaign finance data in natural language**")
st.markdown("---")

# Sidebar - Configuration
st.sidebar.header("⚙️ Configuration")

# API provider selection
api_provider = st.sidebar.radio(
    "AI Provider",
    ["Demo Mode (No API)", "OpenAI", "Anthropic", "Google Gemini"],
    help="Select AI provider. Demo mode provides example responses without API keys."
)

# API key input
api_key = None

if api_provider != "Demo Mode (No API)":
    st.sidebar.markdown(f"### 🔑 {api_provider} API Key")

    # Key input method selection
    key_input_method = st.sidebar.radio(
        "Input Method",
        ["Paste Key", "Upload File"],
        horizontal=True,
        help="Choose how to provide your API key"
    )

    if key_input_method == "Paste Key":
        # Direct text input
        api_key = st.sidebar.text_input(
            "Paste API Key",
            type="password",
            help=f"Paste your {api_provider} API key here",
            placeholder=f"sk-... or AIza... or other API key format"
        )
    else:
        # File upload
        uploaded_file = st.sidebar.file_uploader(
            "Upload Key File",
            type=["txt", "key", "json"],
            help="Upload a text file containing your API key (first line will be used)"
        )

        if uploaded_file is not None:
            try:
                # Read the file
                file_content = uploaded_file.read().decode("utf-8").strip()

                # Check if it's JSON (for service account keys)
                if uploaded_file.name.endswith('.json'):
                    import json
                    try:
                        key_data = json.loads(file_content)
                        # For Google service accounts
                        if 'private_key' in key_data:
                            api_key = key_data.get('private_key')
                            st.sidebar.success("✅ Extracted key from JSON service account file")
                        # For other JSON key files
                        elif 'api_key' in key_data:
                            api_key = key_data.get('api_key')
                            st.sidebar.success("✅ Extracted API key from JSON")
                        else:
                            # Use entire JSON as key
                            api_key = file_content
                            st.sidebar.success("✅ Loaded JSON key file")
                    except json.JSONDecodeError:
                        # Not valid JSON, treat as plain text
                        api_key = file_content.split('\n')[0]
                        st.sidebar.success("✅ Loaded key from file")
                else:
                    # Plain text file - use first line
                    api_key = file_content.split('\n')[0]
                    st.sidebar.success("✅ Loaded key from file")

            except Exception as e:
                st.sidebar.error(f"❌ Error reading file: {str(e)}")
                api_key = None

    # Show key status
    if api_key:
        # Mask the key for display
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        st.sidebar.caption(f"🔐 Key loaded: `{masked_key}`")
    else:
        st.sidebar.warning("⚠️ No API key provided")
else:
    api_key = None

# Data summary in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Summary")

if data:
    st.sidebar.metric("Committees", f"{len(data.get('committees', [])):,}")
    st.sidebar.metric("Candidates", f"{len(data.get('candidates', [])):,}")
    st.sidebar.metric("Donors", f"{len(data.get('donors', [])):,}")

    if 'totals' in data and not data['totals'].empty:
        total_row = data['totals'][data['totals']['Metric'] == 'Total Disbursements']
        if not total_row.empty:
            total_spending = total_row['Amount'].values[0]
            st.sidebar.metric("Total Spending", f"${total_spending / 1e9:.2f}B")

# Main chat interface
st.markdown("### 💬 Chat Interface")

# Example questions
st.markdown("#### 📝 Example Questions")
col1, col2, col3 = st.columns(3)

example_questions = [
    "Who are the top 5 donors?",
    "What is the total spending by Democrats vs Republicans?",
    "Which states have the most Super PAC spending?",
    "Show me candidates who spent over $50M",
    "What is the Gini coefficient for donor wealth distribution?",
    "How many committees are Super PACs?"
]

for idx, question in enumerate(example_questions[:3]):
    with col1 if idx == 0 else col2 if idx == 1 else col3:
        if st.button(question, key=f"ex{idx}", use_container_width=True):
            st.session_state['current_question'] = question

for idx, question in enumerate(example_questions[3:], start=3):
    with col1 if idx == 3 else col2 if idx == 4 else col3:
        if st.button(question, key=f"ex{idx}", use_container_width=True):
            st.session_state['current_question'] = question

st.markdown("---")

# Chat input
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'current_question' not in st.session_state:
    st.session_state['current_question'] = ""

# User input
user_question = st.text_input(
    "Ask a question about campaign finance:",
    value=st.session_state.get('current_question', ''),
    placeholder="e.g., Who are the top megadonors? What is the average campaign spending?"
)

# Clear example question after loading
if st.session_state.get('current_question'):
    st.session_state['current_question'] = ""

# Process question
if st.button("🔍 Ask", type="primary") and user_question:
    with st.spinner("Analyzing data..."):
        # Demo mode responses
        if api_provider == "Demo Mode (No API)":
            # Generate demo responses based on actual data
            response = generate_demo_response(user_question, data)
        elif api_key:
            # Call actual API (placeholder for now)
            response = f"🔧 API integration coming soon!\n\n**Your question:** {user_question}\n\n*To enable real AI responses, implement OpenAI or Anthropic API calls in this section.*"
        else:
            response = "⚠️ Please enter an API key or switch to Demo Mode."

        # Add to chat history
        st.session_state['chat_history'].append({
            'question': user_question,
            'response': response
        })

# Display chat history (reverse order - newest first)
if st.session_state['chat_history']:
    st.markdown("### 📜 Chat History")

    for idx, chat in enumerate(reversed(st.session_state['chat_history'])):
        with st.container():
            col1, col2 = st.columns([1, 20])
            with col1:
                st.markdown("**👤**")
            with col2:
                st.markdown(f"**Question:** {chat['question']}")

            col1, col2 = st.columns([1, 20])
            with col1:
                st.markdown("**🤖**")
            with col2:
                st.markdown(chat['response'])

            st.markdown("---")

    # Clear history button
    if st.button("🗑️ Clear Chat History"):
        st.session_state['chat_history'] = []
        st.rerun()

else:
    st.info("💡 Ask a question above or click an example question to get started!")

# Footer
st.markdown("---")
st.caption("🤖 AI Chat Assistant | Campaign Finance Analysis Dashboard")
st.caption("""
**API Key Sources:**
- **OpenAI**: Get your API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: Get your API key at [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
- **Google Gemini**: Get your API key at [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- **Demo Mode**: No API key needed - provides intelligent responses using actual campaign finance data
""")
