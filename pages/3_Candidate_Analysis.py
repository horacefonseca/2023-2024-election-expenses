"""
Candidate Analysis Dashboard
Interactive analysis of 3,861 candidates across House, Senate, and Presidential races
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_data

# Page config
st.set_page_config(page_title="Candidate Analysis", page_icon="🗳️", layout="wide")

# Load data
@st.cache_data
def load_data():
    return load_all_data()

data = load_data()
df_candidates = data.get('candidates', pd.DataFrame())

# Page header
st.title("🗳️ Candidate Analysis")
st.markdown("**Explore 3,861 Federal Candidates in the 2023-2024 Election Cycle**")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")
st.sidebar.markdown("*Select multiple options to compare*")

# Office filter (multi-select)
if 'OFFICE_NAME' in df_candidates.columns:
    offices = sorted(df_candidates['OFFICE_NAME'].dropna().unique().tolist())
    selected_offices = st.sidebar.multiselect(
        "Office (Multi-select)",
        offices,
        default=offices,  # All selected by default
        help="Select one or more offices to analyze"
    )
else:
    selected_offices = []

# Party filter (multi-select)
if 'CAND_PTY_AFFILIATION' in df_candidates.columns:
    parties = sorted(df_candidates['CAND_PTY_AFFILIATION'].dropna().unique().tolist())
    # Default to DEM and REP for easy comparison
    default_parties = [p for p in ['DEM', 'REP'] if p in parties]
    selected_parties = st.sidebar.multiselect(
        "Party (Multi-select)",
        parties,
        default=default_parties if default_parties else parties[:2],
        help="Select parties to compare (e.g., DEM vs REP)"
    )
else:
    selected_parties = []

# State filter (multi-select)
if 'CAND_OFFICE_ST' in df_candidates.columns:
    states = sorted(df_candidates['CAND_OFFICE_ST'].dropna().unique().tolist())
    selected_states = st.sidebar.multiselect(
        "State (Multi-select)",
        states,
        default=states,  # All selected by default
        help="Select one or more states to analyze"
    )
else:
    selected_states = []

# Incumbent/Challenger/Open filter (multi-select)
if 'CAND_ICI' in df_candidates.columns:
    ici_map = {'I': 'Incumbent', 'C': 'Challenger', 'O': 'Open Seat'}
    ici_options = list(ici_map.values())
    selected_ici_labels = st.sidebar.multiselect(
        "Status (Multi-select)",
        ici_options,
        default=ici_options,  # All selected by default
        help="Select candidate types to include"
    )
else:
    selected_ici_labels = []

# Spending range
if 'TTL_DISB' in df_candidates.columns:
    min_spending = st.sidebar.number_input(
        "Min Disbursements ($)",
        min_value=0,
        value=0,
        step=100000,
        format="%d"
    )
else:
    min_spending = 0

# Apply filters
df_filtered = df_candidates.copy()

# Office filter - use .isin() for list matching
if selected_offices and 'OFFICE_NAME' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['OFFICE_NAME'].isin(selected_offices)]

# Party filter - use .isin() for list matching
if selected_parties and 'CAND_PTY_AFFILIATION' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['CAND_PTY_AFFILIATION'].isin(selected_parties)]

# State filter - use .isin() for list matching
if selected_states and 'CAND_OFFICE_ST' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['CAND_OFFICE_ST'].isin(selected_states)]

# Status filter - convert labels back to codes and use .isin()
if selected_ici_labels and 'CAND_ICI' in df_filtered.columns:
    ici_reverse_map = {v: k for k, v in ici_map.items()}
    selected_ici_codes = [ici_reverse_map[label] for label in selected_ici_labels if label in ici_reverse_map]
    df_filtered = df_filtered[df_filtered['CAND_ICI'].isin(selected_ici_codes)]

# Spending filter
if min_spending > 0 and 'TTL_DISB' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['TTL_DISB'] >= min_spending]

# Summary metrics
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Candidates",
        f"{len(df_filtered):,}",
        delta=f"{len(df_filtered) - len(df_candidates):,}" if len(df_filtered) != len(df_candidates) else None
    )

with col2:
    if 'TTL_DISB' in df_filtered.columns:
        total_disb = df_filtered['TTL_DISB'].sum()
        st.metric(
            "Total Campaign Spending",
            f"${total_disb / 1e9:.2f}B",
            delta="Filtered View" if len(df_filtered) != len(df_candidates) else None
        )
    else:
        st.metric("Total Campaign Spending", "N/A")

with col3:
    if 'TTL_INDIV_CONTRIB' in df_filtered.columns:
        total_indiv = df_filtered['TTL_INDIV_CONTRIB'].sum()
        st.metric(
            "Individual Contributions",
            f"${total_indiv / 1e9:.2f}B",
            delta="Filtered View" if len(df_filtered) != len(df_candidates) else None
        )
    else:
        st.metric("Individual Contributions", "N/A")

with col4:
    if 'TTL_DISB' in df_filtered.columns:
        avg_spending = df_filtered['TTL_DISB'].mean()
        st.metric(
            "Avg Campaign Spending",
            f"${avg_spending / 1e6:.1f}M",
            delta="Per Candidate"
        )
    else:
        st.metric("Avg Campaign Spending", "N/A")

st.markdown("---")

# Visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Top Campaigns",
    "🎯 Party Analysis",
    "🗺️ Geographic Analysis",
    "💰 Funding Sources",
    "📋 Data Table"
])

with tab1:
    st.markdown("### Top Campaign Spenders")

    col1, col2 = st.columns(2)

    with col1:
        # Top 20 candidates by spending
        if 'TTL_DISB' in df_filtered.columns and 'CAND_NAME' in df_filtered.columns:
            top_candidates = df_filtered.nlargest(20, 'TTL_DISB')[[
                'CAND_NAME', 'TTL_DISB', 'OFFICE_NAME', 'CAND_PTY_AFFILIATION', 'CAND_OFFICE_ST'
            ]].copy()

            # Create label with office and state
            top_candidates['Label'] = top_candidates.apply(
                lambda x: f"{x['CAND_NAME']} ({x.get('CAND_OFFICE_ST', 'N/A')}-{x.get('OFFICE_NAME', 'N/A')[:3]})",
                axis=1
            )

            fig = px.bar(
                top_candidates,
                x='TTL_DISB',
                y='Label',
                color='CAND_PTY_AFFILIATION',
                orientation='h',
                title="Top 20 Candidates by Campaign Spending",
                labels={'TTL_DISB': 'Total Disbursements ($)', 'Label': 'Candidate'},
                color_discrete_map={'DEM': '#1f77b4', 'REP': '#d62728', 'OTH': '#gray'}
            )
            fig.update_layout(
                height=600,
                showlegend=True,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Candidate spending data not available")

    with col2:
        # Top fundraisers (individual contributions)
        if 'TTL_INDIV_CONTRIB' in df_filtered.columns and 'CAND_NAME' in df_filtered.columns:
            top_fundraisers = df_filtered.nlargest(20, 'TTL_INDIV_CONTRIB')[[
                'CAND_NAME', 'TTL_INDIV_CONTRIB', 'OFFICE_NAME', 'CAND_PTY_AFFILIATION', 'CAND_OFFICE_ST'
            ]].copy()

            top_fundraisers['Label'] = top_fundraisers.apply(
                lambda x: f"{x['CAND_NAME']} ({x.get('CAND_OFFICE_ST', 'N/A')}-{x.get('OFFICE_NAME', 'N/A')[:3]})",
                axis=1
            )

            fig = px.bar(
                top_fundraisers,
                x='TTL_INDIV_CONTRIB',
                y='Label',
                color='CAND_PTY_AFFILIATION',
                orientation='h',
                title="Top 20 Fundraisers (Individual Contributions)",
                labels={'TTL_INDIV_CONTRIB': 'Individual Contributions ($)', 'Label': 'Candidate'},
                color_discrete_map={'DEM': '#1f77b4', 'REP': '#d62728', 'OTH': '#gray'}
            )
            fig.update_layout(
                height=600,
                showlegend=True,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Fundraising data not available")

with tab2:
    st.markdown("### Party Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Spending by party
        if 'CAND_PTY_AFFILIATION' in df_filtered.columns and 'TTL_DISB' in df_filtered.columns:
            party_spending = df_filtered.groupby('CAND_PTY_AFFILIATION').agg({
                'TTL_DISB': 'sum',
                'CAND_ID': 'count'
            }).reset_index()
            party_spending.columns = ['Party', 'Total_Spending', 'Candidate_Count']
            party_spending = party_spending.sort_values('Total_Spending', ascending=False)

            fig = px.bar(
                party_spending,
                x='Party',
                y='Total_Spending',
                title='Total Campaign Spending by Party',
                labels={'Total_Spending': 'Total Spending ($)', 'Party': 'Party'},
                color='Party',
                color_discrete_map={'DEM': '#1f77b4', 'REP': '#d62728'},
                text='Total_Spending'
            )
            fig.update_traces(texttemplate='$%{text:.2s}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Party spending data not available")

    with col2:
        # Candidate count by party and office
        if 'CAND_PTY_AFFILIATION' in df_filtered.columns and 'OFFICE_NAME' in df_filtered.columns:
            party_office_counts = df_filtered.groupby(['OFFICE_NAME', 'CAND_PTY_AFFILIATION']).size().reset_index(name='Count')

            fig = px.bar(
                party_office_counts,
                x='OFFICE_NAME',
                y='Count',
                color='CAND_PTY_AFFILIATION',
                title='Candidate Count by Office and Party',
                labels={'Count': 'Number of Candidates', 'OFFICE_NAME': 'Office'},
                color_discrete_map={'DEM': '#1f77b4', 'REP': '#d62728'},
                barmode='group'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Office and party data not available")

    # Average spending comparison
    st.markdown("#### Average Campaign Spending by Party and Office")
    if all(col in df_filtered.columns for col in ['OFFICE_NAME', 'CAND_PTY_AFFILIATION', 'TTL_DISB']):
        avg_spending = df_filtered.groupby(['OFFICE_NAME', 'CAND_PTY_AFFILIATION'])['TTL_DISB'].mean().reset_index()

        fig = px.bar(
            avg_spending,
            x='OFFICE_NAME',
            y='TTL_DISB',
            color='CAND_PTY_AFFILIATION',
            title='Average Spending per Candidate by Office and Party',
            labels={'TTL_DISB': 'Average Spending ($)', 'OFFICE_NAME': 'Office'},
            color_discrete_map={'DEM': '#1f77b4', 'REP': '#d62728'},
            barmode='group'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Average spending data not available")

with tab3:
    st.markdown("### Geographic Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Top states by total spending
        if 'CAND_OFFICE_ST' in df_filtered.columns and 'TTL_DISB' in df_filtered.columns:
            state_spending = df_filtered.groupby('CAND_OFFICE_ST').agg({
                'TTL_DISB': 'sum',
                'CAND_ID': 'count'
            }).reset_index()
            state_spending.columns = ['State', 'Total_Spending', 'Candidate_Count']
            state_spending = state_spending.sort_values('Total_Spending', ascending=False).head(20)

            fig = px.bar(
                state_spending,
                x='State',
                y='Total_Spending',
                title='Top 20 States by Campaign Spending',
                labels={'Total_Spending': 'Total Spending ($)', 'State': 'State'},
                color='Total_Spending',
                color_continuous_scale='Viridis',
                hover_data=['Candidate_Count']
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("State spending data not available")

    with col2:
        # Candidate count by state
        if 'CAND_OFFICE_ST' in df_filtered.columns:
            state_counts = df_filtered['CAND_OFFICE_ST'].value_counts().head(20).reset_index()
            state_counts.columns = ['State', 'Count']

            fig = px.bar(
                state_counts,
                x='State',
                y='Count',
                title='Top 20 States by Candidate Count',
                labels={'Count': 'Number of Candidates', 'State': 'State'},
                color='Count',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("State data not available")

with tab4:
    st.markdown("### Funding Source Analysis")

    # Funding source breakdown (stacked bar)
    if all(col in df_filtered.columns for col in ['CAND_NAME', 'TTL_INDIV_CONTRIB', 'POL_PTY_CONTRIB', 'OTHER_POL_CMTE_CONTRIB', 'CAND_CONTRIB']):
        top_candidates_funding = df_filtered.nlargest(20, 'TTL_DISB')[[
            'CAND_NAME', 'TTL_INDIV_CONTRIB', 'POL_PTY_CONTRIB', 'OTHER_POL_CMTE_CONTRIB', 'CAND_CONTRIB', 'OFFICE_NAME'
        ]].copy()

        # Reshape for stacked bar
        funding_melted = top_candidates_funding.melt(
            id_vars=['CAND_NAME', 'OFFICE_NAME'],
            value_vars=['TTL_INDIV_CONTRIB', 'POL_PTY_CONTRIB', 'OTHER_POL_CMTE_CONTRIB', 'CAND_CONTRIB'],
            var_name='Source',
            value_name='Amount'
        )

        # Clean up source names
        funding_melted['Source'] = funding_melted['Source'].map({
            'TTL_INDIV_CONTRIB': 'Individual',
            'POL_PTY_CONTRIB': 'Party',
            'OTHER_POL_CMTE_CONTRIB': 'PACs',
            'CAND_CONTRIB': 'Self-Funded'
        })

        fig = px.bar(
            funding_melted,
            x='CAND_NAME',
            y='Amount',
            color='Source',
            title='Funding Sources for Top 20 Campaigns',
            labels={'Amount': 'Contribution Amount ($)', 'CAND_NAME': 'Candidate'},
            barmode='stack'
        )
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Funding source data not available")

    # Self-funding analysis
    col1, col2 = st.columns(2)

    with col1:
        if 'CAND_CONTRIB' in df_filtered.columns and 'CAND_NAME' in df_filtered.columns:
            self_funded = df_filtered[df_filtered['CAND_CONTRIB'] > 0].nlargest(15, 'CAND_CONTRIB')[[
                'CAND_NAME', 'CAND_CONTRIB', 'OFFICE_NAME', 'CAND_PTY_AFFILIATION'
            ]]

            fig = px.bar(
                self_funded,
                x='CAND_CONTRIB',
                y='CAND_NAME',
                color='CAND_PTY_AFFILIATION',
                orientation='h',
                title='Top 15 Self-Funded Campaigns',
                labels={'CAND_CONTRIB': 'Self-Contribution ($)', 'CAND_NAME': 'Candidate'},
                color_discrete_map={'DEM': '#1f77b4', 'REP': '#d62728'}
            )
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Self-funding data not available")

    with col2:
        if 'CAND_LOANS' in df_filtered.columns and 'CAND_NAME' in df_filtered.columns:
            loans = df_filtered[df_filtered['CAND_LOANS'] > 0].nlargest(15, 'CAND_LOANS')[[
                'CAND_NAME', 'CAND_LOANS', 'OFFICE_NAME', 'CAND_PTY_AFFILIATION'
            ]]

            fig = px.bar(
                loans,
                x='CAND_LOANS',
                y='CAND_NAME',
                color='CAND_PTY_AFFILIATION',
                orientation='h',
                title='Top 15 Campaign Loans',
                labels={'CAND_LOANS': 'Candidate Loans ($)', 'CAND_NAME': 'Candidate'},
                color_discrete_map={'DEM': '#1f77b4', 'REP': '#d62728'}
            )
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Campaign loan data not available")

with tab5:
    st.markdown("### 📋 Candidate Data Table")

    # Select columns to display
    display_cols = [
        'CAND_NAME', 'OFFICE_NAME', 'CAND_PTY_AFFILIATION', 'CAND_OFFICE_ST',
        'TTL_RECEIPTS', 'TTL_DISB', 'TTL_INDIV_CONTRIB', 'COH_COP'
    ]
    available_cols = [col for col in display_cols if col in df_filtered.columns]

    if available_cols:
        # Sort by spending
        if 'TTL_DISB' in df_filtered.columns:
            sorted_df = df_filtered.sort_values('TTL_DISB', ascending=False)[available_cols].head(100).copy()

            # Format numeric columns
            for col in ['TTL_RECEIPTS', 'TTL_DISB', 'TTL_INDIV_CONTRIB', 'COH_COP']:
                if col in sorted_df.columns:
                    sorted_df[col] = sorted_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")

            st.dataframe(sorted_df, use_container_width=True, height=600)
        else:
            st.dataframe(df_filtered[available_cols].head(100), use_container_width=True, height=600)

        st.caption(f"Showing top 100 of {len(df_filtered):,} candidates (sorted by spending)")
    else:
        st.warning("No candidate data available to display")

# Download button
st.markdown("---")
if not df_filtered.empty:
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name="candidate_analysis_filtered.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption("Data Source: FEC Bulk Data (2023-2024 Cycle) | All Candidates (weball24.txt)")
