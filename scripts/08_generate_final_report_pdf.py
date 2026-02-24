from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd

df_top = pd.read_json('outputs/top_attackers_report.json')[:5]
data = [['Rank', 'Attacker', 'Profit SOL', 'Cascade %']] + df_top[['attacker_signer', 'total_profit_sol', 'cascade_pct']].values.tolist()  # add cascade_pct if you have it

doc = SimpleDocTemplate("outputs/Solana_PAMM_MEV_Final_Report.pdf", pagesize=A4)
styles = getSampleStyleSheet()
story = [Paragraph("PAMM MEV Contagion Final Report - Feb 2026", styles['Title'])]

table = Table(data)
table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                           ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                           ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                           ('GRID', (0,0), (-1,-1), 1, colors.black)]))
story.append(table)
doc.build(story)
print("✅ PDF generated: outputs/Solana_PAMM_MEV_Final_Report.pdf")
