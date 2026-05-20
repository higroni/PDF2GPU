"""
Qdrant Service - Upravljanje vektorskom bazom.

Koristi Qdrant za skladištenje i pretragu vektora sa hybrid search podrškom.
"""

from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    Prefetch,
    QueryRequest,
    Query
)
import numpy as np
import logging

# Konfiguriši logger
logger = logging.getLogger(__name__)
from pathlib import Path


class QdrantService:
    """Servis za rad sa Qdrant vektorskom bazom."""
    
    def __init__(
        self,
        path: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Inicijalizuje Qdrant servis.
        
        Args:
            path: Putanja za lokalnu Qdrant bazu (default: ./qdrant_data)
            url: URL za remote Qdrant server (opciono)
            api_key: API key za remote server (opciono)
        """
        if url:
            # Remote Qdrant server
            self.client = QdrantClient(url=url, api_key=api_key)
            logger.info(f"Povezan sa remote Qdrant: {url}")
        else:
            # Lokalna Qdrant baza
            if path is None:
                path = "./qdrant_data"
            
            # Kreiraj direktorijum ako ne postoji
            Path(path).mkdir(parents=True, exist_ok=True)
            
            self.client = QdrantClient(path=path)
            logger.info(f"Koristi lokalnu Qdrant bazu: {path}")
    
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine",
        on_disk: bool = False
    ) -> bool:
        """
        Kreira novu kolekciju.
        
        Args:
            collection_name: Naziv kolekcije
            vector_size: Dimenzija vektora
            distance: Metrika distance ('Cosine', 'Euclid', 'Dot')
            on_disk: Da li čuvati vektore na disku (za velike kolekcije)
            
        Returns:
            True ako je uspešno kreirano
        """
        try:
            # Proveri da li kolekcija već postoji
            if self.collection_exists(collection_name):
                logger.warning(f"Kolekcija '{collection_name}' vec postoji")
                return False
            
            # Mapiraj distance string na enum
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclid": Distance.EUCLID,
                "Dot": Distance.DOT
            }
            
            distance_metric = distance_map.get(distance, Distance.COSINE)
            
            # Kreiraj kolekciju
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_metric,
                    on_disk=on_disk
                )
            )
            
            logger.info(f"Kolekcija '{collection_name}' kreirana")
            logger.info(f"   - Vector size: {vector_size}")
            logger.info(f"   - Distance: {distance}")
            logger.info(f"   - On disk: {on_disk}")
            
            return True
            
        except Exception as e:
            logger.error(f"Greska pri kreiranju kolekcije: {str(e)}")
            return False
    
    def collection_exists(self, collection_name: str) -> bool:
        """Proverava da li kolekcija postoji."""
        try:
            collections = self.client.get_collections().collections
            return any(c.name == collection_name for c in collections)
        except:
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Briše kolekciju.
        
        Args:
            collection_name: Naziv kolekcije
            
        Returns:
            True ako je uspešno obrisano
        """
        try:
            if not self.collection_exists(collection_name):
                logger.warning(f"Kolekcija '{collection_name}' ne postoji")
                return False
            
            self.client.delete_collection(collection_name)
            logger.info(f"Kolekcija '{collection_name}' obrisana")
            return True
            
        except Exception as e:
            logger.error(f"Greska pri brisanju kolekcije: {str(e)}")
            return False
    
    def add_vectors(
        self,
        collection_name: str,
        vectors: List[np.ndarray],
        payloads: List[Dict],
        ids: Optional[List[int]] = None
    ) -> bool:
        """
        Dodaje vektore u kolekciju.
        
        Args:
            collection_name: Naziv kolekcije
            vectors: Lista vektora
            payloads: Lista payload-a (metadata)
            ids: Lista ID-jeva (opciono, generiše se automatski)
            
        Returns:
            True ako je uspešno dodato
        """
        try:
            if not self.collection_exists(collection_name):
                logger.error(f"Kolekcija '{collection_name}' ne postoji")
                return False
            
            # Generiši ID-jeve ako nisu prosleđeni
            if ids is None:
                # Dobij trenutni broj tačaka u kolekciji
                info = self.client.get_collection(collection_name)
                start_id = info.points_count if info.points_count else 0
                ids = list(range(start_id, start_id + len(vectors)))
            
            # Kreiraj points
            points = [
                PointStruct(
                    id=point_id,
                    vector=vector.tolist() if isinstance(vector, np.ndarray) else vector,
                    payload=payload
                )
                for point_id, vector, payload in zip(ids, vectors, payloads)
            ]
            
            # Dodaj u kolekciju
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"Dodato {len(points)} vektora u '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Greska pri dodavanju vektora: {str(e)}")
            return False
    
    def search(
        self,
        collection_name: str,
        query_vector: np.ndarray,
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Pretražuje kolekciju.
        
        Args:
            collection_name: Naziv kolekcije
            query_vector: Query vektor
            limit: Broj rezultata
            score_threshold: Minimalni score (opciono)
            filter_conditions: Filter uslovi (opciono)
            
        Returns:
            Lista rezultata sa score-om i payload-om
        """
        try:
            if not self.collection_exists(collection_name):
                logger.error(f"Kolekcija '{collection_name}' ne postoji")
                return []
            
            # Konvertuj filter ako postoji
            query_filter = None
            if filter_conditions:
                query_filter = self._build_filter(filter_conditions)
            
            # Pretraži
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter,
                with_payload=True
            )
            
            # Formatiraj rezultate
            formatted_results = []
            for result in results.points:
                formatted_results.append({
                    'id': result.id,
                    'score': result.score if hasattr(result, 'score') else 0.0,
                    'payload': result.payload
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Greska pri pretrazi: {str(e)}")
            return []
    
    def _build_filter(self, conditions: Dict) -> Filter:
        """Kreira Qdrant filter iz dict-a."""
        # Jednostavan filter builder - može se proširiti
        must_conditions = []
        
        for key, value in conditions.items():
            must_conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
            )
        
        return Filter(must=must_conditions)
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict]:
        """
        Vraća informacije o kolekciji.
        
        Args:
            collection_name: Naziv kolekcije
            
        Returns:
            Dict sa informacijama ili None
        """
        try:
            if not self.collection_exists(collection_name):
                return None
            
            info = self.client.get_collection(collection_name)
            
            return {
                'name': collection_name,
                'points_count': info.points_count,
                'indexed_vectors_count': info.indexed_vectors_count if hasattr(info, 'indexed_vectors_count') else 0,
                'status': info.status.value if hasattr(info.status, 'value') else str(info.status)
            }
            
        except Exception as e:
            logger.error(f"Greska pri dobijanju info: {str(e)}")
            return None
    
    def list_collections(self) -> List[str]:
        """Vraća listu svih kolekcija."""
        try:
            collections = self.client.get_collections().collections
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"Greska pri listanju kolekcija: {str(e)}")
            return []
    
    def clear_collection(self, collection_name: str) -> bool:
        """
        Briše sve tačke iz kolekcije.
        
        Args:
            collection_name: Naziv kolekcije
            
        Returns:
            True ako je uspešno
        """
        try:
            if not self.collection_exists(collection_name):
                logger.error(f"Kolekcija '{collection_name}' ne postoji")
                return False
            
            # Obriši sve tačke
            self.client.delete(
                collection_name=collection_name,
                points_selector=Filter(must=[])  # Prazni filter = sve tačke
            )
            
            logger.info(f"Kolekcija '{collection_name}' ociscena")
            return True
            
        except Exception as e:
            logger.error(f"Greska pri ciscenju kolekcije: {str(e)}")
            return False

# Made with Bob
