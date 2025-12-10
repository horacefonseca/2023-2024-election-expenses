"""
Chart Utilities
Reusable Plotly chart functions for campaign finance visualizations
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_spending_breakdown_chart(df_breakdown):
    """
    Create bar chart of spending by category.

    Args:
        df_breakdown (pd.DataFrame): Breakdown data with Category and Disbursements columns

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.bar(
        df_breakdown,
        x='Category',
        y='Disbursements',
        title='Campaign Finance Spending by Category',
        labels={'Disbursements': 'Total Spending ($)', 'Category': ''},
        color='Category',
        color_discrete_map={
            'Traditional PACs': '#2ca02c',
            'Super PACs': '#ff7f0e',
            'Party Committees': '#9467bd',
            'Presidential': '#d62728',
            'House': '#1f77b4',
            'Senate': '#8c564b',
            'Other': '#7f7f7f'
        }
    )

    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_tickangle=-45
    )

    # Format y-axis as billions
    fig.update_yaxes(tickformat='$,.0f')

    return fig


def create_party_comparison_chart(df_candidates):
    """
    Create bar chart comparing Democratic vs Republican spending.

    Args:
        df_candidates (pd.DataFrame): Candidate data with CAND_PTY_AFFILIATION and TTL_DISB

    Returns:
        plotly.graph_objects.Figure
    """
    # Aggregate by party
    party_spending = df_candidates.groupby('CAND_PTY_AFFILIATION')['TTL_DISB'].sum().reset_index()
    party_spending = party_spending.sort_values('TTL_DISB', ascending=False).head(5)

    fig = px.bar(
        party_spending,
        x='CAND_PTY_AFFILIATION',
        y='TTL_DISB',
        title='Candidate Spending by Party',
        labels={'TTL_DISB': 'Total Spending ($)', 'CAND_PTY_AFFILIATION': 'Party'},
        color='CAND_PTY_AFFILIATION',
        color_discrete_map={
            'DEM': '#1f77b4',
            'REP': '#d62728',
            'IND': '#7f7f7f',
            'LIB': '#ff7f0e',
            'GRE': '#2ca02c'
        }
    )

    fig.update_layout(
        showlegend=False,
        height=400
    )

    fig.update_yaxes(tickformat='$,.0f')

    return fig


def create_lorenz_curve(df_donors):
    """
    Create Lorenz curve for donor inequality analysis.

    Args:
        df_donors (pd.DataFrame): Donor data with TOTAL_CONTRIB column

    Returns:
        plotly.graph_objects.Figure
    """
    # Sort donors by contribution amount
    sorted_donors = df_donors.sort_values('TOTAL_CONTRIB')

    # Calculate cumulative percentages
    total_contrib = sorted_donors['TOTAL_CONTRIB'].sum()
    cumulative_donors = range(1, len(sorted_donors) + 1)
    cumulative_contrib = sorted_donors['TOTAL_CONTRIB'].cumsum()

    # Normalize to percentages
    pct_donors = [x / len(sorted_donors) * 100 for x in cumulative_donors]
    pct_contrib = [x / total_contrib * 100 for x in cumulative_contrib]

    # Create figure
    fig = go.Figure()

    # Lorenz curve
    fig.add_trace(go.Scatter(
        x=pct_donors,
        y=pct_contrib,
        mode='lines',
        name='Lorenz Curve',
        line=dict(color='#d62728', width=2)
    ))

    # Perfect equality line
    fig.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode='lines',
        name='Perfect Equality',
        line=dict(color='#7f7f7f', width=1, dash='dash')
    ))

    fig.update_layout(
        title='Donor Inequality - Lorenz Curve',
        xaxis_title='Cumulative % of Donors',
        yaxis_title='Cumulative % of Contributions',
        height=400,
        legend=dict(x=0.02, y=0.98)
    )

    return fig


def create_scatter_plot(df, x_col, y_col, color_col=None, title="Scatter Plot"):
    """
    Generic scatter plot creator.

    Args:
        df (pd.DataFrame): Data
        x_col (str): X-axis column name
        y_col (str): Y-axis column name
        color_col (str, optional): Color grouping column
        title (str): Chart title

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        height=400,
        opacity=0.6
    )

    return fig
