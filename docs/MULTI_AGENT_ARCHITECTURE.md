# Multi-Agent Architecture for Campaign Finance Analysis
**Framework:** Hybrid Subagent + Standalone Agent System
**Date:** 2025-12-10

---

## 🏗️ Architecture Overview

### Two-Tier Agent System

```
                    ┌─────────────────────┐
                    │   MANAGER AGENT     │
                    │   (Orchestrator)    │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
         TIER 1: CORE AGENTS   │       TIER 2: SPECIALIZED AGENTS
                │              │              │
    ┌───────────┴───────────┐ │ ┌───────────┴────────────┐
    │                       │ │ │                        │
┌───▼───┐  ┌────▼────┐  ┌──▼─▼──┐  ┌──────▼─────┐  ┌──▼────────┐
│ Data  │  │Frontend │  │Backend│  │  Network   │  │ Temporal  │
│Analyst│  │Special. │  │Special│  │  Analyst   │  │ Analyst   │
└───┬───┘  └────┬────┘  └───┬───┘  └─────┬──────┘  └───┬───────┘
    │           │            │            │             │
    │   ┌───────┴────────────┴────┐       │             │
    │   │     SUBAGENT SKILLS      │       │             │
    │   ├──────────────────────────┤       │             │
    │   │ • Political Classification│      │             │
    │   │ • Partisan Analysis       │      │             │
    │   │ • Donor Categorization   │      │             │
    │   │ • FEC Code Mapping       │      │             │
    │   └──────────────────────────┘      │             │
    │                                      │             │
    └──────────────────┬───────────────────┴─────────────┘
                       │
                ┌──────▼──────┐
                │   SHARED     │
                │  KNOWLEDGE   │
                │    BASE      │
                └──────────────┘
```

---

## 📊 Recommendation: Hybrid Approach

### Option A: Subagent Skills (Recommended for Your Use Case)

**Best for:**
- Skills that enhance existing agents
- Lightweight, specific capabilities
- Skills that multiple agents might need
- Rapid skill addition without architecture changes

**Example:** Data Analyst with subagent skills:
- **Base Skill:** Political entity classification (90-120 words)
- **Subagent Skills:**
  - FEC Code Expert (interprets all committee types)
  - Partisan Classifier (DEM/REP/IND analysis)
  - Donor Tier Analyzer (Mega/Major/Small classification)
  - Geographic Analyzer (state-level patterns)

**Pros:**
- ✅ Easy to add new skills
- ✅ Skills can be reused across agents
- ✅ No need for separate agent processes
- ✅ Lower resource overhead
- ✅ Simpler coordination

**Cons:**
- ❌ Less autonomous than standalone agents
- ❌ Can't run completely independently
- ❌ Limited parallelization

---

### Option B: Standalone Specialized Agents

**Best for:**
- Complex, autonomous tasks
- Long-running background operations
- Tasks requiring independent decision-making
- Heavy computational workloads

**Example:** Network Analyst Agent (standalone):
- Runs independently to analyze donor-committee networks
- Calculates centrality metrics for 110K donors
- Identifies super-connected hubs
- Generates network visualizations
- Reports findings back to manager

**Pros:**
- ✅ Full autonomy and parallel execution
- ✅ Can handle complex, multi-step workflows
- ✅ Better for resource-intensive tasks
- ✅ Can maintain own state/context

**Cons:**
- ❌ More complex coordination
- ❌ Higher resource requirements
- ❌ Requires inter-agent communication protocol
- ❌ More difficult to debug

---

## 🎯 RECOMMENDED: Hybrid Architecture

**Use both together:**

1. **Core Agents** (7 existing) with **Subagent Skills** for everyday tasks
2. **Specialized Agents** (4 new standalone) for complex analysis

### Core Agents with Subagent Skills

