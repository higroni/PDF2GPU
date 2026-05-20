import requests

r = requests.get('http://localhost:8000/api/test-examples?collection_id=1&limit=100')
data = r.json()
print(f'Total imported: {len(data)}')
print('\nFirst 5 examples:')
for i, ex in enumerate(data[:5]):
    print(f'{i+1}. {ex["question"][:60]}...')

# Made with Bob
