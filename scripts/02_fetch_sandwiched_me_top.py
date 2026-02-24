import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

URL = "https://sandwiched.me/"
headers = {"User-Agent": "Mozilla/5.0"}

resp = requests.get(URL, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

# Find the Top Sandwichers table (adjust selector if site changes)
table = soup.find('table')  # or more specific: soup.find('h2', string='Top Sandwichers').find_next('table')

data = []
rows = table.find_all('tr')[1:11]  # top 10
for row in rows:
    cols = row.find_all('td')
    if len(cols) >= 4:
        data.append({
            "rank": cols[0].text.strip(),
            "address": cols[1].text.strip(),
            "profit_sol": float(cols[2].text.strip().replace(',', '')),
            "extracted_sol": float(cols[4].text.strip().replace(',', '')) if len(cols) > 4 else 0
        })

report = {
    "last_updated": datetime.now().isoformat(),
    "top_10": data
}

with open('outputs/sandwiched_me_top_30d.json', 'w') as f:
    json.dump(report, f, indent=2)

print("✅ Sandwiched.me top 10 saved")
print(json.dumps(data[:5], indent=2))