| Agent | Base Skills | Subagent Skills (Expandable) |
|-------|-------------|------------------------------|
| **Data Analyst** | Political classification | • FEC Code Expert<br>• Partisan Classifier<br>• Donor Tier Analyzer<br>• Geographic Analyzer |
| **Frontend Specialist** | Dashboard dev | • Chart Optimizer<br>• UX Analyst<br>• Mobile Adapter |
| **Backend Specialist** | Database architecture | • Query Optimizer<br>• Cache Manager<br>• Data Validator |
| **Sentiment Analyst** | Political sentiment | • Topic Modeler<br>• Bias Detector<br>• Narrative Tracker |

### Specialized Standalone Agents (New)

| Agent | Capability | Use Case |
|-------|-----------|----------|
| **Network Analyst** | Donor-committee graph analysis | Identify coordination patterns, hub donors, cluster communities |
| **Temporal Analyst** | Time-series pattern detection | Late-cycle spikes, monthly trends, seasonal patterns |
| **Predictive Analyst** | Forecasting & modeling | Predict 2026 spending, donor behavior, electoral outcomes |
| **Compliance Auditor** | Anomaly detection | Flag unusual donations, check FEC rule compliance, detect errors |

---

## 💻 Implementation: Agent Configuration Files

I'll create:

1. **agents/config/core_agents.yaml** - Configuration for 7 core agents
2. **agents/config/specialized_agents.yaml** - Configuration for 4 standalone agents
3. **agents/config/subagent_skills.yaml** - Skills that can be attached to any agent
4. **agents/orchestrator.py** - Multi-agent coordinator
5. **agents/skills_registry.py** - Dynamic skill loading system

---

## 🔧 Skill Expansion Strategy

### Method 1: Add Subagent Skills to Existing Agents

**Example: Adding "FEC Code Expert" skill to Data Analyst**

```yaml
# agents/config/subagent_skills.yaml
skills:
  fec_code_expert:
    name: "FEC Code Expert"
    description: "Deep knowledge of all FEC committee and candidate type codes"
    word_count: 90-120
    attachable_to: ["data_analyst", "backend_specialist"]
    content: |
      Interprets all Federal Election Commission type codes beyond basic O/U/N/Q:
      **Committees:** B (Lobbyist/Registrant PAC), D (Leadership PAC),
      M (Generic PAC), T (Separate Segregated Fund), W (PAC with Non-Contribution Account).
      **Designations:** A (Authorized), J (Joint Fundraiser), P (Principal), U (Unauthorized).
      **Special codes:** D2 (Delegate Committee), C (Communication Cost),
      E (Electioneering Communication), I (Independent Expenditor - Person).
      Maps committee IDs to sponsoring organizations using CONNECTED_ORG_NM field.
      Identifies hybrid PACs (Carey committees) with both contribution+IE accounts.
      Distinguishes SSFs (corporate/union) from non-connected PACs via org linkage.
```

**How to attach:**
```python
# In code
data_analyst = Agent.load("data_analyst")
data_analyst.attach_skill("fec_code_expert")
```

---

### Method 2: Create New Standalone Agent

**Example: Network Analyst Agent**

```yaml
# agents/config/specialized_agents.yaml
network_analyst:
  name: "Network Analyst Agent"
  type: "standalone"
  autonomous: true
  resource_intensive: true

  capabilities:
    - donor_committee_network_construction
    - centrality_metrics_calculation
    - community_detection
    - super_connector_identification
    - coordination_pattern_analysis

  tools:
    - networkx
    - igraph
    - plotly_network
    - graph_tool

  inputs:
    - donor_data: "input_oligarchy_donors.csv"
    - contribution_data: "itemized_contributions.csv"
    - committee_data: "all_committees_powerbi.csv"

  outputs:
    - network_metrics: "network_analysis_results.csv"
    - visualization: "donor_committee_network.html"
    - report: "network_analysis_report.md"

  parameters:
    min_contribution: 1000  # Only edges ≥ $1K
    min_degree: 2  # Exclude isolated nodes
    algorithm: "louvain"  # Community detection

  execution:
    trigger: "on_demand"  # or "scheduled", "event_driven"
    max_runtime_minutes: 30
    memory_limit_gb: 8
    parallel: true
```

