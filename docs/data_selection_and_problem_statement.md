# Data Selection and Problem Statement
## Campaign Finance Analysis: 2023-2024 Federal Election Cycle

**Author:** Horacio Fonseca, Data Analyst, MDC Undergraduate
**Date:** December 11, 2025
**Project:** Federal Election Campaign Finance Data Mining Platform

---

## 1. Domain Selection: Political Campaign Finance Analysis

### Why Political Data Analysis Matters

Data analysis serves as a critical tool for democratic engagement and civic participation. In an era where political campaigns are increasingly defined by financial resources, understanding the flow of money through electoral systems becomes an essential function of informed citizenship. This project applies data mining techniques to Federal Election Commission (FEC) records, demonstrating how analytical methodologies can illuminate patterns of influence, concentration of wealth, and structural inequalities within democratic institutions.

**Political analysis through data science enables:**
- **Transparency**: Converting opaque financial disclosures into accessible insights
- **Accountability**: Tracking donor-candidate-committee relationships across the electoral ecosystem
- **Civic Education**: Empowering voters to understand who funds their representatives
- **Democratic Strengthening**: Identifying oligarchic patterns that may undermine representative governance

### Dataset Selection Rationale

The 2023-2024 federal election cycle was selected for analysis due to:

1. **Scale and Completeness**: $29.83 billion in documented spending across 12,370 committees, 3,861 candidates, and 110,664 donors represents one of the most comprehensive campaign finance datasets in U.S. history

2. **Data Availability**: The Federal Election Commission provides bulk data files as a public resource, ensuring reproducibility and transparency of research findings

3. **Timeliness**: Recent election cycle data allows for analysis of contemporary political dynamics, including the influence of Super PACs post-*Citizens United v. FEC* (2010)

4. **Complexity**: Fragmented multi-file structure (committee master files, candidate records, individual contributions, operating expenditures) presents authentic data engineering challenges requiring ETL pipeline development

### Data Fragmentation Challenge

The FEC bulk data exists across multiple disconnected text files:

| File | Records | Description | Size |
|------|---------|-------------|------|
| `webk24.txt` | 12,370 | Committee master file (PACs, Super PACs, Party committees) | ~50 MB |
| `weball24.txt` | 3,861 | Candidate master file (President, Senate, House) | ~8 MB |
| `itcont.txt` | 110,664 | Individual contributions ($200+ donors) | ~2.1 GB |
| `oppexp24.zip` | 847,392 | Operating expenditures by committees | ~890 MB |
| `pas224.zip` | 186,453 | Committee-to-committee transfers | ~120 MB |
| `ccl24.zip` | 9,127 | Candidate-committee linkages | ~2 MB |

**Key Challenge**: These files use inconsistent identifiers, lack normalized structure, and require complex join operations to reconstruct financial relationships among political actors.

---

## 2. Problem Statement

### Research Question

**How can data mining techniques transform fragmented Federal Election Commission bulk data into actionable intelligence that reveals patterns of financial influence, oligarchic concentration, and structural inequalities within the U.S. campaign finance system?**

### Specific Analytical Objectives

1. **Relationship Reconstruction**: Build a unified data model connecting donors → committees → candidates through multi-file joins and entity resolution

2. **Concentration Analysis**: Quantify wealth inequality in political contributions using Gini coefficients and Lorenz curves

3. **Network Mapping**: Identify financial flows between Super PACs, traditional PACs, party committees, and candidate campaigns

4. **Temporal Patterns**: Detect strategic timing of contributions across quarterly and monthly cycles (primary vs. general election spending)

5. **Partisan Asymmetry**: Compare Democratic vs. Republican fundraising structures, donor networks, and spending strategies

### The Democratic Imperative

**Active democracy requires informed citizenship.** However, the current state of campaign finance disclosure creates a paradox:

- **Legal Transparency**: The FEC publishes comprehensive financial data
- **Practical Opacity**: Raw bulk files are incomprehensible to most citizens, journalists, and even researchers without advanced data science skills

**The gap between legal compliance and functional transparency undermines democratic accountability.**

This project addresses this gap by:
1. **Finding Sources**: Identifying and accessing fragmented FEC bulk data repositories
2. **Organizing Information**: Designing ETL pipelines to consolidate 3+ million records into unified analytical datasets
3. **Extracting Insights**: Applying statistical methods (Gini coefficients, network analysis, hypothesis testing) to reveal concentration patterns
4. **Democratizing Access**: Building interactive Streamlit dashboards that allow non-technical users to explore $29.83 billion in campaign spending

---

## 3. The "Performative Transparency" Problem

### Current State of FEC Disclosure

The Federal Election Commission makes campaign finance data legally public through:
- Web-based search interface (fec.gov)
- Bulk data downloads (text files, ZIP archives)
- API access (JSON endpoints)

However, **technical accessibility ≠ functional transparency**. The raw data presents barriers:

**Structural Barriers:**
- Files exceed 2 GB, requiring specialized software to open
- Pipe-delimited text format (not Excel-compatible)
- No data dictionary or schema documentation in download
- Inconsistent field names across files (e.g., `CMTE_ID` vs. `COMMITTEE_ID`)

**Analytical Barriers:**
- Requires SQL or Python skills to join multiple tables
- Missing foreign key relationships (must infer linkages)
- Dirty data: duplicate records, inconsistent naming conventions, null values
- No aggregation or summary statistics provided

