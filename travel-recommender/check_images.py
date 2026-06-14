import pandas as pd

df = pd.read_csv('backend/data/processed/destinations_clustered.csv')

# Also check for images that look wrong based on URL content analysis
suspect = []
for _, r in df[['Destination Name', 'image', 'Country']].iterrows():
    url = str(r['image']) if pd.notna(r['image']) else ''
    name = r['Destination Name']
    country = r['Country']
    
    if not url or url == 'nan':
        continue
    
    # Check for non-photo content
    bad = False
    reason = ''
    
    if '.pdf' in url.lower() or '.djvu' in url.lower():
        bad = True
        reason = 'PDF/DJVU file'
    elif 'page1-' in url:
        bad = True
        reason = 'PDF thumbnail'
    
    # Check if image name suggests wrong content
    name_lower = name.lower()
    url_lower = url.lower()
    
    # Check for Wikipedia images from articles about different topics
    if not bad:
        # Known bad patterns: book covers, historical documents, portraits
        bad_keywords = ['forester', 'fleet_hospital', 'whaling', 'bear-hunting', 'new_york_herald',
                       'galathe', 'archaeological_tour', 'vonnegut', 'east_gate_edition',
                       'pills_to_purge', 'fish_and_fishing', 'palace_and_cottage']
        for kw in bad_keywords:
            if kw in url_lower:
                bad = True
                reason = f'Wrong content (keyword: {kw})'
                break
    
    if bad:
        suspect.append((name, country, reason, url[:120]))

# Also check Oslo and other visually wrong ones  
# Let's also check for images that might be from wrong Wikipedia articles
check_manual = [
    'Oslo Fjords & Museum Peninsula',
    'Innsbruck Alpine Skiing', 
    'Cartagena Spanish Walled City',
    'New York Times Square Neon',
    'Pokhara Phewa Lake Resort',
    'Kathmandu Durbar Square Temples',
    'Panama Canal Miraflores Locks',
    'Taipei 101 Observatory',
    'Negril Cliffs & Seven Mile Beach',
]

print(f"=== Found {len(suspect)} definitely problematic images ===")
for name, country, reason, url in suspect:
    print(f"  [{reason}] {name} ({country})")
    print(f"    {url}")
    print()

print("=== URLs for manual check (may be wrong content) ===")
for check_name in check_manual:
    row = df[df['Destination Name'] == check_name]
    if not row.empty:
        url = str(row.iloc[0]['image'])
        print(f"  {check_name}: {url[:120]}")