---

## 🚀 Recommended Skill Expansion Roadmap

### Phase 1: Subagent Skills (Quick Wins)

**Data Analyst Skills:**
1. **FEC Code Expert** (120 words) - Deep committee type knowledge
2. **Partisan Classifier** (110 words) - DEM/REP/IND determination
3. **Donor Tier Analyzer** (100 words) - Mega/Major/Significant/Small/Nano
4. **Geographic Analyzer** (95 words) - State-level concentration patterns

**Sentiment Analyst Skills:**
5. **Topic Modeler** (105 words) - Identify campaign themes (healthcare, immigration, economy)
6. **Bias Detector** (100 words) - Detect partisan framing in committee messaging
7. **Narrative Tracker** (95 words) - Track evolving political narratives over time

**Backend Specialist Skills:**
8. **Query Optimizer** (90 words) - Optimize Pandas/SQL queries for performance
9. **Data Validator** (100 words) - Comprehensive data quality checks
10. **Cache Manager** (85 words) - Intelligent caching strategies

---

### Phase 2: Standalone Specialized Agents

**Week 1:**
- **Network Analyst** - Donor-committee graph analysis

**Week 2:**
- **Temporal Analyst** - Time-series pattern detection

**Week 3:**
- **Predictive Analyst** - Forecasting models

**Week 4:**
- **Compliance Auditor** - Anomaly detection

---

## 📋 Multi-Agent Activity Examples

### Scenario 1: Analyzing a New FEC Dataset

**Workflow:**
1. **Manager Agent**: Receives request "Process latest FEC data for 2026 cycle"
2. **Backend Specialist**: Downloads files via ETL pipeline
3. **Data Analyst** + **FEC Code Expert skill**: Classifies committees
4. **Data Analyst** + **Partisan Classifier skill**: Determines partisan lean
5. **Network Analyst** (standalone): Builds donor-committee graph (parallel)
6. **Temporal Analyst** (standalone): Analyzes spending trends (parallel)
7. **Frontend Specialist**: Updates dashboards
8. **Manager Agent**: Validates results, notifies user

**Parallelization:**
- Steps 5-6 run simultaneously (Network + Temporal agents)
- Reduces total time from 45 min → 25 min

---

### Scenario 2: Investigating Megadonor Coordination

**Workflow:**
1. **User Query**: "Are megadonors coordinating?"
2. **Manager Agent**: Delegates to specialists
3. **Data Analyst** + **Donor Tier Analyzer**: Identifies megadonors
4. **Network Analyst**: Calculates donor overlap across committees
5. **Sentiment Analyst** + **Narrative Tracker**: Checks for messaging alignment
6. **Temporal Analyst**: Analyzes synchronized spending timing
7. **Manager Agent**: Synthesizes findings into report

**Agent Interaction:**
```
Manager → Data Analyst: "Get list of megadonors"
Data Analyst → Manager: "574 megadonors identified"

Manager → Network Analyst: "Analyze connections among these 574"
Network Analyst → Manager: "47 clusters found, 89% overlap in Cluster 1"

Manager → Sentiment Analyst: "Check messaging similarity in Cluster 1"
Sentiment Analyst → Manager: "94% similar narratives detected"

Manager → User: "Evidence suggests coordination in Cluster 1"
```

---

## 🛠️ Implementation Files

I'll now create the actual configuration files and orchestrator code.

---

**Next Action:** Create the 5 implementation files listed above?

**Approval Required:** Should I proceed with creating:
1. `agents/config/core_agents.yaml`
2. `agents/config/specialized_agents.yaml`
3. `agents/config/subagent_skills.yaml`
4. `agents/orchestrator.py`
5. `agents/skills_registry.py`

This will enable the full multi-agent framework.
