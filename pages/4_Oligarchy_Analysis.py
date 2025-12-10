"""
Oligarchy Analysis Dashboard
Deep dive into donor concentration, inequality, and oligarchic patterns in campaign finance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_data

# Page config
st.set_page_config(page_title="Oligarchy Analysis", page_icon="👑", layout="wide")

# Load data
@st.cache_data
def load_data():
    return load_all_data()

data = load_data()
df_donors = data.get('donors', pd.DataFrame())

# Page header
st.title("👑 Oligarchy Analysis")
st.markdown("**Examining Wealth Concentration and Oligarchic Patterns in Campaign Finance**")
st.markdown("*Analysis of 110,664+ donors contributing $4.29B to Super PACs*")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Donor tier filter
if 'DONOR_TIER' in df_donors.columns:
    tiers = ['All'] + ['Mega', 'Major', 'Significant', 'Small', 'Nano']
    selected_tier = st.sidebar.multiselect(
        "Donor Tiers",
        tiers[1:],  # Exclude 'All'
        default=tiers[1:]  # Select all by default
    )
else:
    selected_tier = []

# State filter
if 'STATE' in df_donors.columns:
    states = ['All'] + sorted(df_donors['STATE'].dropna().unique().tolist())
    selected_state = st.sidebar.selectbox("State", states)
else:
    selected_state = 'All'

# Megadonor filter
show_megadonors_only = st.sidebar.checkbox("Show Megadonors Only ($1M+)", value=False)

# Apply filters
df_filtered = df_donors.copy()

if selected_tier and 'DONOR_TIER' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['DONOR_TIER'].isin(selected_tier)]

if selected_state != 'All' and 'STATE' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['STATE'] == selected_state]

if show_megadonors_only and 'TOTAL_CONTRIB' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['TOTAL_CONTRIB'] >= 1_000_000]

# Calculate Gini coefficient
def calculate_gini(values):
    """Calculate Gini coefficient for wealth distribution"""
    if len(values) == 0:
        return 0
    sorted_values = np.sort(values)
    n = len(sorted_values)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n

# Summary metrics
st.markdown("### 📊 Oligarchy Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if 'TOTAL_CONTRIB' in df_filtered.columns:
        gini = calculate_gini(df_filtered['TOTAL_CONTRIB'].values)
        st.metric(
            "Gini Coefficient",
            f"{gini:.4f}",
            delta="Perfect Inequality = 1.0",
            help="Measures wealth concentration. 0 = perfect equality, 1 = perfect inequality"
        )
    else:
        st.metric("Gini Coefficient", "N/A")

with col2:
    if 'DONOR_TIER' in df_filtered.columns:
        megadonor_count = len(df_filtered[df_filtered['DONOR_TIER'] == 'Mega'])
        megadonor_pct = (megadonor_count / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric(
            "Megadonors",
            f"{megadonor_count:,}",
            delta=f"{megadonor_pct:.2f}% of donors"
        )
    else:
        st.metric("Megadonors", "N/A")

with col3:
    if 'TOTAL_CONTRIB' in df_filtered.columns and 'DONOR_TIER' in df_filtered.columns:
        mega_total = df_filtered[df_filtered['DONOR_TIER'] == 'Mega']['TOTAL_CONTRIB'].sum()
        total_contrib = df_filtered['TOTAL_CONTRIB'].sum()
        mega_control = (mega_total / total_contrib * 100) if total_contrib > 0 else 0
        st.metric(
            "Megadonor Control",
            f"{mega_control:.1f}%",
            delta=f"${mega_total / 1e9:.2f}B controlled"
        )
    else:
        st.metric("Megadonor Control", "N/A")

with col4:
    if 'IS_SUPER_CONNECTED' in df_filtered.columns:
        super_connected = df_filtered['IS_SUPER_CONNECTED'].sum() if 'IS_SUPER_CONNECTED' in df_filtered.columns else 0
        st.metric(
            "Super-Connected Donors",
            f"{super_connected:,}",
            delta="10+ committees",
            help="Donors contributing to 10 or more committees"
        )
    else:
        st.metric("Super-Connected Donors", "N/A")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Wealth Concentration",
    "👑 Top Oligarchs",
    "🌐 Network Effects",
    "📊 Tier Analysis",
    "📋 Data Explorer"
])

with tab1:
    st.markdown("### Wealth Distribution and Concentration")

    col1, col2 = st.columns(2)

    with col1:
        # Lorenz curve
        if 'TOTAL_CONTRIB' in df_filtered.columns:
            sorted_contrib = np.sort(df_filtered['TOTAL_CONTRIB'].values)
            cumsum_contrib = np.cumsum(sorted_contrib)
            cumsum_contrib = cumsum_contrib / cumsum_contrib[-1]  # Normalize
            cumsum_pop = np.arange(1, len(sorted_contrib) + 1) / len(sorted_contrib)

            fig = go.Figure()

            # Lorenz curve
            fig.add_trace(go.Scatter(
                x=cumsum_pop * 100,
                y=cumsum_contrib * 100,
                mode='lines',
                name='Lorenz Curve',
                line=dict(color='red', width=3),
                fill='tonexty'
            ))

            # Equality line
            fig.add_trace(go.Scatter(
                x=[0, 100],
                y=[0, 100],
                mode='lines',
                name='Perfect Equality',
                line=dict(color='gray', dash='dash', width=2)
            ))

            fig.update_layout(
                title=f'Lorenz Curve (Gini = {gini:.4f})',
                xaxis_title='Cumulative % of Donors',
                yaxis_title='Cumulative % of Contributions',
                height=500,
                hovermode='closest'
            )

            # Add shaded inequality area
            fig.add_trace(go.Scatter(
                x=list(cumsum_pop * 100) + [100, 0],
                y=list(cumsum_contrib * 100) + [100, 0],
                fill='toself',
                fillcolor='rgba(255,0,0,0.1)',
                line=dict(color='rgba(255,0,0,0)'),
                showlegend=False,
                name='Inequality Area'
            ))

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Contribution data not available for Lorenz curve")

    with col2:
        # Top percentile control
        if 'TOTAL_CONTRIB' in df_filtered.columns:
            total = df_filtered['TOTAL_CONTRIB'].sum()
            sorted_donors = df_filtered.sort_values('TOTAL_CONTRIB', ascending=False)

            percentiles = [1, 5, 10, 25, 50]
            control_data = []

            for pct in percentiles:
                n_donors = max(1, int(len(sorted_donors) * pct / 100))
                top_contrib = sorted_donors.head(n_donors)['TOTAL_CONTRIB'].sum()
                control_pct = (top_contrib / total * 100) if total > 0 else 0
                control_data.append({
                    'Percentile': f'Top {pct}%',
                    'Control': control_pct,
                    'Amount': top_contrib
                })

            control_df = pd.DataFrame(control_data)

            fig = px.bar(
                control_df,
                x='Percentile',
                y='Control',
                title='Wealth Concentration by Top Percentiles',
                labels={'Control': '% of Total Contributions', 'Percentile': 'Donor Percentile'},
                text='Control',
                color='Control',
                color_continuous_scale='Reds'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Percentile control data not available")

    # Contribution distribution histogram
    st.markdown("#### Contribution Distribution (Log Scale)")
    if 'TOTAL_CONTRIB' in df_filtered.columns:
        fig = px.histogram(
            df_filtered[df_filtered['TOTAL_CONTRIB'] > 0],
            x='TOTAL_CONTRIB',
            nbins=50,
            title='Distribution of Contributions',
            labels={'TOTAL_CONTRIB': 'Total Contributions ($)'},
            log_x=True,
            log_y=True,
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Contribution distribution data not available")

with tab2:
    st.markdown("### Top Oligarchs (Mega Donors)")

    if 'TOTAL_CONTRIB' in df_filtered.columns and 'NAME_CLEAN' in df_filtered.columns:
        top_donors = df_filtered.nlargest(50, 'TOTAL_CONTRIB')

        col1, col2 = st.columns([2, 1])

        with col1:
            # Top 30 donors bar chart
            top_30 = top_donors.head(30)

            fig = px.bar(
                top_30,
                x='TOTAL_CONTRIB',
                y='NAME_CLEAN',
                title='Top 30 Individual Donors',
                labels={'TOTAL_CONTRIB': 'Total Contributions ($)', 'NAME_CLEAN': 'Donor'},
                orientation='h',
                color='TOTAL_CONTRIB',
                color_continuous_scale='Reds',
                hover_data=['NUM_COMMITTEES', 'NUM_TRANSACTIONS'] if 'NUM_COMMITTEES' in top_30.columns else None
            )
            fig.update_layout(
                height=800,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Top 10 donor cards
            st.markdown("#### 🏆 Top 10 Donors")
            top_10 = top_donors.head(10)

            for idx, row in top_10.iterrows():
                with st.container():
                    st.markdown(f"**#{top_10.index.get_loc(idx) + 1}. {row.get('NAME_CLEAN', 'Unknown')}**")
                    st.metric(
                        "Total Contributions",
                        f"${row.get('TOTAL_CONTRIB', 0) / 1e6:.1f}M"
                    )
                    if 'NUM_COMMITTEES' in row:
                        st.caption(f"📊 {row.get('NUM_COMMITTEES', 0)} committees | {row.get('NUM_TRANSACTIONS', 0)} transactions")
                    if 'CITY' in row and 'STATE' in row:
                        st.caption(f"📍 {row.get('CITY', 'N/A')}, {row.get('STATE', 'N/A')}")
                    st.markdown("---")
    else:
        st.info("Top donor data not available")

with tab3:
    st.markdown("### Network Effects and Super-Connected Donors")

    col1, col2 = st.columns(2)

    with col1:
        # Committee connectivity distribution
        if 'NUM_COMMITTEES' in df_filtered.columns:
            fig = px.histogram(
                df_filtered[df_filtered['NUM_COMMITTEES'] > 0],
                x='NUM_COMMITTEES',
                nbins=30,
                title='Distribution of Committee Connections',
                labels={'NUM_COMMITTEES': 'Number of Committees Supported'},
                color_discrete_sequence=['#2ca02c']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Committee connection data not available")

    with col2:
        # Average contribution by connectivity
        if 'NUM_COMMITTEES' in df_filtered.columns and 'AVG_PER_COMMITTEE' in df_filtered.columns:
            # Group by number of committees
            connectivity_groups = df_filtered.groupby('NUM_COMMITTEES').agg({
                'AVG_PER_COMMITTEE': 'mean',
                'DONOR_KEY': 'count'
            }).reset_index()
            connectivity_groups.columns = ['Num_Committees', 'Avg_Per_Committee', 'Donor_Count']
            connectivity_groups = connectivity_groups[connectivity_groups['Num_Committees'] <= 50]

            fig = px.scatter(
                connectivity_groups,
                x='Num_Committees',
                y='Avg_Per_Committee',
                size='Donor_Count',
                title='Avg Contribution vs Committee Connectivity',
                labels={
                    'Num_Committees': 'Number of Committees',
                    'Avg_Per_Committee': 'Avg Contribution per Committee ($)',
                    'Donor_Count': 'Number of Donors'
                },
                log_y=True,
                color='Donor_Count',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Connectivity analysis data not available")

    # Super-connected donors table
    st.markdown("#### Super-Connected Donors (10+ Committees)")
    if 'NUM_COMMITTEES' in df_filtered.columns:
        super_connected = df_filtered[df_filtered['NUM_COMMITTEES'] >= 10].sort_values('NUM_COMMITTEES', ascending=False)

        if not super_connected.empty:
            display_cols = ['NAME_CLEAN', 'NUM_COMMITTEES', 'TOTAL_CONTRIB', 'AVG_PER_COMMITTEE', 'STATE']
            available_cols = [col for col in display_cols if col in super_connected.columns]

            if available_cols:
                display_df = super_connected[available_cols].head(20).copy()

                # Format numeric columns
                if 'TOTAL_CONTRIB' in display_df.columns:
                    display_df['TOTAL_CONTRIB'] = display_df['TOTAL_CONTRIB'].apply(lambda x: f"${x:,.0f}")
                if 'AVG_PER_COMMITTEE' in display_df.columns:
                    display_df['AVG_PER_COMMITTEE'] = display_df['AVG_PER_COMMITTEE'].apply(lambda x: f"${x:,.0f}")

                st.dataframe(display_df, use_container_width=True, height=400)
                st.caption(f"Showing top 20 of {len(super_connected):,} super-connected donors")
            else:
                st.info("Column data not available for display")
        else:
            st.info("No super-connected donors in filtered data")
    else:
        st.info("Committee connection data not available")

with tab4:
    st.markdown("### Donor Tier Analysis")

    if 'DONOR_TIER' in df_filtered.columns:
        col1, col2 = st.columns(2)

        with col1:
            # Donor count by tier
            tier_counts = df_filtered['DONOR_TIER'].value_counts().reset_index()
            tier_counts.columns = ['Tier', 'Count']

            # Define tier order
            tier_order = ['Mega', 'Major', 'Significant', 'Small', 'Nano']
            tier_counts['Tier'] = pd.Categorical(tier_counts['Tier'], categories=tier_order, ordered=True)
            tier_counts = tier_counts.sort_values('Tier')

            fig = px.pie(
                tier_counts,
                values='Count',
                names='Tier',
                title='Donor Distribution by Tier',
                color='Tier',
                color_discrete_map={
                    'Mega': '#d62728',
                    'Major': '#ff7f0e',
                    'Significant': '#2ca02c',
                    'Small': '#1f77b4',
                    'Nano': '#9467bd'
                }
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Contribution amount by tier
            if 'TOTAL_CONTRIB' in df_filtered.columns:
                tier_amounts = df_filtered.groupby('DONOR_TIER')['TOTAL_CONTRIB'].sum().reset_index()
                tier_amounts.columns = ['Tier', 'Total']

                tier_amounts['Tier'] = pd.Categorical(tier_amounts['Tier'], categories=tier_order, ordered=True)
                tier_amounts = tier_amounts.sort_values('Tier')

                fig = px.pie(
                    tier_amounts,
                    values='Total',
                    names='Tier',
                    title='Total Contributions by Tier',
                    color='Tier',
                    color_discrete_map={
                        'Mega': '#d62728',
                        'Major': '#ff7f0e',
                        'Significant': '#2ca02c',
                        'Small': '#1f77b4',
                        'Nano': '#9467bd'
                    }
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Contribution amount data not available")

        # Tier statistics table
        st.markdown("#### Tier Statistics Summary")
        if 'TOTAL_CONTRIB' in df_filtered.columns:
            tier_stats = df_filtered.groupby('DONOR_TIER').agg({
                'DONOR_KEY': 'count',
                'TOTAL_CONTRIB': ['sum', 'mean', 'median'],
                'NUM_COMMITTEES': 'mean' if 'NUM_COMMITTEES' in df_filtered.columns else 'count'
            }).reset_index()

            tier_stats.columns = ['Tier', 'Count', 'Total_Contrib', 'Avg_Contrib', 'Median_Contrib', 'Avg_Committees']

            # Format numeric columns
            tier_stats['Total_Contrib'] = tier_stats['Total_Contrib'].apply(lambda x: f"${x / 1e9:.2f}B")
            tier_stats['Avg_Contrib'] = tier_stats['Avg_Contrib'].apply(lambda x: f"${x:,.0f}")
            tier_stats['Median_Contrib'] = tier_stats['Median_Contrib'].apply(lambda x: f"${x:,.0f}")
            tier_stats['Avg_Committees'] = tier_stats['Avg_Committees'].apply(lambda x: f"{x:.1f}")

            st.dataframe(tier_stats, use_container_width=True)
        else:
            st.info("Tier statistics not available")
    else:
        st.info("Donor tier data not available")

with tab5:
    st.markdown("### 📋 Data Explorer")

    # Search functionality
    search_term = st.text_input("🔍 Search donors by name", "")

    display_df = df_filtered.copy()

    if search_term and 'NAME_CLEAN' in display_df.columns:
        display_df = display_df[display_df['NAME_CLEAN'].str.contains(search_term, case=False, na=False)]

    # Select columns
    all_cols = display_df.columns.tolist()
    default_cols = ['NAME_CLEAN', 'DONOR_TIER', 'TOTAL_CONTRIB', 'NUM_COMMITTEES', 'STATE', 'CITY']
    available_default = [col for col in default_cols if col in all_cols]

    selected_cols = st.multiselect(
        "Select columns to display",
        all_cols,
        default=available_default if available_default else all_cols[:6]
    )

    if selected_cols:
        # Sort options
        if 'TOTAL_CONTRIB' in display_df.columns:
            sort_col = st.selectbox("Sort by", selected_cols, index=selected_cols.index('TOTAL_CONTRIB') if 'TOTAL_CONTRIB' in selected_cols else 0)
            sort_order = st.radio("Sort order", ['Descending', 'Ascending'], horizontal=True)

            display_df = display_df.sort_values(sort_col, ascending=(sort_order == 'Ascending'))

        # Format display
        formatted_df = display_df[selected_cols].head(100).copy()

        for col in formatted_df.columns:
            if col in ['TOTAL_CONTRIB', 'AVG_TRANSACTION', 'AVG_PER_COMMITTEE'] and formatted_df[col].dtype in ['float64', 'int64']:
                formatted_df[col] = formatted_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")

        st.dataframe(formatted_df, use_container_width=True, height=600)
        st.caption(f"Showing {min(100, len(display_df)):,} of {len(display_df):,} donors")
    else:
        st.warning("Please select at least one column to display")

# Download button
st.markdown("---")
if not df_filtered.empty:
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name="oligarchy_analysis_filtered.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption("Data Source: FEC Individual Contributions to Super PACs (itcont.txt) | Analysis of 110,664+ donors contributing $4.29B")
