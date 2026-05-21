"""
Skripta za pripremu JSON fajla za import sa collection_id
"""
import json
import sys

def prepare_for_import(input_file, output_file, collection_id):
    """Dodaj collection_id u JSON za import"""
    
    # Učitaj postojeći JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Kreiraj novi format
    import_data = {
        "collection_id": collection_id,
        "test_examples": data["test_examples"]
    }
    
    # Sačuvaj
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(import_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Pripremljeno {len(data['test_examples'])} pitanja za import")
    print(f"✓ Collection ID: {collection_id}")
    print(f"✓ Sačuvano u: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Upotreba: python prepare_import.py <collection_id>")
        print("Primer: python prepare_import.py 1")
        sys.exit(1)
    
    collection_id = int(sys.argv[1])
    prepare_for_import(
        "test_examples_150.json",
        f"test_examples_150_import_collection_{collection_id}.json",
        collection_id
    )

# Made with Bob