**Cognitive Barriers:**
- 110,664 donor records overwhelm manual analysis
- Cannot identify patterns (e.g., megadonor concentration) without statistical modeling
- Temporal trends invisible without time-series aggregation

### Impact on Democratic Function

This "performative transparency"—data that is technically public but practically inaccessible—concentrates political knowledge among:
- Well-funded political campaigns with data teams
- Wealthy organizations that can hire consultants
- Academic researchers with institutional resources

**Average citizens, journalists at local outlets, and grassroots advocacy groups are effectively excluded from campaign finance analysis.**

---

## 4. Project Approach: Strengthening Democracy Through Data Literacy

### Guiding Principles

**1. Accessibility Over Expertise**
- Build tools usable by non-programmers
- Natural language AI chat interface for querying data
- Interactive visualizations requiring no statistical background

**2. Reproducibility and Transparency**
- Open-source codebase (GitHub repository)
- Documented ETL pipeline for replication
- Exportable datasets for third-party verification

**3. Analytical Rigor**
- Statistical hypothesis testing (Gini coefficients, t-tests, chi-square)
- Network analysis using graph theory
- Temporal analysis with quarterly/monthly aggregations

**4. Civic Education**
- Executive summary explaining key findings in plain language
- Contextual tooltips defining terms (Super PAC, Gini coefficient, etc.)
- Data source citations in APA format for academic credibility

### Hypothesis-Driven Investigation

This project tests three core hypotheses about U.S. campaign finance:

**H1: Oligarchic Concentration**
Campaign contributions exhibit extreme wealth inequality (Gini > 0.95), with a small number of megadonors ($1M+) controlling the majority of political funding.

**H2: Strategic Timing**
Contributions are disproportionately concentrated in Q4 (October-December), reflecting late-cycle spending designed to maximize electoral impact while minimizing accountability windows.

**H3: Partisan Asymmetry**
Democratic and Republican fundraising networks exhibit fundamentally different structures, with Democrats relying on broader donor coalitions and Republicans concentrating funds through centralized Super PACs.

---

## 5. Expected Outcomes and Democratic Impact

### Analytical Deliverables

1. **Unified Dataset**: Consolidated campaign finance database with 3.86M+ records linking donors, committees, and candidates
2. **Statistical Metrics**: Gini coefficients (0.9849), Lorenz curves, concentration ratios, network centrality measures
3. **Interactive Dashboard**: Streamlit application with 7 analytical modules (Committee, Candidate, Oligarchy, Timeline, Hypothesis Testing, AI Chat)
4. **Executive Report**: 3,247-word professional summary for policymakers and advocacy groups

### Civic Impact

**Empowering Informed Citizenship:**
- Voters can research who funds their representatives
- Journalists can identify corruption patterns for investigative reporting
- Advocacy groups can build evidence for campaign finance reform

**Strengthening Democratic Accountability:**
- Reveal megadonor influence on policy outcomes
- Track corporate and special interest spending
- Identify "shadow PACs" with partisan leanings despite nonpartisan status

**Advancing Data Literacy:**
- Demonstrate how citizens can use public data for accountability
- Provide replicable methodology for analyzing other government datasets
- Build technical skills applicable to civic engagement

---

## 6. Ethical Considerations

### Data Privacy and Public Records

All data analyzed in this project:
- Is legally public under federal disclosure laws (52 U.S.C. § 30104)
- Contains only donors who contributed $200+ (triggering FEC reporting requirements)
- Excludes personal identifiers beyond name, employer, and state
- Complies with FEC Terms of Service for bulk data usage

### Analytical Objectivity

This project maintains nonpartisan analytical standards:
- Equal treatment of Democratic and Republican data
- Statistical methods applied uniformly across parties
- Findings reported regardless of political implications
- Limitations and uncertainties disclosed in documentation

### Responsible Communication

Campaign finance analysis risks misinterpretation. This project addresses this through:
- Clear definitions of terms (e.g., "oligarchy" as statistical concentration, not conspiracy)
- Contextual explanations of Gini coefficients and inequality metrics
- Acknowledgment of legal fundraising within current regulations
- Distinction between descriptive analysis and normative policy recommendations

---

## 7. Conclusion: Data as Democratic Infrastructure

Active democracy depends on informed citizenship. **Information is not knowledge.** The FEC provides information; this project transforms it into knowledge.

By rebuilding financial relationships from fragmented datasets, applying rigorous statistical analysis, and delivering insights through accessible interfaces, this campaign finance data mining platform demonstrates that **democratic accountability requires not just transparency laws, but the analytical infrastructure to make transparency meaningful**.

In an era where $29.83 billion flows through political campaigns, understanding who pays for democracy is itself an act of democratic participation.

---

## References

Federal Election Commission. (2024). *Bulk data downloads*. Retrieved from https://www.fec.gov/data/browse-data/?tab=bulk-data

Gilens, M., & Page, B. I. (2014). Testing theories of American politics: Elites, interest groups, and average citizens. *Perspectives on Politics, 12*(3), 564-581.

*Citizens United v. Federal Election Commission*, 558 U.S. 310 (2010).

OpenSecrets.org. (2024). *2024 election overview*. Center for Responsive Politics. Retrieved from https://www.opensecrets.org/elections-overview

---

**Document Version:** 1.0
**Last Updated:** December 11, 2025
**Project Repository:** https://github.com/horacefonseca/2023-2024-election-expenses
