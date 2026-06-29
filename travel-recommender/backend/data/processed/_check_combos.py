import csv
from collections import Counter

rows = list(csv.DictReader(open('destinations_clean.csv', 'r', encoding='utf-8')))
types = sorted(set(r['Type'] for r in rows))
print(f'Total: {len(types)} types')
print('\n'.join(types))
print()

combos = Counter((r['Country'], r['Type']) for r in rows)
print(f'Total unique country+type combos: {len(combos)}')
for (c, t), cnt in sorted(combos.items()):
    print(f'  {c:15s} {t:15s} -> {cnt} dests')
