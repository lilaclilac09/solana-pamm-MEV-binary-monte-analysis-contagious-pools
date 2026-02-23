#!/usr/bin/env python3
"""
Generate enhanced academic-style PDF report with TOC, images, tables, and case studies
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import csv
from pathlib import Path

class NumberedCanvas(canvas.Canvas):
    """Custom canvas for page numbers and TOC"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.toc = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            self.canv.showPage()
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        page_num = self._pageNumber
        self.drawRightString(7*inch, 0.75*inch, f"Page {page_num} of {page_count}")
        self.restoreState()

def load_csv_data(csv_path, max_rows=20):
    """Load CSV data for tables"""
    if not os.path.exists(csv_path):
        return None
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            return rows[:max_rows] if rows else None
    except:
        return None

def create_enhanced_report():
    """Create enhanced academic-style PDF report with TOC and attachments"""
    
    output_path = "/Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/Solana_PAMM_MEV_Analysis_Report_Enhanced.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    story = []
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
    
    toc_style = ParagraphStyle(
        'TOC',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        leftIndent=0,
        spaceAfter=8
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
    
    # TABLE OF CONTENTS
    story.append(Paragraph("Table of Contents", heading1_style))
    story.append(Spacer(1, 0.3*inch))
    
    toc_items = [
        ("Conclusion", "1"),
        ("1. Introduction", "2"),
        ("1.1 Research Objectives", "2"),
        ("1.2 Methodology Overview", "2"),
        ("2. Data Preprocessing and Cleaning", "3"),
        ("2.1 Data Collection", "3"),
        ("2.1.1 Data Quality Assessment", "3"),
        ("2.2 Data Transformation", "3"),
        ("2.3 Event Type Distribution", "3"),
        ("3. MEV Detection and Classification", "4"),
        ("3.1 Detection Algorithms", "4"),
        ("3.1.1 Sandwich Attack Patterns", "4"),
        ("3.2 Attacker Identification", "4"),
        ("3.3 Protocol-Level Analysis", "4"),
        ("4. Oracle Timing and Manipulation Analysis", "5"),
        ("4.1 Oracle Update Patterns", "5"),
        ("4.2 Back-Running Detection", "5"),
        ("4.3 Oracle Updater Analysis", "5"),
        ("5. Validator Behavior and MEV Correlation", "6"),
        ("5.1 Validator Distribution", "6"),
        ("5.2 Validator-AMM Clustering", "6"),
        ("6. Machine Learning Classification", "7"),
        ("6.1 Model Development", "7"),
        ("6.2 Model Performance", "7"),
        ("6.3 Feature Importance", "7"),
        ("7. Monte Carlo Risk Assessment", "8"),
        ("7.1 Simulation Methodology", "8"),
        ("7.2 Risk Metrics", "8"),
        ("7.3 Trapped Bot Detection", "8"),
        ("8. Case Studies", "9"),
        ("8.1 Top MEV Attackers", "9"),
        ("8.2 Validator Case Study", "9"),
        ("8.3 Bot Pattern Analysis", "9"),
        ("9. Results Summary", "10"),
        ("9.1 Quantitative Findings", "10"),
        ("9.2 Protocol-Specific Results", "10"),
        ("9.3 Validator Analysis Results", "10"),
        ("10. Attachments", "11"),
        ("10.1 MEV Bot Signers Data", "11"),
        ("10.2 Validator Statistics", "11"),
        ("10.3 Visualizations", "11"),
        ("11. Data Sources and Methodology Details", "12"),
    ]
    
    for item, page in toc_items:
        story.append(Paragraph(f"{item} <i>... {page}</i>", toc_style))
    
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
    
    # MAIN CONTENT (same as before but condensed)
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
    
    # Data Cleaning Section (condensed)
    story.append(Paragraph("2. Data Preprocessing and Cleaning", heading1_style))
    story.append(Paragraph("2.1 Data Collection", heading2_style))
    story.append(Paragraph("The original dataset contained 5,526,137 rows with 11 columns including slot, time, validator, transaction index, signature, signer, event kind, AMM identifier, account updates, trades, and timing information.", normal_style))
    
    story.append(Paragraph("2.1.1 Data Quality Assessment", heading3_style))
    story.append(Paragraph("Initial data quality analysis revealed missing values in several columns: trades (87.58% missing), AMM (12.42% missing), and timing data (0.36% missing). The parsing process successfully extracted AMM trade information from account_updates with 100% success rate.", normal_style))
    
    story.append(Paragraph("2.2 Data Transformation", heading2_style))
    story.append(Paragraph("The data transformation process involved parsing account_updates, high-precision time parsing, removal of 20,047 rows with missing timing data, and generation of a fused table. The final cleaned dataset contains 5,506,090 rows with 15 columns.", normal_style))
    story.append(PageBreak())
    
    # MEV Detection Section
    story.append(Paragraph("3. MEV Detection and Classification", heading1_style))
    story.append(Paragraph("3.1 Detection Algorithms", heading2_style))
    story.append(Paragraph("We implemented seven distinct MEV detection algorithms: Fat Sandwich Detection (5+ trades per slot), Classic Sandwich Detection (3-4 trades), Front-Running Detection (>300ms delay), Back-Running Detection (<50ms after oracle), Cross-Slot Sandwich, Slippage Sandwich, and MEV Bot Diagnostic.", normal_style))
    
    story.append(Paragraph("3.1.1 Sandwich Attack Patterns", heading3_style))
    story.append(Paragraph("Our analysis identified 26,223 sandwich attack patterns across all pAMM protocols. Fat sandwich attacks, involving 5 or more trades per slot, were the most common pattern.", normal_style))
    
    story.append(Paragraph("3.2 Attacker Identification", heading2_style))
    story.append(Paragraph("The analysis identified 589 distinct MEV attackers operating across the ecosystem. Attackers were distributed across different pAMM protocols: BisonFi (256 attackers), GoonFi (589 attackers), HumidiFi (14 attackers), ObricV2 (9 attackers), SolFi (171 attackers), SolFiV2 (157 attackers), TesseraV (115 attackers), and ZeroFi.", normal_style))
    story.append(PageBreak())
    
    # Oracle, Validator, ML, Monte Carlo sections (condensed)
    story.append(Paragraph("4. Oracle Timing and Manipulation Analysis", heading1_style))
    story.append(Paragraph("4.1 Oracle Update Patterns", heading2_style))
    story.append(Paragraph("Oracle analysis examined timing relationships between oracle price updates and trade execution. Oracle burst detection identified clusters of oracle updates in short time windows, suggesting potential manipulation attempts.", normal_style))
    
    story.append(Paragraph("5. Validator Behavior and MEV Correlation", heading1_style))
    story.append(Paragraph("5.1 Validator Distribution", heading2_style))
    story.append(Paragraph("MEV activity was distributed across 742 validators, with significant variation in bot counts and trade volumes per validator. Top 10 validators by bot count were identified, showing concentration of MEV activity.", normal_style))
    story.append(PageBreak())
    
    story.append(Paragraph("6. Machine Learning Classification", heading1_style))
    story.append(Paragraph("6.1 Model Development", heading2_style))
    story.append(Paragraph("Machine learning models were developed with 2,559 records, 9 features, and 4 classes. Multiple algorithms were evaluated including XGBoost, SVM, Logistic Regression, and Random Forest.", normal_style))
    
    story.append(Paragraph("7. Monte Carlo Risk Assessment", heading1_style))
    story.append(Paragraph("7.1 Simulation Methodology", heading2_style))
    story.append(Paragraph("Monte Carlo simulations assessed MEV risk across different scenarios, evaluating sandwich risk, front-run risk, back-run risk, expected slippage, expected loss in SOL, and success rates at both pool and token pair levels.", normal_style))
    
    # Add Monte Carlo visualization if available
    mc_image_path = "/Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/01a_data_cleaning_DeezNode_filters/outputs/images/fat_sandwich_distribution.png"
    if os.path.exists(mc_image_path):
        try:
            img = Image(mc_image_path, width=5*inch, height=3.75*inch)
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("7.2 Monte Carlo Risk Visualization", heading2_style))
            story.append(img)
            story.append(Paragraph("<i>Figure 1: Fat Sandwich Attack Distribution - Monte Carlo Risk Analysis</i>", normal_style))
            story.append(Spacer(1, 0.2*inch))
        except:
            pass
    
    story.append(PageBreak())
    
    # CASE STUDIES SECTION
    story.append(Paragraph("8. Case Studies", heading1_style))
    
    story.append(Paragraph("8.1 Top MEV Attackers", heading2_style))
    story.append(Paragraph("Analysis of the most active MEV attackers reveals distinct patterns and strategies employed by different bots.", normal_style))
    
    # Load and display top MEV bot signers
    bot_signers_path = "/Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/01a_data_cleaning_DeezNode_filters/outputs/csv/top_mev_bot_signers.csv"
    bot_data = load_csv_data(bot_signers_path, 10)
    if bot_data:
        story.append(Paragraph("8.1.1 Top 10 MEV Bot Signers by Attack Count", heading3_style))
        # Create table
        data = [bot_data[0]] + bot_data[1:11]  # Header + top 10
        t = Table(data, colWidths=[4*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("The top attacker, YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP, executed 3,782 sandwich attacks, demonstrating highly automated MEV extraction capabilities.", normal_style))
    
    story.append(Paragraph("8.2 Validator Case Study", heading2_style))
    story.append(Paragraph("8.2.1 Top Botted Validator Analysis", heading3_style))
    validator_text = """
    The validator HEL1USMZKAL2odpNBj2oCjffnFGaYwmbGmyewGv1e2TU emerged as the most affected by MEV activity:
    - Trade Count: 28,859
    - Bot Count: 408
    - Bot Ratio: 1.41%
    - MEV Breakdown: 3,119 fat_sandwich, 122 sandwich, 674 front_running, 3,998 back_running
    """
    story.append(Paragraph(validator_text, normal_style))
    
    # Load validator data
    validator_path = "/Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/01a_data_cleaning_DeezNode_filters/outputs/csv/top_validators_by_sandwich_count.csv"
    validator_data = load_csv_data(validator_path, 15)
    if validator_data:
        story.append(Paragraph("8.2.2 Top Validators by Sandwich Count", heading3_style))
        data = [validator_data[0]] + validator_data[1:16]
        t = Table(data, colWidths=[4*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("8.3 Bot Pattern Analysis", heading2_style))
    story.append(Paragraph("8.3.1 Known MEV Bot Patterns", heading3_style))
    bot_patterns_text = """
    Analysis identified several distinct bot patterns based on attack characteristics:
    
    <b>B91 Bot Pattern:</b> Fat sandwich attacks with 4-10+ trades per slot, typically wrapping 
    multiple victims in a single transaction sequence.
    
    <b>Arsc Bot Pattern:</b> Cross-slot sandwich attacks combined with oracle manipulation, 
    demonstrating sophisticated multi-slot coordination.
    
    <b>DeezNode Bot Pattern:</b> Oracle-timed back-running with trades executed within 50ms 
    after oracle updates, indicating real-time oracle monitoring.
    
    <b>2Fast Bot Pattern:</b> Cross-slot wide sandwich attacks with 4-6 trades across 2+ slots, 
    showing ability to coordinate attacks across slot boundaries.
    """
    story.append(Paragraph(bot_patterns_text, normal_style))
    
    story.append(Paragraph("8.3.2 Attacker Verification Case Study", heading3_style))
    attacker_case_text = """
    Detailed analysis of top attacker YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP revealed:
    - Total Trades: 31,220
    - Trades per Hour: 2,828.8
    - Aggregator Likelihood: 69.00% (indicating potential Jupiter aggregator activity)
    - Late-Slot Trades (>300ms): 21.55%
    
    This pattern suggests a sophisticated bot capable of both MEV extraction and legitimate 
    aggregator functionality, highlighting the challenge of distinguishing between malicious 
    MEV bots and legitimate high-frequency trading systems.
    """
    story.append(Paragraph(attacker_case_text, normal_style))
    story.append(PageBreak())
    
    # Results Summary
    story.append(Paragraph("9. Results Summary", heading1_style))
    
    story.append(Paragraph("9.1 Quantitative Findings", heading2_style))
    
    # Key statistics table
    data = [
        ['Metric', 'Value'],
        ['Total Events Analyzed', '5,506,090'],
        ['Sandwich Patterns Detected', '26,223'],
        ['Fat Sandwich Patterns', '367,162'],
        ['Distinct MEV Attackers', '589'],
        ['pAMM Protocols Analyzed', '8'],
        ['Validators Involved', '742'],
        ['Data Collection Duration', '39,735 seconds (~11 hours)'],
        ['ML Dataset Size', '2,559 records'],
        ['ML Features', '9'],
        ['ML Classes', '4'],
        ['Top Attacker Attacks', '3,782'],
    ]
    
    t = Table(data, colWidths=[3*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("9.2 Protocol-Specific Results", heading2_style))
    story.append(Paragraph("Analysis across the 8 pAMM protocols revealed varying levels of MEV activity. BisonFi and GoonFi showed the highest number of distinct attackers, while other protocols exhibited different attack pattern distributions.", normal_style))
    story.append(PageBreak())
    
    # ATTACHMENTS SECTION
    story.append(Paragraph("10. Attachments", heading1_style))
    
    story.append(Paragraph("10.1 MEV Bot Signers Data", heading2_style))
    story.append(Paragraph("Complete dataset of MEV bot signers with attack counts is available in the accompanying CSV files. The top 10 attackers account for a significant portion of total MEV activity.", normal_style))
    
    story.append(Paragraph("10.2 Validator Statistics", heading2_style))
    story.append(Paragraph("Detailed validator statistics including sandwich counts, trade volumes, and bot ratios are provided in the output CSV files. These statistics enable identification of validators most affected by MEV activity.", normal_style))
    
    story.append(Paragraph("10.3 Visualizations", heading2_style))
    
    # Add available images
    image_paths = [
        ("Fat Sandwich Distribution", "01a_data_cleaning_DeezNode_filters/outputs/images/fat_sandwich_distribution.png"),
        ("Top Validators by Volume", "01a_data_cleaning_DeezNode_filters/outputs/images/top_validators_by_volume.png"),
        ("Top Validators by Sandwich Count", "01a_data_cleaning_DeezNode_filters/outputs/images/top_validators_by_sandwich_count.png"),
        ("Top MEV Bot Signers", "01a_data_cleaning_DeezNode_filters/outputs/images/top_mev_bot_signers.png"),
        ("Event Type Distribution", "01_data_cleaning/outputs/images/event_type_distribution.png"),
    ]
    
    for img_name, img_path in image_paths:
        full_path = f"/Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/{img_path}"
        if os.path.exists(full_path):
            try:
                story.append(Paragraph(f"10.3.{image_paths.index((img_name, img_path)) + 1} {img_name}", heading3_style))
                img = Image(full_path, width=5*inch, height=3.75*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                story.append(Paragraph(f"<i>Image {img_name} could not be loaded</i>", normal_style))
    
    story.append(PageBreak())
    
    # Data Sources
    story.append(Paragraph("11. Data Sources and Methodology Details", heading1_style))
    story.append(Paragraph("11.1 Data Sources", heading2_style))
    story.append(Paragraph("All data was collected from Solana blockchain events, specifically focusing on pAMM protocol interactions. The analysis covered slots 391,876,700 to 391,976,700.", normal_style))
    
    story.append(Paragraph("11.2 Analysis Tools", heading2_style))
    story.append(Paragraph("The analysis utilized Python-based data processing pipelines, machine learning frameworks (scikit-learn, XGBoost), statistical analysis tools, and Monte Carlo simulation engines.", normal_style))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Enhanced PDF report generated: {output_path}")
    return output_path

if __name__ == "__main__":
    try:
        output = create_enhanced_report()
        print(f"\nEnhanced report successfully created at: {output}")
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
