"""
Committee Analysis Dashboard
Interactive analysis of 12,370+ PACs, Super PACs, and Party Committees
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_data

# Page config
st.set_page_config(page_title="Committee Analysis", page_icon="🏛️", layout="wide")

# Load data
@st.cache_data
def load_data():
    return load_all_data()

data = load_data()
df_committees = data.get('committees', pd.DataFrame())

# Page header
st.title("🏛️ Committee Analysis")
st.markdown("**Explore 12,370+ Political Committees in the 2023-2024 Election Cycle**")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Category filter
if 'CATEGORY' in df_committees.columns:
    categories = ['All'] + sorted(df_committees['CATEGORY'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Committee Category", categories)
else:
    selected_category = 'All'

# Committee type filter
if 'CMTE_TP_DESC' in df_committees.columns:
    types = ['All'] + sorted(df_committees['CMTE_TP_DESC'].dropna().unique().tolist())
    selected_type = st.sidebar.selectbox("Committee Type", types)
else:
    selected_type = 'All'

# Spending range filter
if 'TTL_DISB' in df_committees.columns:
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
df_filtered = df_committees.copy()

if selected_category != 'All' and 'CATEGORY' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['CATEGORY'] == selected_category]

if selected_type != 'All' and 'CMTE_TP_DESC' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['CMTE_TP_DESC'] == selected_type]

if min_spending > 0 and 'TTL_DISB' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['TTL_DISB'] >= min_spending]

# Summary metrics
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Committees",
        f"{len(df_filtered):,}",
        delta=f"{len(df_filtered) - len(df_committees):,}" if len(df_filtered) != len(df_committees) else None
    )

with col2:
    if 'TTL_DISB' in df_filtered.columns:
        total_disb = df_filtered['TTL_DISB'].sum()
        st.metric(
            "Total Disbursements",
            f"${total_disb / 1e9:.2f}B",
            delta="Filtered View" if len(df_filtered) != len(df_committees) else None
        )
    else:
        st.metric("Total Disbursements", "N/A")

with col3:
    if 'TTL_RECEIPTS' in df_filtered.columns:
        total_receipts = df_filtered['TTL_RECEIPTS'].sum()
        st.metric(
            "Total Receipts",
            f"${total_receipts / 1e9:.2f}B",
            delta="Filtered View" if len(df_filtered) != len(df_committees) else None
        )
    else:
        st.metric("Total Receipts", "N/A")

with col4:
    if 'COH_COP' in df_filtered.columns:
        total_cash = df_filtered['COH_COP'].sum()
        st.metric(
            "Cash on Hand",
            f"${total_cash / 1e9:.2f}B",
            delta="Filtered View" if len(df_filtered) != len(df_committees) else None
        )
    else:
        st.metric("Cash on Hand", "N/A")

st.markdown("---")

# Visualizations
tab1, tab2, tab3, tab4 = st.tabs(["📈 Spending Analysis", "🏦 Financial Overview", "📊 Category Breakdown", "📋 Data Table"])

with tab1:
    st.markdown("### Spending Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Top 20 committees by disbursements
        if 'TTL_DISB' in df_filtered.columns and 'CMTE_NM' in df_filtered.columns:
            top_committees = df_filtered.nlargest(20, 'TTL_DISB')[['CMTE_NM', 'TTL_DISB', 'CATEGORY']]

            fig = px.bar(
                top_committees,
                x='TTL_DISB',
                y='CMTE_NM',
                color='CATEGORY',
                orientation='h',
                title="Top 20 Committees by Disbursements",
                labels={'TTL_DISB': 'Total Disbursements ($)', 'CMTE_NM': 'Committee'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                height=600,
                showlegend=True,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Disbursement data not available")

    with col2:
        # Spending by category (pie chart)
        if 'CATEGORY' in df_filtered.columns and 'TTL_DISB' in df_filtered.columns:
            category_spending = df_filtered.groupby('CATEGORY')['TTL_DISB'].sum().reset_index()
            category_spending = category_spending.sort_values('TTL_DISB', ascending=False)

            fig = px.pie(
                category_spending,
                values='TTL_DISB',
                names='CATEGORY',
                title='Spending Distribution by Category',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category data not available")

with tab2:
    st.markdown("### Financial Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Receipts vs Disbursements scatter plot
        if 'TTL_RECEIPTS' in df_filtered.columns and 'TTL_DISB' in df_filtered.columns:
            # Sample for performance if too many committees
            plot_df = df_filtered.copy()
            if len(plot_df) > 1000:
                plot_df = plot_df.nlargest(1000, 'TTL_DISB')

            fig = px.scatter(
                plot_df,
                x='TTL_RECEIPTS',
                y='TTL_DISB',
                color='CATEGORY' if 'CATEGORY' in plot_df.columns else None,
                size='TTL_DISB',
                hover_name='CMTE_NM' if 'CMTE_NM' in plot_df.columns else None,
                title='Receipts vs Disbursements (Top 1,000)',
                labels={'TTL_RECEIPTS': 'Total Receipts ($)', 'TTL_DISB': 'Total Disbursements ($)'},
                log_x=True,
                log_y=True
            )
            # Add diagonal line (balanced budget)
            max_val = max(plot_df['TTL_RECEIPTS'].max(), plot_df['TTL_DISB'].max())
            fig.add_trace(go.Scatter(
                x=[1, max_val],
                y=[1, max_val],
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name='Balanced Budget Line',
                showlegend=True
            ))
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Financial data not available")

    with col2:
        # Cash on hand distribution
        if 'COH_COP' in df_filtered.columns and 'CATEGORY' in df_filtered.columns:
            fig = px.box(
                df_filtered[df_filtered['COH_COP'] > 0],
                x='CATEGORY',
                y='COH_COP',
                title='Cash on Hand Distribution by Category',
                labels={'COH_COP': 'Cash on Hand ($)', 'CATEGORY': 'Category'},
                log_y=True,
                color='CATEGORY',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Cash on hand data not available")

with tab3:
    st.markdown("### Category Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        # Committee count by category
        if 'CATEGORY' in df_filtered.columns:
            category_counts = df_filtered['CATEGORY'].value_counts().reset_index()
            category_counts.columns = ['CATEGORY', 'COUNT']

            fig = px.bar(
                category_counts,
                x='CATEGORY',
                y='COUNT',
                title='Committee Count by Category',
                labels={'COUNT': 'Number of Committees', 'CATEGORY': 'Category'},
                color='COUNT',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category data not available")

    with col2:
        # Average spending by type
        if 'CMTE_TP_DESC' in df_filtered.columns and 'TTL_DISB' in df_filtered.columns:
            type_avg = df_filtered.groupby('CMTE_TP_DESC').agg({
                'TTL_DISB': 'mean',
                'CMTE_ID': 'count'
            }).reset_index()
            type_avg.columns = ['Type', 'Avg_Disbursements', 'Count']
            type_avg = type_avg.sort_values('Avg_Disbursements', ascending=False)

            fig = px.bar(
                type_avg,
                x='Type',
                y='Avg_Disbursements',
                title='Average Disbursements by Committee Type',
                labels={'Avg_Disbursements': 'Average Disbursements ($)', 'Type': 'Committee Type'},
                color='Avg_Disbursements',
                color_continuous_scale='Viridis',
                hover_data=['Count']
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Committee type data not available")

    # Treemap of spending
    st.markdown("#### 🗺️ Spending Treemap (Category → Type → Committee)")
    if all(col in df_filtered.columns for col in ['CATEGORY', 'CMTE_TP_DESC', 'CMTE_NM', 'TTL_DISB']):
        # Get top 100 for performance
        top_df = df_filtered.nlargest(100, 'TTL_DISB')

        fig = px.treemap(
            top_df,
            path=['CATEGORY', 'CMTE_TP_DESC', 'CMTE_NM'],
            values='TTL_DISB',
            title='Spending Hierarchy (Top 100 Committees)',
            color='TTL_DISB',
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Hierarchical data not available for treemap")

with tab4:
    st.markdown("### 📋 Committee Data Table")

    # Select columns to display
    display_cols = ['CMTE_NM', 'CATEGORY', 'CMTE_TP_DESC', 'TTL_RECEIPTS', 'TTL_DISB', 'COH_COP']
    available_cols = [col for col in display_cols if col in df_filtered.columns]

    if available_cols:
        # Format numeric columns
        display_df = df_filtered[available_cols].copy()

        for col in ['TTL_RECEIPTS', 'TTL_DISB', 'COH_COP']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")

        # Sort by disbursements (descending)
        if 'TTL_DISB' in df_filtered.columns:
            sorted_df = df_filtered.sort_values('TTL_DISB', ascending=False)[available_cols].head(100)

            for col in ['TTL_RECEIPTS', 'TTL_DISB', 'COH_COP']:
                if col in sorted_df.columns:
                    sorted_df[col] = sorted_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")

            st.dataframe(sorted_df, use_container_width=True, height=600)
        else:
            st.dataframe(display_df.head(100), use_container_width=True, height=600)

        st.caption(f"Showing top 100 of {len(df_filtered):,} committees (sorted by disbursements)")
    else:
        st.warning("No committee data available to display")

# Download button
st.markdown("---")
if not df_filtered.empty:
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name="committee_analysis_filtered.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption("Data Source: FEC Bulk Data (2023-2024 Cycle) | Committee Summary (webk24.txt)")
