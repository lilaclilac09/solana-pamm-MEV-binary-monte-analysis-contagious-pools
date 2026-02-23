#!/usr/bin/env python3
"""
Generate academic-style PDF report from analysis results
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
import os

def create_academic_report():
    """Create academic-style PDF report"""
    
    # Create PDF document
    output_path = "/Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/Solana_PAMM_MEV_Analysis_Report.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    abstract_style = ParagraphStyle(
        'Abstract',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        rightIndent=20,
        spaceAfter=20
    )
    
    # Title Page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Comprehensive Analysis of Maximum Extractable Value (MEV) in Solana Proportional Automated Market Makers", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("An Empirical Study of MEV Extraction Patterns, Oracle Manipulation, and Validator Behavior", styles['Normal']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(f"<i>Generated: {datetime.now().strftime('%B %d, %Y')}</i>", styles['Normal']))
    story.append(PageBreak())
    
    # Abstract
    story.append(Paragraph("Abstract", heading1_style))
    abstract_text = """
    This study presents a comprehensive analysis of Maximum Extractable Value (MEV) activities 
    within Solana's Proportional Automated Market Maker (pAMM) ecosystem. Through systematic 
    examination of 5.5 million blockchain events across 8 pAMM protocols (BisonFi, GoonFi, 
    HumidiFi, ObricV2, SolFi, SolFiV2, TesseraV, ZeroFi), we identify and quantify various MEV 
    extraction strategies including sandwich attacks, front-running, back-running, and oracle 
    manipulation. Our analysis reveals 26,223 sandwich patterns, involving 589 distinct attackers 
    across 742 validators. Machine learning classification models achieve high accuracy in 
    identifying MEV patterns, while Monte Carlo simulations provide risk assessments for different 
    trading scenarios. The findings demonstrate significant MEV extraction activity, with fat 
    sandwich attacks being the most prevalent pattern, and reveal correlations between validator 
    behavior and MEV opportunities. This research contributes to understanding MEV dynamics in 
    Solana's DeFi ecosystem and provides actionable insights for protocol developers and traders.
    """
    story.append(Paragraph(abstract_text, abstract_style))
    story.append(PageBreak())
    
    # CONCLUSION (shown first as requested)
    story.append(Paragraph("Conclusion", heading1_style))
    
    conclusion_text = """
    This comprehensive analysis of MEV activities in Solana's pAMM ecosystem reveals several 
    critical findings that have significant implications for the DeFi landscape.
    """
    story.append(Paragraph(conclusion_text, normal_style))
    
    story.append(Paragraph("1.1 Key Findings", heading2_style))
    findings_text = """
    Our analysis of 5,506,090 blockchain events demonstrates extensive MEV extraction activity 
    across the Solana pAMM ecosystem. We identified 26,223 sandwich attack patterns, with fat 
    sandwich attacks (involving 5+ trades per slot) being the dominant strategy. The study 
    revealed 589 distinct MEV attackers operating across 8 pAMM protocols, with activity 
    distributed across 742 validators. Machine learning models successfully classified MEV 
    patterns with high accuracy, while Monte Carlo simulations provided quantitative risk 
    assessments showing varying success rates across different attack scenarios.
    """
    story.append(Paragraph(findings_text, normal_style))
    
    story.append(Paragraph("1.2 Implications for Protocol Design", heading2_style))
    implications_text = """
    The prevalence of MEV extraction, particularly sandwich attacks, suggests that current 
    pAMM implementations may benefit from enhanced protection mechanisms. Oracle manipulation 
    patterns indicate potential vulnerabilities in price update mechanisms that could be 
    addressed through improved oracle design or additional validation layers. The correlation 
    between validator behavior and MEV opportunities highlights the importance of validator 
    selection and monitoring in DeFi protocols.
    """
    story.append(Paragraph(implications_text, normal_style))
    
    story.append(Paragraph("1.3 Future Research Directions", heading2_style))
    future_text = """
    Future research should focus on developing real-time MEV detection systems, exploring 
    mitigation strategies such as commit-reveal schemes or private mempools, and investigating 
    the economic impact of MEV extraction on protocol users. Additionally, comparative 
    studies across different blockchain ecosystems could provide insights into MEV patterns 
    specific to Solana's architecture.
    """
    story.append(Paragraph(future_text, normal_style))
    story.append(PageBreak())
    
    # MAIN CONTENT
    story.append(Paragraph("1. Introduction", heading1_style))
    
    intro_text = """
    Maximum Extractable Value (MEV) represents one of the most significant challenges in 
    decentralized finance (DeFi). This study examines MEV extraction patterns within Solana's 
    Proportional Automated Market Maker (pAMM) ecosystem, analyzing transaction data from 8 
    major protocols to identify attack vectors, quantify extraction volumes, and assess 
    validator behavior patterns.
    """
    story.append(Paragraph(intro_text, normal_style))
    
    story.append(Paragraph("1.1 Research Objectives", heading2_style))
    objectives_text = """
    The primary objectives of this research are: (1) to identify and classify different types 
    of MEV extraction strategies in Solana pAMMs, (2) to quantify the scale and frequency of 
    MEV activities, (3) to analyze validator behavior and its correlation with MEV opportunities, 
    (4) to develop machine learning models for MEV pattern detection, and (5) to assess risk 
    scenarios through Monte Carlo simulations.
    """
    story.append(Paragraph(objectives_text, normal_style))
    
    story.append(Paragraph("1.2 Methodology Overview", heading2_style))
    methodology_text = """
    Our analysis pipeline consists of data cleaning and preprocessing, MEV pattern detection 
    using multiple algorithms, oracle timing analysis, validator behavior assessment, token 
    pair and pool analysis, machine learning classification, and Monte Carlo risk simulation. 
    The dataset comprises 5,526,137 raw events, which after cleaning and filtering, resulted 
    in 5,506,090 analyzable events spanning 39,735 seconds of blockchain activity.
    """
    story.append(Paragraph(methodology_text, normal_style))
    story.append(PageBreak())
    
    # Data Cleaning Section
    story.append(Paragraph("2. Data Preprocessing and Cleaning", heading1_style))
    
    story.append(Paragraph("2.1 Data Collection", heading2_style))
    data_collection_text = """
    The original dataset contained 5,526,137 rows with 11 columns including slot, time, 
    validator, transaction index, signature, signer, event kind, AMM identifier, account 
    updates, trades, and timing information. Data was collected from Solana blockchain 
    events across slots 391,876,700 to 391,976,700.
    """
    story.append(Paragraph(data_collection_text, normal_style))
    
    story.append(Paragraph("2.1.1 Data Quality Assessment", heading3_style))
    quality_text = """
    Initial data quality analysis revealed missing values in several columns: trades (87.58% 
    missing), AMM (12.42% missing), and timing data (0.36% missing). The parsing process 
    successfully extracted AMM trade information from account_updates with 100% success rate, 
    creating new columns for amm_trade, account_trade, is_pool_trade, and bytes_changed_trade.
    """
    story.append(Paragraph(quality_text, normal_style))
    
    story.append(Paragraph("2.2 Data Transformation", heading2_style))
    transformation_text = """
    The data transformation process involved: (1) parsing account_updates to extract trade 
    information, (2) high-precision time parsing to create datetime and millisecond timestamp 
    columns, (3) removal of 20,047 rows with missing timing data, and (4) generation of a 
    fused table combining original and parsed columns. The final cleaned dataset contains 
    5,506,090 rows with 15 columns, sorted by high-precision millisecond timestamps.
    """
    story.append(Paragraph(transformation_text, normal_style))
    
    story.append(Paragraph("2.3 Event Type Distribution", heading2_style))
    event_dist_text = """
    Analysis of event types revealed a distribution between ORACLE updates and TRADE events. 
    The dataset spans 39,735 seconds (approximately 11 hours) of blockchain activity, with 
    events distributed across multiple validators and AMM protocols.
    """
    story.append(Paragraph(event_dist_text, normal_style))
    story.append(PageBreak())
    
    # MEV Detection Section
    story.append(Paragraph("3. MEV Detection and Classification", heading1_style))
    
    story.append(Paragraph("3.1 Detection Algorithms", heading2_style))
    detection_text = """
    We implemented seven distinct MEV detection algorithms to identify various attack patterns: 
    (1) Fat Sandwich Detection - identifies attacks with 5+ trades per slot involving the same 
    attacker wrapping multiple victims, (2) Classic Sandwich Detection - detects 3-4 trade 
    patterns with attacker-victim-attacker sequences, (3) Front-Running Detection - identifies 
    late-slot trade placement (>300ms delay), (4) Back-Running Detection - detects trades within 
    50ms after oracle updates, (5) Cross-Slot Sandwich - identifies attacks spanning multiple slots, 
    (6) Slippage Sandwich - detects exploitation of slippage tolerance, and (7) MEV Bot Diagnostic 
    - comprehensive bot scoring and classification.
    """
    story.append(Paragraph(detection_text, normal_style))
    
    story.append(Paragraph("3.1.1 Sandwich Attack Patterns", heading3_style))
    sandwich_text = """
    Our analysis identified 26,223 sandwich attack patterns across all pAMM protocols. Fat 
    sandwich attacks, involving 5 or more trades per slot, were the most common pattern. 
    These attacks typically involve an attacker placing transactions before and after victim 
    transactions to profit from price movements.
    """
    story.append(Paragraph(sandwich_text, normal_style))
    
    story.append(Paragraph("3.2 Attacker Identification", heading2_style))
    attacker_text = """
    The analysis identified 589 distinct MEV attackers operating across the ecosystem. 
    Attackers were distributed across different pAMM protocols: BisonFi (256 attackers), 
    GoonFi (589 attackers), HumidiFi (14 attackers), ObricV2 (9 attackers), SolFi (171 
    attackers), SolFiV2 (157 attackers), TesseraV (115 attackers), and ZeroFi. The top 
    10 attackers per protocol were identified and analyzed for detailed activity patterns.
    """
    story.append(Paragraph(attacker_text, normal_style))
    
    story.append(Paragraph("3.3 Protocol-Level Analysis", heading2_style))
    protocol_text = """
    All 8 pAMM protocols showed evidence of MEV activity. The analysis generated per-protocol 
    statistics including total MEV trades, attacker counts, and validator distributions. Top 
    10 MEV statistics per pAMM were compiled to identify the most affected protocols and 
    the most active attackers within each protocol.
    """
    story.append(Paragraph(protocol_text, normal_style))
    story.append(PageBreak())
    
    # Oracle Analysis Section
    story.append(Paragraph("4. Oracle Timing and Manipulation Analysis", heading1_style))
    
    story.append(Paragraph("4.1 Oracle Update Patterns", heading2_style))
    oracle_patterns_text = """
    Oracle analysis examined the timing relationships between oracle price updates and trade 
    execution. The study identified patterns where oracle updates cluster before or after 
    trades, suggesting potential manipulation or exploitation opportunities. Oracle burst 
    detection algorithms identified clusters of oracle updates in short time windows, which 
    may indicate coordinated price manipulation attempts.
    """
    story.append(Paragraph(oracle_patterns_text, normal_style))
    
    story.append(Paragraph("4.2 Back-Running Detection", heading2_style))
    backrun_text = """
    Back-running patterns were identified by detecting trades occurring within 50ms after 
    oracle updates. This rapid response time suggests automated systems monitoring oracle 
    updates and executing trades immediately to capitalize on price changes. The analysis 
    also examined slow response times to understand the full spectrum of oracle-trade 
    relationships.
    """
    story.append(Paragraph(backrun_text, normal_style))
    
    story.append(Paragraph("4.3 Oracle Updater Analysis", heading2_style))
    updater_text = """
    The study identified the most active oracle updaters and analyzed their update frequency 
    patterns. Correlation analysis between oracle update activity and MEV events revealed 
    potential relationships between oracle behavior and MEV opportunities.
    """
    story.append(Paragraph(updater_text, normal_style))
    story.append(PageBreak())
    
    # Validator Analysis Section
    story.append(Paragraph("5. Validator Behavior and MEV Correlation", heading1_style))
    
    story.append(Paragraph("5.1 Validator Distribution", heading2_style))
    validator_dist_text = """
    MEV activity was distributed across 742 validators, with significant variation in bot 
    counts and trade volumes per validator. Top 10 validators by bot count were identified, 
    showing the concentration of MEV activity among certain validators. The analysis 
    calculated bot ratios, trade counts, and MEV type distributions per validator.
    """
    story.append(Paragraph(validator_dist_text, normal_style))
    
    story.append(Paragraph("5.2 Validator-AMM Clustering", heading2_style))
    clustering_text = """
    Cluster analysis revealed patterns in validator behavior across different AMM protocols. 
    Some validators showed higher concentrations of MEV activity for specific protocols, 
    suggesting potential specialization or targeted exploitation strategies.
    """
    story.append(Paragraph(clustering_text, normal_style))
    story.append(PageBreak())
    
    # Machine Learning Section
    story.append(Paragraph("6. Machine Learning Classification", heading1_style))
    
    story.append(Paragraph("6.1 Model Development", heading2_style))
    ml_model_text = """
    Machine learning models were developed to classify MEV patterns automatically. The dataset 
    comprised 2,559 records with 9 features across 4 classes. Multiple algorithms were 
    evaluated including XGBoost, Support Vector Machines (SVM), Logistic Regression, and 
    Random Forest classifiers. Feature importance analysis identified the most significant 
    indicators of MEV activity.
    """
    story.append(Paragraph(ml_model_text, normal_style))
    
    story.append(Paragraph("6.2 Model Performance", heading2_style))
    ml_perf_text = """
    Model comparison revealed varying performance across different algorithms. Confusion matrices 
    were generated to assess classification accuracy. Gaussian Mixture Model (GMM) analysis 
    was also performed to identify natural clusters in the MEV data, providing additional 
    insights into attack pattern similarities.
    """
    story.append(Paragraph(ml_perf_text, normal_style))
    
    story.append(Paragraph("6.3 Feature Importance", heading2_style))
    feature_text = """
    Feature importance analysis identified the most critical variables for MEV detection, 
    enabling prioritization of monitoring metrics and development of more efficient detection 
    systems. Visualization of feature importance and 2D cluster representations provided 
    interpretable insights into model behavior.
    """
    story.append(Paragraph(feature_text, normal_style))
    story.append(PageBreak())
    
    # Monte Carlo Section
    story.append(Paragraph("7. Monte Carlo Risk Assessment", heading1_style))
    
    story.append(Paragraph("7.1 Simulation Methodology", heading2_style))
    mc_method_text = """
    Monte Carlo simulations were conducted to assess MEV risk across different scenarios. 
    The simulations evaluated sandwich risk, front-run risk, back-run risk, expected slippage, 
    expected loss in SOL, and success rates. Scenarios were analyzed both at the pool level 
    and token pair level to provide granular risk assessments.
    """
    story.append(Paragraph(mc_method_text, normal_style))
    
    story.append(Paragraph("7.2 Risk Metrics", heading2_style))
    risk_metrics_text = """
    The analysis generated comprehensive risk metrics including percentage risks for different 
    attack types, expected financial losses, and success rate distributions. Comparison 
    across scenarios revealed variations in vulnerability, with some pools and token pairs 
    showing significantly higher MEV risk than others.
    """
    story.append(Paragraph(risk_metrics_text, normal_style))
    
    story.append(Paragraph("7.3 Trapped Bot Detection", heading2_style))
    trapped_text = """
    The analysis included detection of trapped bots - MEV bots that may have been caught in 
    failed attack attempts. This provides insights into the success rates of different MEV 
    strategies and identifies potential counter-strategies that protocols might employ.
    """
    story.append(Paragraph(trapped_text, normal_style))
    story.append(PageBreak())
    
    # Results Summary
    story.append(Paragraph("8. Results Summary", heading1_style))
    
    story.append(Paragraph("8.1 Quantitative Findings", heading2_style))
    
    # Create a table with key statistics
    data = [
        ['Metric', 'Value'],
        ['Total Events Analyzed', '5,506,090'],
        ['Sandwich Patterns Detected', '26,223'],
        ['Distinct MEV Attackers', '589'],
        ['pAMM Protocols Analyzed', '8'],
        ['Validators Involved', '742'],
        ['Data Collection Duration', '39,735 seconds (~11 hours)'],
        ['ML Dataset Size', '2,559 records'],
        ['ML Features', '9'],
        ['ML Classes', '4'],
    ]
    
    t = Table(data, colWidths=[3*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("8.2 Protocol-Specific Results", heading2_style))
    protocol_results_text = """
    Analysis across the 8 pAMM protocols revealed varying levels of MEV activity. BisonFi 
    and GoonFi showed the highest number of distinct attackers, while other protocols exhibited 
    different attack pattern distributions. Fat sandwich patterns were consistently the most 
    common attack type across all protocols.
    """
    story.append(Paragraph(protocol_results_text, normal_style))
    
    story.append(Paragraph("8.3 Validator Analysis Results", heading2_style))
    validator_results_text = """
    Validator analysis revealed significant concentration of MEV activity, with top validators 
    showing high bot ratios and trade counts. The distribution of MEV types (fat sandwich, 
    sandwich, front-running, back-running) varied across validators, suggesting different 
    specialization patterns or strategic preferences.
    """
    story.append(Paragraph(validator_results_text, normal_style))
    story.append(PageBreak())
    
    # References/Data Sources
    story.append(Paragraph("9. Data Sources and Methodology Details", heading1_style))
    
    story.append(Paragraph("9.1 Data Sources", heading2_style))
    sources_text = """
    All data was collected from Solana blockchain events, specifically focusing on pAMM 
    protocol interactions. The analysis covered slots 391,876,700 to 391,976,700, representing 
    a comprehensive snapshot of MEV activity during this period.
    """
    story.append(Paragraph(sources_text, normal_style))
    
    story.append(Paragraph("9.2 Analysis Tools", heading2_style))
    tools_text = """
    The analysis utilized Python-based data processing pipelines, machine learning frameworks 
    (scikit-learn, XGBoost), statistical analysis tools, and Monte Carlo simulation engines. 
    All code and methodologies are documented in the accompanying Jupyter notebooks.
    """
    story.append(Paragraph(tools_text, normal_style))
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF report generated: {output_path}")
    return output_path

if __name__ == "__main__":
    try:
        output = create_academic_report()
        print(f"\nReport successfully created at: {output}")
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
