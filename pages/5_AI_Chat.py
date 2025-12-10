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

# Page header
st.title("🤖 AI Chat Assistant")
st.markdown("**Ask questions about campaign finance data in natural language**")
st.markdown("---")

# Sidebar - Configuration
st.sidebar.header("⚙️ Configuration")

# API provider selection
api_provider = st.sidebar.radio(
    "AI Provider",
    ["Demo Mode (No API)", "OpenAI", "Anthropic"],
    help="Select AI provider. Demo mode provides example responses without API keys."
)

# API key input
if api_provider != "Demo Mode (No API)":
    api_key = st.sidebar.text_input(
        f"{api_provider} API Key",
        type="password",
        help=f"Enter your {api_provider} API key. Not required in Demo Mode."
    )
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

# Helper function for demo responses
def generate_demo_response(question, data):
    """Generate demo responses based on question keywords"""
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
                import numpy as np

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
                import re
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

# Footer
st.markdown("---")
st.caption("🤖 AI Chat Assistant | Campaign Finance Analysis Dashboard")
st.caption("Note: API integration requires OpenAI or Anthropic API keys. Demo mode provides example responses using actual data.")
