"""
Hypothesis Analysis Workflow
Orchestrated multi-agent analysis of campaign finance hypotheses

Author: Campaign Finance Analysis Team
Date: 2025-12-10
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from orchestrator import MultiAgentOrchestrator, AgentTask
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hypothesis_testing_workflow(orchestrator: MultiAgentOrchestrator):
    """
    RESEARCH HYPOTHESES FROM ORIGINAL STUDY:

    H1: Megadonor Concentration Hypothesis
        - Small % of megadonors control disproportionate share
        - Gini coefficient analysis
        - Top percentile control analysis

    H2: Strategic Timing Hypothesis
        - Late-cycle spending concentration (Q4 spike)
        - Megadonor-dependent PACs show stronger patterns

    H3: Partisan Asymmetry Hypothesis
        - Different network structures across DEM/REP
        - Donor connectivity and dependency patterns vary by party

    ADDITIONAL ANALYSIS:
    - Superdonor vs People-level donor power dynamics
    - Donor-entity classification by party/candidate support
    """

    workflow = [
        # =====================================================================
        # TASK 1: H1 - MEGADONOR CONCENTRATION ANALYSIS
        # =====================================================================
        AgentTask(
            task_id="h1_concentration_analysis",
            agent_name="data_analyst",
            action="analyze_concentration",
            parameters={
                'hypothesis': 'H1_Megadonor_Concentration',
                'use_skills': ['donor_tier_analyzer', 'fec_code_expert'],
                'data_source': 'input_oligarchy_donors.csv',
                'metrics': [
                    'gini_coefficient',
                    'top_1_percent_control',
                    'top_5_percent_control',
                    'top_10_percent_control',
                    'lorenz_curve_data'
                ],
                'visualizations': [
                    'lorenz_curve',
                    'concentration_bar_chart',
                    'donor_tier_distribution',
                    'cumulative_control_chart'
                ],
                'expected_results': {
                    'gini': 0.9849,
                    'top_1_control': 0.642,
                    'megadonor_count': 574
                }
            },
            priority=1
        ),

        # =====================================================================
        # TASK 2: H2 - STRATEGIC TIMING ANALYSIS
        # =====================================================================
        AgentTask(
            task_id="h2_timing_analysis",
            agent_name="temporal_analyst",
            action="analyze_late_cycle_patterns",
            parameters={
                'hypothesis': 'H2_Strategic_Timing',
                'data_source': 'itemized_records.parquet',
                'time_periods': ['Q1', 'Q2', 'Q3', 'Q4'],
                'metrics': [
                    'q4_concentration',
                    'late_cycle_spike_detection',
                    'monthly_spending_trends',
                    'megadonor_timing_patterns'
                ],
                'visualizations': [
                    'quarterly_spending_bar',
                    'monthly_trend_line',
                    'late_cycle_spike_committees',
                    'megadonor_vs_regular_timing'
                ],
                'analysis': {
                    'compare_megadonor_dependent': True,
                    'threshold': 0.50,
                    'detect_synchronized_spending': True
                }
            },
            priority=2,
            dependencies=["h1_concentration_analysis"]
        ),

        # =====================================================================
        # TASK 3: H3 - PARTISAN ASYMMETRY ANALYSIS
        # =====================================================================
        AgentTask(
            task_id="h3_partisan_network",
            agent_name="network_analyst",
            action="analyze_partisan_networks",
            parameters={
                'hypothesis': 'H3_Partisan_Asymmetry',
                'data_sources': [
                    'input_oligarchy_donors.csv',
                    'all_committees_powerbi.csv',
                    'itemized_contributions.parquet'
                ],
                'partisan_groups': ['DEM', 'REP', 'BIPARTISAN'],
                'metrics': [
                    'average_donor_degree',
                    'super_connected_percentage',
                    'mean_megadonor_dependency',
                    'network_density',
                    'clustering_coefficient'
                ],
                'visualizations': [
                    'partisan_network_comparison',
                    'donor_connectivity_by_party',
                    'dependency_classification_distribution',
                    'network_density_heatmap'
                ],
                'statistical_tests': [
                    'independent_t_test_dem_rep',
                    'chi_square_dependency_classification',
                    'anova_network_metrics'
                ]
            },
            priority=2,
            dependencies=["h1_concentration_analysis"]
        ),

        # =====================================================================
        # TASK 4: POWER DYNAMICS - SUPERDONORS VS PEOPLE-LEVEL
        # =====================================================================
        AgentTask(
            task_id="power_dynamics_analysis",
            agent_name="data_analyst",
            action="analyze_power_dynamics",
            parameters={
                'analysis_type': 'superdonor_vs_people_power',
                'use_skills': ['donor_tier_analyzer', 'partisan_classifier'],
                'donor_tiers': {
                    'superdonors': ['Mega'],  # $1M+
                    'people_level': ['Small', 'Nano']  # <$10K
                },
                'metrics': [
                    'total_spending_by_tier',
                    'number_of_donors_by_tier',
                    'average_contribution_by_tier',
                    'committees_influenced_by_tier',
                    'influence_ratio',  # Spending / # donors
                    'geographic_distribution_by_tier',
                    'partisan_alignment_by_tier'
                ],
                'visualizations': [
                    'power_comparison_bar',  # Superdonors vs People side-by-side
                    'influence_per_capita',  # $ per donor by tier
                    'committee_dependency_by_tier',  # How many PACs depend on each tier
                    'geographic_power_map',  # State-level power concentration
                    'sankey_money_flow'  # Donor tier → Committee → Candidate
                ],
                'key_insights': [
                    'Calculate "voice inequality": spending per donor ratio',
                    'Identify committees funded 80%+ by superdonors',
                    'Find "grassroots" committees (80%+ people-level)',
                    'Measure effective "voting power" ($ influence vs # people)'
                ]
            },
            priority=3,
            dependencies=["h1_concentration_analysis", "h3_partisan_network"]
        ),

        # =====================================================================
        # TASK 5: DONOR-ENTITY CLASSIFICATION
        # =====================================================================
        AgentTask(
            task_id="donor_entity_classification",
            agent_name="sentiment_analyst",
            action="classify_donor_entities",
            parameters={
                'analysis_type': 'pac_partisan_classification',
                'use_skills': ['partisan_classifier', 'bias_detector', 'narrative_tracker'],
                'data_sources': [
                    'input_oligarchy_donors.csv',
                    'all_committees_powerbi.csv',
                    'itemized_contributions.parquet'
                ],
                'classification_methods': [
                    'spending_pattern_analysis',  # Where money goes
                    'committee_name_nlp',  # "Democrats for...", "Republican..."
                    'connected_org_analysis',  # Corporate/union affiliations
                    'recipient_candidate_party',  # Ultimate beneficiary
                    'messaging_sentiment'  # If text data available
                ],
                'outputs': [
                    'pac_partisan_alignment',  # DEM/REP/BIPARTISAN/NON-PARTISAN
                    'confidence_scores',  # 0-1 for classification certainty
                    'shadow_partisan_flags',  # Claims non-partisan but spends 90/10
                    'candidate_specific_support',  # Which candidates each PAC supports
                    'issue_advocacy_topics'  # Healthcare, immigration, etc.
                ],
                'visualizations': [
                    'pac_classification_sunburst',  # Hierarchy: Party → Candidate → PAC
                    'confidence_distribution',  # How certain are classifications
                    'shadow_partisan_table',  # Misalignment between claim & spending
                    'candidate_support_network',  # PACs → Candidates graph
                    'issue_topic_clusters'  # Topic modeling visualization
                ],
                'validation': {
                    'cross_check_fec_reported_party': True,
                    'flag_discrepancies': True,
                    'minimum_confidence_threshold': 0.70
                }
            },
            priority=4,
            dependencies=["h3_partisan_network", "power_dynamics_analysis"]
        ),

        # =====================================================================
        # TASK 6: FRONTEND VISUALIZATION INTEGRATION
        # =====================================================================
        AgentTask(
            task_id="create_hypothesis_dashboard",
            agent_name="frontend_specialist",
            action="build_hypothesis_dashboard",
            parameters={
                'page_name': 'Hypothesis_Testing',
                'use_skills': ['chart_optimizer', 'ux_analyzer'],
                'sections': [
                    {
                        'title': 'H1: Oligarchic Concentration',
                        'charts': ['lorenz_curve', 'concentration_bar', 'tier_distribution'],
                        'kpis': ['Gini: 0.9849', 'Top 1%: 64.2%', 'Megadonors: 574']
                    },
                    {
                        'title': 'H2: Strategic Timing',
                        'charts': ['quarterly_spending', 'late_cycle_spikes', 'monthly_trends'],
                        'kpis': ['Q4 Concentration: 35.5%', 'Late Spike PACs: 57.8%']
                    },
                    {
                        'title': 'H3: Partisan Asymmetry',
                        'charts': ['network_comparison', 'donor_connectivity', 'dependency_dist'],
                        'kpis': ['DEM Dependency: 32.7%', 'REP Dependency: 28.9%']
                    },
                    {
                        'title': 'Power Dynamics: Superdonors vs People',
                        'charts': ['power_comparison', 'influence_ratio', 'committee_dependency'],
                        'kpis': ['Voice Inequality Ratio', 'Committees Dependent on Mega']
                    },
                    {
                        'title': 'PAC Partisan Classification',
                        'charts': ['pac_alignment_sunburst', 'shadow_partisan_table', 'candidate_network'],
                        'kpis': ['Classified PACs', 'Shadow Partisan %', 'Avg Confidence']
                    }
                ],
                'interactivity': {
                    'filters': ['Party', 'Donor Tier', 'Office Segment', 'Time Period'],
                    'drill_down': True,
                    'export_data': True
                }
            },
            priority=5,
            dependencies=["h1_concentration_analysis", "h2_timing_analysis",
                         "h3_partisan_network", "power_dynamics_analysis",
                         "donor_entity_classification"]
        ),

        # =====================================================================
        # TASK 7: MANAGER VALIDATION & REPORTING
        # =====================================================================
        AgentTask(
            task_id="validate_and_report",
            agent_name="manager",
            action="validate_hypothesis_results",
            parameters={
                'validation_checks': [
                    'Compare results to published research',
                    'Verify statistical significance',
                    'Check data quality and completeness',
                    'Validate visualizations accuracy'
                ],
                'generate_report': True,
                'report_sections': [
                    'Executive Summary',
                    'Hypothesis Testing Results',
                    'Power Dynamics Findings',
                    'PAC Classification Insights',
                    'Methodology',
                    'Limitations',
                    'Next Steps'
                ]
            },
            priority=6,
            dependencies=["create_hypothesis_dashboard"]
        )
    ]

    return workflow


# ==============================================================================
# EXECUTE WORKFLOW
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("HYPOTHESIS ANALYSIS WORKFLOW - ORCHESTRATOR")
    print("="*80 + "\n")

    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator()

    # Attach required skills to agents
    print("Attaching skills to agents...")
    orchestrator.attach_skill_to_agent("data_analyst", "donor_tier_analyzer")
    orchestrator.attach_skill_to_agent("data_analyst", "fec_code_expert")
    orchestrator.attach_skill_to_agent("data_analyst", "partisan_classifier")
    orchestrator.attach_skill_to_agent("sentiment_analyst", "bias_detector")
    orchestrator.attach_skill_to_agent("sentiment_analyst", "narrative_tracker")
    orchestrator.attach_skill_to_agent("frontend_specialist", "chart_optimizer")
    orchestrator.attach_skill_to_agent("frontend_specialist", "ux_analyzer")

    # Get workflow
    workflow = hypothesis_testing_workflow(orchestrator)

    print(f"\n✓ Workflow created with {len(workflow)} tasks")
    print("\nTASK BREAKDOWN:")
    print("-" * 80)
    for i, task in enumerate(workflow, 1):
        print(f"{i}. [{task.agent_name}] {task.action}")
        print(f"   Hypothesis: {task.parameters.get('hypothesis', 'N/A')}")
        print(f"   Priority: {task.priority} | Dependencies: {len(task.dependencies)}")
        print()

    # Execute workflow
    print("\n" + "="*80)
    print("EXECUTING WORKFLOW...")
    print("="*80 + "\n")

    results = orchestrator.execute_workflow(workflow)

    # Summary
    print("\n" + "="*80)
    print("WORKFLOW COMPLETE")
    print("="*80)
    print(f"\nTotal tasks executed: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed: {sum(1 for r in results if r['status'] == 'failed')}")

    print("\nRESULTS:")
    print("-" * 80)
    for result in results:
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_icon} {result['task_id']}: {result.get('output', 'No output')}")

    print("\n" + "="*80)
    print("Next: Review results in Streamlit dashboard")
    print("Run: streamlit run app.py")
    print("="*80 + "\n")
