"""Test script za debugging collections endpoint."""
import sys
import traceback

try:
    print("Importing dependencies...")
    from backend.dependencies import get_collection_service
    from backend.database import SessionLocal
    
    print("Creating service...")
    service = get_collection_service()
    
    print("Creating database session...")
    db = SessionLocal()
    
    print("Calling get_all_collections...")
    collections = service.get_all_collections(db=db, skip=0, limit=100)
    
    print(f"Success! Found {len(collections)} collections")
    for c in collections:
        print(f"  - {c.name}: {c.description}")
    
    db.close()
    
except Exception as e:
    print(f"\nERROR: {e}")
    print(f"Type: {type(e).__name__}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

# Made with Bob
