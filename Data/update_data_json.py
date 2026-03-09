import json

# Update data.json with new certs
with open('c:/Users/kodag/OneDrive/Desktop/GitHub/rajeshkodaganti/js/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('c:/Users/kodag/OneDrive/Desktop/GitHub/rajeshkodaganti/Data/certs.json', 'r', encoding='utf-8') as f:
    certs = json.load(f)

data['certificates'] = certs

with open('c:/Users/kodag/OneDrive/Desktop/GitHub/rajeshkodaganti/js/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("data.json updated.")
