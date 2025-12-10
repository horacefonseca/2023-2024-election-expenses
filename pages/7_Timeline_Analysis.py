"""
Timeline Analysis Dashboard
Temporal donation patterns across the 2023-2024 election cycle
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import load_all_data

# Page config
st.set_page_config(page_title="Timeline Analysis", page_icon="⏰", layout="wide")

# Load data
@st.cache_data
def load_data():
    return load_all_data()

data = load_data()
df_donors = data.get('donors', pd.DataFrame())
df_candidates = data.get('candidates', pd.DataFrame())
df_committees = data.get('committees', pd.DataFrame())

# Helper function to add quarter column
def add_quarter_info(df, date_col):
    """Add quarter and month columns based on date column"""
    if date_col not in df.columns:
        return df

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

    # Extract quarter and month
    df['QUARTER'] = df[date_col].dt.quarter
    df['MONTH'] = df[date_col].dt.month
    df['MONTH_NAME'] = df[date_col].dt.strftime('%Y-%m')
    df['YEAR'] = df[date_col].dt.year

    # Label quarters
    df['QUARTER_LABEL'] = df['QUARTER'].apply(lambda x: f'Q{int(x)}' if pd.notna(x) else 'Unknown')

    # Primary vs General election period
    df['PERIOD'] = df['QUARTER'].apply(lambda x: 'Primary (Q1-Q2)' if x in [1, 2] else 'General (Q3-Q4)' if x in [3, 4] else 'Unknown')

    return df

# Add quarter info to donors
if 'FIRST_CONTRIB_DATE' in df_donors.columns:
    df_donors = add_quarter_info(df_donors, 'FIRST_CONTRIB_DATE')

# Page header
st.title("⏰ Timeline Analysis")
st.markdown("**When Does Money Flow? Temporal Donation Patterns Across the Election Cycle**")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Donor tier filter
if 'DONOR_TIER' in df_donors.columns:
    tiers = ['All'] + ['Mega', 'Major', 'Significant', 'Small', 'Nano']
    selected_tiers = st.sidebar.multiselect(
        "Donor Tiers",
        tiers[1:],
        default=tiers[1:]
    )
else:
    selected_tiers = []

# State filter
if 'STATE' in df_donors.columns:
    states = ['All'] + sorted(df_donors['STATE'].dropna().unique().tolist())
    selected_state = st.sidebar.selectbox("State", states)
else:
    selected_state = 'All'

# Apply filters
df_filtered = df_donors.copy()

if selected_tiers and 'DONOR_TIER' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['DONOR_TIER'].isin(selected_tiers)]

if selected_state != 'All' and 'STATE' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['STATE'] == selected_state]

# Summary metrics
st.markdown("### 📊 Timeline Metrics")

if 'QUARTER' in df_filtered.columns and 'TOTAL_CONTRIB' in df_filtered.columns:
    # Calculate quarterly totals
    q1_q2 = df_filtered[df_filtered['QUARTER'].isin([1, 2])]['TOTAL_CONTRIB'].sum()
    q3_q4 = df_filtered[df_filtered['QUARTER'].isin([3, 4])]['TOTAL_CONTRIB'].sum()
    total_contrib = df_filtered['TOTAL_CONTRIB'].sum()

    q4_only = df_filtered[df_filtered['QUARTER'] == 4]['TOTAL_CONTRIB'].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        q1_q2_pct = (q1_q2 / total_contrib * 100) if total_contrib > 0 else 0
        st.metric(
            "Q1-Q2 (Primary Period)",
            f"${q1_q2 / 1e9:.2f}B",
            delta=f"{q1_q2_pct:.1f}% of total"
        )

    with col2:
        q3_q4_pct = (q3_q4 / total_contrib * 100) if total_contrib > 0 else 0
        st.metric(
            "Q3-Q4 (General Period)",
            f"${q3_q4 / 1e9:.2f}B",
            delta=f"{q3_q4_pct:.1f}% of total"
        )

    with col3:
        q4_concentration = (q4_only / total_contrib * 100) if total_contrib > 0 else 0
        st.metric(
            "Q4 Concentration",
            f"{q4_concentration:.1f}%",
            delta="Late-cycle surge"
        )

    with col4:
        # Count donors with Q4 concentration > 50%
        if 'Q4_CONCENTRATION' in df_filtered.columns:
            late_cycle_donors = len(df_filtered[df_filtered['Q4_CONCENTRATION'] > 0.5])
            late_cycle_pct = (late_cycle_donors / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
            st.metric(
                "Late-Cycle Donors",
                f"{late_cycle_donors:,}",
                delta=f"{late_cycle_pct:.1f}% >50% in Q4"
            )
        else:
            st.metric("Late-Cycle Donors", "N/A")
else:
    st.info("Date information not available for timeline analysis")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Quarterly Timeline",
    "📈 Monthly Trends",
    "⚡ Strategic Timing",
    "👥 Donor Behavior"
])

with tab1:
    st.markdown("### Quarterly Donation Patterns")

    if 'QUARTER' in df_filtered.columns and 'TOTAL_CONTRIB' in df_filtered.columns:
        col1, col2 = st.columns(2)

        with col1:
            # Quarterly totals bar chart
            quarterly_totals = df_filtered.groupby('QUARTER_LABEL').agg({
                'TOTAL_CONTRIB': 'sum',
                'DONOR_KEY': 'count'
            }).reset_index()
            quarterly_totals.columns = ['Quarter', 'Total_Contributions', 'Donor_Count']

            # Sort by quarter
            quarter_order = ['Q1', 'Q2', 'Q3', 'Q4']
            quarterly_totals['Quarter'] = pd.Categorical(quarterly_totals['Quarter'], categories=quarter_order, ordered=True)
            quarterly_totals = quarterly_totals.sort_values('Quarter')

            fig = px.bar(
                quarterly_totals,
                x='Quarter',
                y='Total_Contributions',
                title='Total Contributions by Quarter',
                labels={'Total_Contributions': 'Total Contributions ($)', 'Quarter': 'Quarter'},
                color='Total_Contributions',
                color_continuous_scale='Blues',
                text='Total_Contributions',
                hover_data=['Donor_Count']
            )
            fig.update_traces(texttemplate='$%{text:.2s}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Primary vs General period comparison
            period_totals = df_filtered.groupby('PERIOD')['TOTAL_CONTRIB'].sum().reset_index()
            period_totals = period_totals[period_totals['PERIOD'] != 'Unknown']

            fig = px.pie(
                period_totals,
                values='TOTAL_CONTRIB',
                names='PERIOD',
                title='Primary vs General Election Funding',
                color='PERIOD',
                color_discrete_map={
                    'Primary (Q1-Q2)': '#1f77b4',
                    'General (Q3-Q4)': '#ff7f0e'
                }
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Donor tier by quarter (stacked bar)
        st.markdown("#### Donor Tier Contributions by Quarter")
        if 'DONOR_TIER' in df_filtered.columns:
            tier_quarter = df_filtered.groupby(['QUARTER_LABEL', 'DONOR_TIER'])['TOTAL_CONTRIB'].sum().reset_index()
            tier_quarter['QUARTER_LABEL'] = pd.Categorical(tier_quarter['QUARTER_LABEL'], categories=quarter_order, ordered=True)
            tier_quarter = tier_quarter.sort_values('QUARTER_LABEL')

            fig = px.bar(
                tier_quarter,
                x='QUARTER_LABEL',
                y='TOTAL_CONTRIB',
                color='DONOR_TIER',
                title='Contribution Breakdown by Donor Tier and Quarter',
                labels={'TOTAL_CONTRIB': 'Total Contributions ($)', 'QUARTER_LABEL': 'Quarter'},
                color_discrete_map={
                    'Mega': '#d62728',
                    'Major': '#ff7f0e',
                    'Significant': '#2ca02c',
                    'Small': '#1f77b4',
                    'Nano': '#9467bd'
                },
                barmode='stack'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Quarterly statistics table
        st.markdown("#### Quarterly Statistics Summary")
        quarterly_stats = df_filtered.groupby('QUARTER_LABEL').agg({
            'DONOR_KEY': 'count',
            'TOTAL_CONTRIB': ['sum', 'mean', 'median'],
            'NUM_COMMITTEES': 'mean' if 'NUM_COMMITTEES' in df_filtered.columns else 'count'
        }).reset_index()

        quarterly_stats.columns = ['Quarter', 'Donor_Count', 'Total_Contrib', 'Avg_Contrib', 'Median_Contrib', 'Avg_Committees']
        quarterly_stats['Quarter'] = pd.Categorical(quarterly_stats['Quarter'], categories=quarter_order, ordered=True)
        quarterly_stats = quarterly_stats.sort_values('Quarter')

        # Format for display
        display_stats = quarterly_stats.copy()
        display_stats['Total_Contrib'] = display_stats['Total_Contrib'].apply(lambda x: f"${x / 1e9:.2f}B")
        display_stats['Avg_Contrib'] = display_stats['Avg_Contrib'].apply(lambda x: f"${x:,.0f}")
        display_stats['Median_Contrib'] = display_stats['Median_Contrib'].apply(lambda x: f"${x:,.0f}")
        display_stats['Avg_Committees'] = display_stats['Avg_Committees'].apply(lambda x: f"{x:.1f}")

        st.dataframe(display_stats, use_container_width=True, hide_index=True)

    else:
        st.info("Quarter information not available. Add FIRST_CONTRIB_DATE to enable quarterly analysis.")

with tab2:
    st.markdown("### Monthly Donation Trends")

    if 'MONTH_NAME' in df_filtered.columns and 'TOTAL_CONTRIB' in df_filtered.columns:
        # Monthly totals line chart
        monthly_totals = df_filtered.groupby('MONTH_NAME').agg({
            'TOTAL_CONTRIB': 'sum',
            'DONOR_KEY': 'count'
        }).reset_index()
        monthly_totals.columns = ['Month', 'Total_Contributions', 'Donor_Count']
        monthly_totals = monthly_totals.sort_values('Month')

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=monthly_totals['Month'],
            y=monthly_totals['Total_Contributions'],
            mode='lines+markers',
            name='Monthly Contributions',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)'
        ))

        fig.update_layout(
            title='Monthly Contribution Timeline',
            xaxis_title='Month',
            yaxis_title='Total Contributions ($)',
            height=400,
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            # Cumulative contributions over time
            monthly_totals['Cumulative'] = monthly_totals['Total_Contributions'].cumsum()

            fig = px.area(
                monthly_totals,
                x='Month',
                y='Cumulative',
                title='Cumulative Contributions Over Time',
                labels={'Cumulative': 'Cumulative Contributions ($)', 'Month': 'Month'},
                color_discrete_sequence=['#2ca02c']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Month-over-month growth rate
            monthly_totals['Growth_Rate'] = monthly_totals['Total_Contributions'].pct_change() * 100

            fig = px.bar(
                monthly_totals[1:],  # Skip first month (no prior month to compare)
                x='Month',
                y='Growth_Rate',
                title='Month-over-Month Growth Rate',
                labels={'Growth_Rate': 'Growth Rate (%)', 'Month': 'Month'},
                color='Growth_Rate',
                color_continuous_scale='RdYlGn',
                color_continuous_midpoint=0
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        # Monthly heatmap by donor tier
        if 'DONOR_TIER' in df_filtered.columns:
            st.markdown("#### Monthly Contribution Heatmap by Donor Tier")

            tier_month_pivot = df_filtered.groupby(['MONTH_NAME', 'DONOR_TIER'])['TOTAL_CONTRIB'].sum().reset_index()
            tier_month_pivot = tier_month_pivot.pivot(index='DONOR_TIER', columns='MONTH_NAME', values='TOTAL_CONTRIB')

            # Order tiers
            tier_order_list = ['Mega', 'Major', 'Significant', 'Small', 'Nano']
            tier_month_pivot = tier_month_pivot.reindex([t for t in tier_order_list if t in tier_month_pivot.index])

            fig = px.imshow(
                tier_month_pivot,
                labels=dict(x="Month", y="Donor Tier", color="Contributions ($)"),
                title="Donor Tier Activity Heatmap (by Month)",
                color_continuous_scale='YlOrRd',
                aspect='auto'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Monthly data not available. Add date fields to enable monthly trend analysis.")

with tab3:
    st.markdown("### Strategic Timing Patterns")

    if 'Q4_CONCENTRATION' in df_filtered.columns:
        col1, col2 = st.columns(2)

        with col1:
            # Q4 concentration distribution
            fig = px.histogram(
                df_filtered,
                x='Q4_CONCENTRATION',
                nbins=30,
                title='Q4 Concentration Distribution',
                labels={'Q4_CONCENTRATION': 'Q4 Concentration (% of total in Q4)'},
                color_discrete_sequence=['#ff7f0e']
            )

            # Add vertical line at 0.25 (equal distribution)
            fig.add_vline(x=0.25, line_dash="dash", line_color="gray", annotation_text="Equal (25%)")
            # Add vertical line at 0.50 (late-cycle dependent)
            fig.add_vline(x=0.50, line_dash="dash", line_color="red", annotation_text="Late-Cycle (50%)")

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Late-cycle donors by tier
            if 'DONOR_TIER' in df_filtered.columns:
                late_cycle_tiers = df_filtered[df_filtered['Q4_CONCENTRATION'] > 0.5].groupby('DONOR_TIER').size().reset_index(name='Count')

                fig = px.bar(
                    late_cycle_tiers,
                    x='DONOR_TIER',
                    y='Count',
                    title='Late-Cycle Donors (>50% in Q4) by Tier',
                    labels={'Count': 'Number of Donors', 'DONOR_TIER': 'Donor Tier'},
                    color='DONOR_TIER',
                    color_discrete_map={
                        'Mega': '#d62728',
                        'Major': '#ff7f0e',
                        'Significant': '#2ca02c',
                        'Small': '#1f77b4',
                        'Nano': '#9467bd'
                    }
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        # Top 20 late-cycle surge donors
        st.markdown("#### Top 20 Late-Cycle Surge Donors")
        top_late_cycle = df_filtered.nlargest(20, 'Q4_CONCENTRATION')[
            ['NAME_CLEAN', 'TOTAL_CONTRIB', 'Q4_CONCENTRATION', 'DONOR_TIER', 'STATE']
        ].copy()

        top_late_cycle['Q4_Percentage'] = (top_late_cycle['Q4_CONCENTRATION'] * 100).apply(lambda x: f"{x:.1f}%")
        top_late_cycle['Total_Contrib_Formatted'] = top_late_cycle['TOTAL_CONTRIB'].apply(lambda x: f"${x:,.0f}")

        display_cols = ['NAME_CLEAN', 'Total_Contrib_Formatted', 'Q4_Percentage', 'DONOR_TIER', 'STATE']
        st.dataframe(
            top_late_cycle[display_cols].rename(columns={
                'NAME_CLEAN': 'Donor',
                'Total_Contrib_Formatted': 'Total Contrib',
                'Q4_Percentage': 'Q4 %',
                'DONOR_TIER': 'Tier',
                'STATE': 'State'
            }),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Q4 concentration data not available.")

    # Early vs Late money scatter plot
    if 'QUARTER' in df_filtered.columns and 'TOTAL_CONTRIB' in df_filtered.columns:
        st.markdown("#### Early Money vs Late Money Analysis")
        st.caption("Comparing Q1-Q2 (Primary) funding vs Q3-Q4 (General) funding for donors")

        # Calculate Q1-Q2 and Q3-Q4 totals per donor
        early_late_df = df_filtered.groupby('DONOR_KEY').agg({
            'TOTAL_CONTRIB': 'sum',
            'DONOR_TIER': 'first',
            'NAME_CLEAN': 'first'
        }).reset_index()

        # This would require transaction-level data to properly split
        # For now, we'll use Q4_CONCENTRATION as a proxy
        if 'Q4_CONCENTRATION' in df_filtered.columns:
            early_late_summary = df_filtered.groupby('DONOR_TIER').agg({
                'Q4_CONCENTRATION': 'mean',
                'DONOR_KEY': 'count'
            }).reset_index()
            early_late_summary.columns = ['Tier', 'Avg_Q4_Concentration', 'Count']

            fig = px.bar(
                early_late_summary,
                x='Tier',
                y='Avg_Q4_Concentration',
                title='Average Q4 Concentration by Donor Tier',
                labels={'Avg_Q4_Concentration': 'Average % of Contributions in Q4', 'Tier': 'Donor Tier'},
                color='Tier',
                color_discrete_map={
                    'Mega': '#d62728',
                    'Major': '#ff7f0e',
                    'Significant': '#2ca02c',
                    'Small': '#1f77b4',
                    'Nano': '#9467bd'
                },
                text='Avg_Q4_Concentration'
            )
            fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            fig.add_hline(y=0.25, line_dash="dash", line_color="gray", annotation_text="Equal distribution (25%)")
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### Donor Timeline Behavior")

    if 'DONOR_TIER' in df_filtered.columns and 'QUARTER' in df_filtered.columns:
        # Donor tier engagement over quarters (stacked area)
        tier_quarter_engagement = df_filtered.groupby(['QUARTER_LABEL', 'DONOR_TIER']).agg({
            'DONOR_KEY': 'count',
            'TOTAL_CONTRIB': 'sum'
        }).reset_index()
        tier_quarter_engagement.columns = ['Quarter', 'Tier', 'Donor_Count', 'Total_Contrib']

        quarter_order = ['Q1', 'Q2', 'Q3', 'Q4']
        tier_quarter_engagement['Quarter'] = pd.Categorical(tier_quarter_engagement['Quarter'], categories=quarter_order, ordered=True)
        tier_quarter_engagement = tier_quarter_engagement.sort_values('Quarter')

        col1, col2 = st.columns(2)

        with col1:
            # Stacked area chart - donor count
            fig = px.area(
                tier_quarter_engagement,
                x='Quarter',
                y='Donor_Count',
                color='Tier',
                title='Donor Engagement Timeline (Count)',
                labels={'Donor_Count': 'Number of Donors', 'Quarter': 'Quarter'},
                color_discrete_map={
                    'Mega': '#d62728',
                    'Major': '#ff7f0e',
                    'Significant': '#2ca02c',
                    'Small': '#1f77b4',
                    'Nano': '#9467bd'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Stacked area chart - contribution amount
            fig = px.area(
                tier_quarter_engagement,
                x='Quarter',
                y='Total_Contrib',
                color='Tier',
                title='Donor Engagement Timeline (Contributions)',
                labels={'Total_Contrib': 'Total Contributions ($)', 'Quarter': 'Quarter'},
                color_discrete_map={
                    'Mega': '#d62728',
                    'Major': '#ff7f0e',
                    'Significant': '#2ca02c',
                    'Small': '#1f77b4',
                    'Nano': '#9467bd'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Average transaction size over time
    if 'MONTH_NAME' in df_filtered.columns and 'AVG_TRANSACTION' in df_filtered.columns:
        st.markdown("#### Average Transaction Size Over Time")

        if 'DONOR_TIER' in df_filtered.columns:
            avg_transaction_timeline = df_filtered.groupby(['MONTH_NAME', 'DONOR_TIER'])['AVG_TRANSACTION'].mean().reset_index()
            avg_transaction_timeline = avg_transaction_timeline.sort_values('MONTH_NAME')

            fig = px.line(
                avg_transaction_timeline,
                x='MONTH_NAME',
                y='AVG_TRANSACTION',
                color='DONOR_TIER',
                title='Average Transaction Size by Month and Donor Tier',
                labels={'AVG_TRANSACTION': 'Average Transaction ($)', 'MONTH_NAME': 'Month'},
                color_discrete_map={
                    'Mega': '#d62728',
                    'Major': '#ff7f0e',
                    'Significant': '#2ca02c',
                    'Small': '#1f77b4',
                    'Nano': '#9467bd'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            monthly_avg = df_filtered.groupby('MONTH_NAME')['AVG_TRANSACTION'].mean().reset_index()
            monthly_avg = monthly_avg.sort_values('MONTH_NAME')

            fig = px.line(
                monthly_avg,
                x='MONTH_NAME',
                y='AVG_TRANSACTION',
                title='Average Transaction Size Over Time',
                labels={'AVG_TRANSACTION': 'Average Transaction ($)', 'MONTH_NAME': 'Month'},
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Geographic timeline (if state data available)
    if 'STATE' in df_filtered.columns and 'QUARTER' in df_filtered.columns:
        st.markdown("#### Geographic Timeline Heatmap")

        # Top 20 states
        top_states = df_filtered.groupby('STATE')['TOTAL_CONTRIB'].sum().nlargest(20).index.tolist()
        state_quarter_df = df_filtered[df_filtered['STATE'].isin(top_states)]

        state_quarter_pivot = state_quarter_df.groupby(['STATE', 'QUARTER_LABEL'])['TOTAL_CONTRIB'].sum().reset_index()
        state_quarter_pivot = state_quarter_pivot.pivot(index='STATE', columns='QUARTER_LABEL', values='TOTAL_CONTRIB')

        # Reorder columns by quarter
        quarter_order = ['Q1', 'Q2', 'Q3', 'Q4']
        state_quarter_pivot = state_quarter_pivot[[q for q in quarter_order if q in state_quarter_pivot.columns]]

        fig = px.imshow(
            state_quarter_pivot,
            labels=dict(x="Quarter", y="State", color="Contributions ($)"),
            title="Top 20 States - Quarterly Contribution Heatmap",
            color_continuous_scale='Viridis',
            aspect='auto'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

# Download button
st.markdown("---")
if not df_filtered.empty:
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Timeline Data (CSV)",
        data=csv,
        file_name="timeline_analysis_filtered.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption("⏰ Timeline Analysis | Campaign Finance Dashboard")
st.caption("Data Source: FEC Individual Contributions (itcont.txt) | Analyzes donation timing patterns across 2023-2024 election cycle")
