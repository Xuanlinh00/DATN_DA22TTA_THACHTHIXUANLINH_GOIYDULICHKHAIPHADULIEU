import pandas as pd

df = pd.read_csv('backend/data/processed/destinations_clustered.csv')

suspicious_keywords = [
    'map', 'logo', 'flag', 'document', 'portrait', 'book', 'cover', 'statue',
    'diagram', 'chart', 'graph', 'text', 'signature', 'coin', 'stamp'
]

print("Scanning for suspicious Wikipedia images...")
for _, row in df.iterrows():
    name = row['Destination Name']
    url = str(row['image']).lower()
    
    if url and url != 'nan' and 'wikimedia' in url:
        for kw in suspicious_keywords:
            if kw in url:
                print(f"- {name}: contains '{kw}'\n  {url[:120]}")
                break
