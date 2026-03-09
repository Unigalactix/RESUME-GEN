import csv
import json

certs = []
with open('Certifications.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Authority'] != 'LinkedIn' and row['Name'].strip() != '':
            certs.append({
                "name": row['Name'].strip(),
                "issuer": row['Authority'].strip(),
                "date": row['Started On'].strip() if row['Started On'] else row['Finished On'].strip(),
                "url": row['Url'].strip() if row['Url'] else "#"
            })

with open('certs.json', 'w') as f:
    json.dump(certs, f, indent=2)

positions = []
with open('Positions.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Company Name'].strip() != '':
            positions.append({
                "Company Name": row['Company Name'],
                "Title": row['Title'],
                "Description": row['Description'],
                "Location": row['Location'],
                "Started On": row['Started On'],
                "Finished On": row['Finished On']
            })

with open('positions.json', 'w') as f:
    json.dump(positions, f, indent=2)

print("Data parsed successfully.")
