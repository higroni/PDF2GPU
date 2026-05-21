"""
Lemmatization Service - Normalizacija srpskog teksta u osnovni oblik.

Koristi classla biblioteku za lemmatizaciju srpskog jezika.
Ovo poboljšava pretragu jer srpski ima 7 padeža.
"""

from typing import List, Optional
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class LemmatizationService:
    """Servis za lemmatizaciju srpskog teksta."""
    
    def __init__(self, language: str = "sr"):
        """
        Inicijalizuje lemmatization servis.
        
        Args:
            language: Jezik za lemmatizaciju (default: "sr" za srpski)
        """
        self.language = language
        self.nlp = None
        self._initialized = False
        
        # Pokušaj da učitaš classla
        try:
            import classla
            self.classla = classla
            logger.info(f"classla library loaded successfully for language: {language}")
        except ImportError:
            logger.warning("classla library not installed. Lemmatization will be disabled.")
            logger.warning("Install with: pip install classla")
            self.classla = None
    
    def _ensure_initialized(self):
        """Lazy initialization - učitaj model samo kada je potreban."""
        if self._initialized or self.classla is None:
            return
        
        try:
            logger.info(f"Initializing classla pipeline for {self.language}...")
            
            # Proveri da li su modeli preuzeti
            try:
                self.nlp = self.classla.Pipeline(
                    self.language,
                    processors='tokenize,pos,lemma',
                    use_gpu=False  # Koristimo CPU za lemmatizaciju (brže za male tekstove)
                )
                self._initialized = True
                logger.info("classla pipeline initialized successfully")
            except Exception as e:
                logger.warning(f"Models not downloaded. Downloading now...")
                # Preuzmi modele
                self.classla.download(self.language)
                # Pokušaj ponovo
                self.nlp = self.classla.Pipeline(
                    self.language,
                    processors='tokenize,pos,lemma',
                    use_gpu=False
                )
                self._initialized = True
                logger.info("classla pipeline initialized successfully after download")
                
        except Exception as e:
            logger.error(f"Failed to initialize classla pipeline: {e}")
            self._initialized = False
    
    def lemmatize(self, text: str) -> str:
        """
        Lemmatizuje tekst - pretvara reči u osnovni oblik.
        
        Args:
            text: Tekst za lemmatizaciju
            
        Returns:
            Lemmatizovani tekst
            
        Example:
            >>> service = LemmatizationService()
            >>> service.lemmatize("Poreskog obveznika")
            "poreski obveznik"
        """
        if not text or not text.strip():
            return text
        
        # Ako classla nije dostupna, vrati original
        if self.classla is None:
            return text
        
        # Lazy initialization
        self._ensure_initialized()
        
        if not self._initialized or self.nlp is None:
            return text
        
        try:
            # Procesuj tekst
            doc = self.nlp(text)
            
            # Ekstraktuj lemme
            lemmas = []
            for sentence in doc.sentences:
                for word in sentence.words:
                    lemmas.append(word.lemma)
            
            return " ".join(lemmas)
            
        except Exception as e:
            logger.error(f"Error during lemmatization: {e}")
            return text
    
    @lru_cache(maxsize=10000)
    def lemmatize_cached(self, text: str) -> str:
        """
        Lemmatizuje tekst sa keširanjem rezultata.
        
        Koristi LRU cache za često korišćene tekstove.
        
        Args:
            text: Tekst za lemmatizaciju
            
        Returns:
            Lemmatizovani tekst
        """
        return self.lemmatize(text)
    
    def lemmatize_batch(self, texts: List[str], use_cache: bool = True) -> List[str]:
        """
        Lemmatizuje listu tekstova.
        
        Args:
            texts: Lista tekstova za lemmatizaciju
            use_cache: Da li koristiti cache
            
        Returns:
            Lista lemmatizovanih tekstova
        """
        if use_cache:
            return [self.lemmatize_cached(text) for text in texts]
        else:
            return [self.lemmatize(text) for text in texts]
    
    def is_available(self) -> bool:
        """
        Proveri da li je lemmatizacija dostupna.
        
        Returns:
            True ako je classla instaliran i inicijalizovan
        """
        if self.classla is None:
            return False
        
        self._ensure_initialized()
        return self._initialized


# Singleton instance
_lemmatization_service: Optional[LemmatizationService] = None


def get_lemmatization_service(language: str = "sr") -> LemmatizationService:
    """
    Dobij singleton instancu lemmatization servisa.
    
    Args:
        language: Jezik za lemmatizaciju
        
    Returns:
        LemmatizationService instanca
    """
    global _lemmatization_service
    if _lemmatization_service is None:
        _lemmatization_service = LemmatizationService(language)
    return _lemmatization_service


# Made with Bob