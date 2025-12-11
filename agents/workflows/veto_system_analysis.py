"""
Veto System Analysis Workflow
Check if campaign finance data supports assertions about U.S. amendment veto system

Target Assertions:
1. High partisan correlation (r > 0.90)
2. Binary party structure (two coherent veto blocs)
3. Polarization index impact
4. Independent/third-party presence
5. Party discipline indicators

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


def veto_system_analysis_workflow(orchestrator: MultiAgentOrchestrator):
    """
    RESEARCH QUESTION:
    Can campaign finance data support assertions about the U.S. engineered veto system?

    KEY ASSERTIONS TO TEST:
    1. High partisan correlation (r > 0.90) in voting/spending behavior
    2. Binary party structure with two coherent veto blocs
    3. Polarization index drives outcomes
    4. Third-party/independent weakness (< 5% of seats)
    5. Party discipline reflected in spending patterns

    CAMPAIGN FINANCE PROXIES:
    - Partisan spending patterns → Partisan correlation proxy
    - DEM vs REP funding ratios → Binary structure indicator
    - Partisan imbalance scores → Polarization proxy
    - Third-party candidate funding → Independent viability indicator
    - Committee partisan alignment → Party discipline proxy
    """

    workflow = [
        # =====================================================================
        # TASK 1: PARTISAN CORRELATION ANALYSIS
        # =====================================================================
        AgentTask(
            task_id="partisan_correlation_proxy",
            agent_name="data_analyst",
            action="analyze_partisan_correlation",
            parameters={
                'assertion': 'High partisan correlation (r > 0.90)',
                'use_skills': ['partisan_classifier', 'donor_tier_analyzer'],
                'data_sources': [
                    'all_committees_powerbi.csv',
                    'all_candidates_powerbi.csv',
                    'input_oligarchy_donors.csv'
                ],
                'analysis': {
                    'calculate_spending_correlation': {
                        'method': 'Compare DEM vs REP spending patterns across:',
                        'dimensions': [
                            'Office segment (PRES/SEN/HOU)',
                            'Geographic region (states)',
                            'Time period (quarters)',
                            'Committee type (PAC/Super PAC)'
                        ],
                        'expected': 'If partisan correlation > 0.90, expect:',
                        'indicators': [
                            'DEM donors fund almost exclusively DEM candidates',
                            'REP donors fund almost exclusively REP candidates',
                            'Minimal cross-partisan funding (<5%)',
                            'High partisan imbalance scores (>0.80)'
                        ]
                    },
                    'calculate_partisan_purity': {
                        'metric': 'Partisan Purity Index',
                        'formula': '% of donors funding single party exclusively',
                        'threshold': '>85% = high correlation proxy'
                    }
                },
                'outputs': {
                    'correlation_matrix': 'DEM_spending vs REP_spending by dimension',
                    'partisan_purity_pct': '% donors funding single party',
                    'cross_partisan_funding_pct': '% funding both parties',
                    'imbalance_score_distribution': 'Histogram of partisan scores'
                },
                'conclusion': {
                    'if_high_purity': 'SUPPORTS assertion - binary partisan structure',
                    'if_low_purity': 'CONTRADICTS - more fluid partisan landscape'
                }
            },
            priority=1
        ),

        # =====================================================================
        # TASK 2: BINARY PARTY STRUCTURE ANALYSIS
        # =====================================================================
        AgentTask(
            task_id="binary_structure_test",
            agent_name="data_analyst",
            action="test_binary_party_structure",
            parameters={
                'assertion': 'Binary party structure (two coherent veto blocs)',
                'use_skills': ['partisan_classifier', 'fec_code_expert'],
                'metrics': [
                    {
                        'name': 'Two-Party Dominance',
                        'calculation': '(DEM_spending + REP_spending) / TOTAL_spending',
                        'threshold': '>95% = binary structure',
                        'data_source': 'all_candidates_powerbi.csv'
                    },
                    {
                        'name': 'Third-Party Viability',
                        'calculation': 'IND + LIB + GRE + Other spending / TOTAL',
                        'threshold': '<5% = confirms weak third parties',
                        'data_source': 'all_candidates_powerbi.csv'
                    },
                    {
                        'name': 'Committee Partisan Clarity',
                        'calculation': '% committees with partisan_imbalance > 0.80',
                        'threshold': '>70% = coherent blocs',
                        'data_source': 'all_committees_powerbi.csv'
                    }
                ],
                'analysis': {
                    'break_down_by_office': {
                        'presidential': 'Expect highest DEM/REP dominance',
                        'senate': 'Expect high but slightly more third-party',
                        'house': 'Check for independent candidacies'
                    },
                    'identify_exceptions': {
                        'find': 'Candidates/committees with bipartisan funding',
                        'quantify': '% that are truly independent',
                        'assess': 'Could these disrupt veto system?'
                    }
                },
                'conclusion_criteria': {
                    'strong_binary': '>95% two-party, <5% third-party, >70% partisan clarity',
                    'weak_binary': '85-95% two-party, 5-10% third-party',
                    'multiparty': '<85% two-party, >10% third-party'
                }
            },
            priority=2,
            dependencies=["partisan_correlation_proxy"]
        ),

        # =====================================================================
        # TASK 3: POLARIZATION INDEX PROXY
        # =====================================================================
        AgentTask(
            task_id="polarization_indicators",
            agent_name="network_analyst",
            action="calculate_polarization_proxies",
            parameters={
                'assertion': 'Polarization index has highest weight in outcomes',
                'use_skills': None,  # Specialized agent
                'polarization_proxies': [
                    {
                        'name': 'Partisan Spending Gap',
                        'calculation': 'abs(DEM_total - REP_total) / (DEM + REP)',
                        'interpretation': 'Higher gap = higher polarization'
                    },
                    {
                        'name': 'Cross-Partisan Network Density',
                        'calculation': 'DEM donor → REP committee edge count',
                        'interpretation': 'Lower density = higher polarization'
                    },
                    {
                        'name': 'Partisan Segregation Index',
                        'calculation': 'Dissimilarity index for donor networks',
                        'interpretation': 'Like residential segregation measure'
                    },
                    {
                        'name': 'Ideological Distance',
                        'proxy': 'Avg partisan imbalance score by party',
                        'interpretation': '>0.80 avg = extreme polarization'
                    }
                ],
                'sensitivity_test': {
                    'question': 'Do highly polarized committees behave differently?',
                    'method': 'Compare high imbalance (>0.90) vs low (<0.50)',
                    'metrics': [
                        'Spending concentration',
                        'Late-cycle behavior',
                        'Donor diversity',
                        'Geographic concentration'
                    ]
                },
                'expected_finding': {
                    'if_supports': 'High polarization correlates with:',
                    'indicators': [
                        'More extreme spending patterns',
                        'Less donor diversity',
                        'Stronger late-cycle concentration',
                        'Geographic clustering (blue/red states)'
                    ]
                }
            },
            priority=3,
            dependencies=["binary_structure_test"]
        ),

        # =====================================================================
        # TASK 4: INDEPENDENT/THIRD-PARTY VIABILITY
        # =====================================================================
        AgentTask(
            task_id="independent_viability_analysis",
            agent_name="data_analyst",
            action="assess_independent_viability",
            parameters={
                'assertion': 'Independent wave requires 60 House + 15 Senate seats',
                'use_skills': ['partisan_classifier', 'donor_tier_analyzer'],
                'current_state_analysis': {
                    'count_independent_candidates': {
                        'party_codes': ['IND', 'LIB', 'GRE', 'NPA'],
                        'source': 'all_candidates_powerbi.csv'
                    },
                    'calculate_funding_gap': {
                        'metric': 'IND_avg_spending / DEM_avg_spending',
                        'expected': '<0.10 (10% of major party funding)'
                    },
                    'assess_megadonor_support': {
                        'question': 'Do megadonors fund independents?',
                        'data': 'input_oligarchy_donors.csv',
                        'calculate': '% megadonors funding IND candidates',
                        'expected': '<2%'
                    }
                },
                'viability_metrics': [
                    {
                        'name': 'Funding Competitiveness',
                        'calculation': 'IND_spending / (DEM + REP) spending',
                        'threshold': '>0.15 = viable, <0.05 = non-viable'
                    },
                    {
                        'name': 'Donor Base Breadth',
                        'calculation': '# unique donors to IND candidates',
                        'compare': 'vs DEM/REP donor counts'
                    },
                    {
                        'name': 'Geographic Spread',
                        'calculation': '# states with IND candidates >5% spending',
                        'threshold': '<10 states = not viable wave'
                    }
                ],
                'hypothetical_scenario': {
                    'question': 'What would 60 House + 15 Senate IND seats cost?',
                    'calculation': {
                        'house_avg_cost': 'Median House candidate spending',
                        'senate_avg_cost': 'Median Senate candidate spending',
                        'total_estimate': '(60 * house) + (15 * senate)'
                    },
                    'feasibility': 'Compare to current third-party total funding'
                },
                'conclusion': {
                    'if_non_viable': 'SUPPORTS veto assertion - no disruption possible',
                    'if_viable': 'CONTRADICTS - independent wave feasible'
                }
            },
            priority=4,
            dependencies=["polarization_indicators"]
        ),

        # =====================================================================
        # TASK 5: PARTY DISCIPLINE INDICATORS
        # =====================================================================
        AgentTask(
            task_id="party_discipline_proxy",
            agent_name="sentiment_analyst",
            action="analyze_party_discipline_signals",
            parameters={
                'assertion': 'Party discipline affects amendment probability',
                'use_skills': ['partisan_classifier', 'bias_detector'],
                'discipline_proxies': [
                    {
                        'name': 'Committee Alignment Consistency',
                        'measure': 'Do DEM committees fund same candidates?',
                        'calculation': 'Overlap % in recipient candidates',
                        'interpretation': '>70% overlap = high discipline'
                    },
                    {
                        'name': 'Donor Loyalty',
                        'measure': '% donors giving to single party across cycles',
                        'data_limitation': 'Only have 2024 data, note for future',
                        'proxy': 'Current partisan purity as indicator'
                    },
                    {
                        'name': 'Message Coordination',
                        'measure': 'Similarity in committee messaging/topics',
                        'method': 'If text data available, topic modeling',
                        'proxy': 'Committee name analysis for party mentions'
                    },
                    {
                        'name': 'Leadership PAC Dominance',
                        'measure': 'What % of funding flows through party leaders?',
                        'identify': 'Leadership PACs in dataset',
                        'calculate': 'Their share of total party spending'
                    }
                ],
                'expected_finding': {
                    'high_discipline': 'If committees show high coordination:',
                    'indicators': [
                        '>70% funding same set of candidates',
                        '>85% partisan purity',
                        'Centralized through leadership PACs',
                        'Geographic consistency (party strongholds)'
                    ],
                    'implication': 'SUPPORTS veto - parties act as coherent blocs'
                }
            },
            priority=5,
            dependencies=["independent_viability_analysis"]
        ),

        # =====================================================================
        # TASK 6: SYNTHESIS & CONCLUSION
        # =====================================================================
        AgentTask(
            task_id="synthesize_veto_analysis",
            agent_name="manager",
            action="synthesize_findings",
            parameters={
                'synthesis_questions': [
                    {
                        'question': 'Does our data support high partisan correlation?',
                        'look_for': 'Partisan purity >85%, cross-partisan funding <5%'
                    },
                    {
                        'question': 'Is binary structure evident?',
                        'look_for': 'DEM+REP >95% of spending, third-party <5%'
                    },
                    {
                        'question': 'Can we proxy polarization?',
                        'look_for': 'High imbalance scores, low cross-partisan network density'
                    },
                    {
                        'question': 'Are independents viable?',
                        'look_for': 'Funding gap, donor support, number of candidates'
                    },
                    {
                        'question': 'Is party discipline evident?',
                        'look_for': 'Coordinated funding, donor loyalty, message alignment'
                    }
                ],
                'overall_assessment': {
                    'if_supports': {
                        'conclusion': 'Campaign finance data SUPPORTS veto system assertions',
                        'evidence': [
                            'Extreme partisan purity in funding',
                            'Binary two-party dominance',
                            'High polarization indicators',
                            'Weak third-party viability',
                            'Coordinated party discipline'
                        ],
                        'implication': 'Money flows mirror political gridlock structure'
                    },
                    'if_contradicts': {
                        'conclusion': 'Data shows more fluidity than veto theory suggests',
                        'evidence': 'Cross-partisan funding, viable independents, etc.'
                    },
                    'limitations': [
                        'Campaign finance ≠ voting behavior',
                        'Money influence indirect',
                        'Single cycle snapshot',
                        'No direct amendment voting data'
                    ]
                },
                'recommendations': {
                    'data_needed': [
                        'Congressional roll call votes for correlation calc',
                        'Multi-cycle data for trend analysis',
                        'Amendment proposal voting records',
                        'State legislature data for ratification analysis'
                    ],
                    'further_analysis': [
                        'Compare fundraising to actual votes',
                        'Analyze PAC influence on amendment positions',
                        'Track independent candidates across cycles',
                        'State-level analysis (ratification threshold)'
                    ]
                }
            },
            priority=6,
            dependencies=["partisan_correlation_proxy", "binary_structure_test",
                         "polarization_indicators", "independent_viability_analysis",
                         "party_discipline_proxy"]
        )
    ]

    return workflow


# ==============================================================================
# EXECUTE WORKFLOW
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("VETO SYSTEM ANALYSIS WORKFLOW")
    print("Checking if campaign finance data supports veto system assertions")
    print("="*80 + "\n")

    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator()

    # Attach skills
    print("Attaching skills...")
    orchestrator.attach_skill_to_agent("data_analyst", "partisan_classifier")
    orchestrator.attach_skill_to_agent("data_analyst", "donor_tier_analyzer")
    orchestrator.attach_skill_to_agent("data_analyst", "fec_code_expert")
    orchestrator.attach_skill_to_agent("sentiment_analyst", "bias_detector")
    orchestrator.attach_skill_to_agent("sentiment_analyst", "partisan_classifier")

    # Get workflow
    workflow = veto_system_analysis_workflow(orchestrator)

    print(f"\n✓ Workflow created with {len(workflow)} tasks\n")
    print("ASSERTIONS TO TEST:")
    print("-" * 80)
    print("1. High partisan correlation (r > 0.90)")
    print("2. Binary party structure (two coherent veto blocs)")
    print("3. Polarization index impact")
    print("4. Third-party/independent weakness")
    print("5. Party discipline indicators")
    print()

    # Execute
    print("="*80)
    print("EXECUTING ANALYSIS...")
    print("="*80 + "\n")

    results = orchestrator.execute_workflow(workflow)

    # Summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nTasks executed: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['status'] == 'success')}")

    print("\nKEY FINDINGS:")
    print("-" * 80)
    for result in results:
        if result['status'] == 'success':
            print(f"✓ {result['task_id']}")

    print("\n" + "="*80)
    print("Interpretation: Campaign finance data provides INDIRECT evidence")
    print("for veto system assertions through spending pattern analysis.")
    print("="*80 + "\n")
