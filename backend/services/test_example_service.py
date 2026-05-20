"""
TestExample Service
Biznis logika za test primere
"""
import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from backend.models.test_example import TestExample
from backend.models.collection import Collection

logger = logging.getLogger(__name__)


class TestExampleService:
    """Servis za upravljanje test primerima"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_test_example(
        self,
        collection_id: int,
        question: str,
        expected_answer: str,
        category: Optional[str] = None,
        difficulty: str = "medium"
    ) -> TestExample:
        """
        Kreira novi test primer
        
        Args:
            collection_id: ID kolekcije
            question: Pitanje
            expected_answer: Očekivani odgovor
            category: Kategorija (opciono)
            difficulty: Težina (easy, medium, hard)
            
        Returns:
            TestExample instanca
            
        Raises:
            ValueError: Ako kolekcija ne postoji
        """
        # Proveri da li kolekcija postoji
        collection = self.db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise ValueError(f"Kolekcija sa ID {collection_id} ne postoji")
        
        # Validacija
        if not question or not question.strip():
            raise ValueError("Pitanje ne može biti prazno")
        if not expected_answer or not expected_answer.strip():
            raise ValueError("Očekivani odgovor ne može biti prazan")
        if difficulty not in ["easy", "medium", "hard"]:
            raise ValueError("Težina mora biti: easy, medium ili hard")
        
        # Kreiraj test primer
        test_example = TestExample(
            collection_id=collection_id,
            question=question.strip(),
            expected_answer=expected_answer.strip(),
            category=category.strip() if category else None,
            difficulty=difficulty
        )
        
        self.db.add(test_example)
        self.db.commit()
        self.db.refresh(test_example)
        
        logger.info(f"Created test example: {test_example.id}")
        return test_example
    
    def get_test_examples(
        self,
        collection_id: Optional[int] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestExample]:
        """
        Dohvata test primere sa filterima
        
        Args:
            collection_id: Filter po kolekciji
            category: Filter po kategoriji
            difficulty: Filter po težini
            skip: Broj za preskočiti (pagination)
            limit: Maksimalan broj rezultata
            
        Returns:
            Lista TestExample instanci
        """
        query = self.db.query(TestExample)
        
        if collection_id:
            query = query.filter(TestExample.collection_id == collection_id)
        if category:
            query = query.filter(TestExample.category == category)
        if difficulty:
            query = query.filter(TestExample.difficulty == difficulty)
        
        query = query.order_by(TestExample.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        return query.all()
    
    def get_test_example(self, test_example_id: int) -> Optional[TestExample]:
        """
        Dohvata pojedinačni test primer
        
        Args:
            test_example_id: ID test primera
            
        Returns:
            TestExample instanca ili None
        """
        return self.db.query(TestExample).filter(TestExample.id == test_example_id).first()
    
    def update_test_example(
        self,
        test_example_id: int,
        question: Optional[str] = None,
        expected_answer: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> TestExample:
        """
        Ažurira test primer
        
        Args:
            test_example_id: ID test primera
            question: Novo pitanje (opciono)
            expected_answer: Novi očekivani odgovor (opciono)
            category: Nova kategorija (opciono)
            difficulty: Nova težina (opciono)
            
        Returns:
            Ažurirani TestExample
            
        Raises:
            ValueError: Ako test primer ne postoji
        """
        test_example = self.get_test_example(test_example_id)
        if not test_example:
            raise ValueError(f"Test primer sa ID {test_example_id} ne postoji")
        
        # Ažuriraj polja
        if question is not None:
            if not question.strip():
                raise ValueError("Pitanje ne može biti prazno")
            test_example.question = question.strip()
        
        if expected_answer is not None:
            if not expected_answer.strip():
                raise ValueError("Očekivani odgovor ne može biti prazan")
            test_example.expected_answer = expected_answer.strip()
        
        if category is not None:
            test_example.category = category.strip() if category else None
        
        if difficulty is not None:
            if difficulty not in ["easy", "medium", "hard"]:
                raise ValueError("Težina mora biti: easy, medium ili hard")
            test_example.difficulty = difficulty
        
        self.db.commit()
        self.db.refresh(test_example)
        
        logger.info(f"Updated test example: {test_example_id}")
        return test_example
    
    def delete_test_example(self, test_example_id: int) -> bool:
        """
        Briše test primer
        
        Args:
            test_example_id: ID test primera
            
        Returns:
            True ako je obrisan, False ako ne postoji
        """
        test_example = self.get_test_example(test_example_id)
        if not test_example:
            return False
        
        self.db.delete(test_example)
        self.db.commit()
        
        logger.info(f"Deleted test example: {test_example_id}")
        return True
    
    def bulk_import(self, collection_id: int, test_examples_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk import test primera iz JSON-a
        
        Args:
            collection_id: ID kolekcije
            test_examples_data: Lista dict-ova sa test primerima
            
        Returns:
            Dict sa statistikom importa
            
        Example JSON format:
        [
            {
                "question": "Kolika je stopa poreza?",
                "expected_answer": "Stopa poreza je 10%",
                "category": "Porezi",
                "difficulty": "easy"
            }
        ]
        """
        # Proveri da li kolekcija postoji
        collection = self.db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise ValueError(f"Kolekcija sa ID {collection_id} ne postoji")
        
        imported = 0
        failed = 0
        errors = []
        
        for idx, data in enumerate(test_examples_data):
            try:
                self.create_test_example(
                    collection_id=collection_id,
                    question=data.get("question", ""),
                    expected_answer=data.get("expected_answer", ""),
                    category=data.get("category"),
                    difficulty=data.get("difficulty", "medium")
                )
                imported += 1
            except Exception as e:
                failed += 1
                errors.append(f"Row {idx + 1}: {str(e)}")
                logger.error(f"Failed to import test example {idx + 1}: {e}")
        
        logger.info(f"Bulk import completed: {imported} imported, {failed} failed")
        
        return {
            "imported": imported,
            "failed": failed,
            "total": len(test_examples_data),
            "errors": errors
        }
    
    def export_to_json(self, collection_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Export test primera u JSON format
        
        Args:
            collection_id: Filter po kolekciji (opciono)
            
        Returns:
            Lista dict-ova sa test primerima
        """
        test_examples = self.get_test_examples(collection_id=collection_id, limit=10000)
        
        return [
            {
                "id": te.id,
                "collection_id": te.collection_id,
                "question": te.question,
                "expected_answer": te.expected_answer,
                "category": te.category,
                "difficulty": te.difficulty,
                "created_at": te.created_at.isoformat()
            }
            for te in test_examples
        ]
    
    def get_statistics(self, collection_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Dohvata statistiku test primera
        
        Args:
            collection_id: Filter po kolekciji (opciono)
            
        Returns:
            Dict sa statistikom
        """
        query = self.db.query(TestExample)
        
        if collection_id:
            query = query.filter(TestExample.collection_id == collection_id)
        
        total = query.count()
        
        # Po težini
        easy = query.filter(TestExample.difficulty == "easy").count()
        medium = query.filter(TestExample.difficulty == "medium").count()
        hard = query.filter(TestExample.difficulty == "hard").count()
        
        # Po kategorijama
        categories = {}
        for te in query.all():
            cat = te.category or "Uncategorized"
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total": total,
            "by_difficulty": {
                "easy": easy,
                "medium": medium,
                "hard": hard
            },
            "by_category": categories
        }


# Made with Bob