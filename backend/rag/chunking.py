"""
Chunking strategije za deljenje teksta na delove.

Podržava različite strategije:
- Semantic: Deljenje po semantičkim celinama (optimalno za pravne dokumente)
- Fixed: Fiksna veličina sa preklapanjem
- Sentence: Deljenje po rečenicama
"""

from typing import List, Dict
import re


class ChunkingStrategy:
    """Bazna klasa za chunking strategije."""
    
    def chunk(self, text: str) -> List[Dict]:
        """
        Deli tekst na delove.
        
        Args:
            text: Tekst za deljenje
            
        Returns:
            Lista chunk-ova sa tekstom i metapodacima
        """
        raise NotImplementedError


class SemanticChunking(ChunkingStrategy):
    """
    Semantičko deljenje teksta.
    
    Deli tekst na logične celine (paragrafe, sekcije) sa preklapanjem.
    Optimalno za pravne dokumente.
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Inicijalizuje semantic chunking.
        
        Args:
            chunk_size: Ciljna veličina chunk-a u karakterima
            overlap: Preklapanje između chunk-ova u karakterima
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, text: str) -> List[Dict]:
        """
        Deli tekst na semantičke celine.
        
        Args:
            text: Tekst za deljenje
            
        Returns:
            Lista chunk-ova
        """
        # Podeli na paragrafe
        paragraphs = self._split_into_paragraphs(text)
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for paragraph in paragraphs:
            # Ako je paragraf sam po sebi veći od chunk_size, podeli ga
            if len(paragraph) > self.chunk_size:
                # Sačuvaj trenutni chunk ako postoji
                if current_chunk:
                    chunks.append({
                        'id': chunk_id,
                        'text': current_chunk.strip(),
                        'char_count': len(current_chunk),
                        'type': 'semantic'
                    })
                    chunk_id += 1
                    current_chunk = ""
                
                # Podeli veliki paragraf
                sub_chunks = self._split_large_paragraph(paragraph)
                for sub_chunk in sub_chunks:
                    chunks.append({
                        'id': chunk_id,
                        'text': sub_chunk.strip(),
                        'char_count': len(sub_chunk),
                        'type': 'semantic'
                    })
                    chunk_id += 1
            
            # Ako dodavanje paragrafa prelazi chunk_size
            elif len(current_chunk) + len(paragraph) > self.chunk_size:
                # Sačuvaj trenutni chunk
                if current_chunk:
                    chunks.append({
                        'id': chunk_id,
                        'text': current_chunk.strip(),
                        'char_count': len(current_chunk),
                        'type': 'semantic'
                    })
                    chunk_id += 1
                
                # Počni novi chunk sa preklapanjem
                if self.overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-self.overlap:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                # Dodaj paragraf u trenutni chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Dodaj poslednji chunk
        if current_chunk:
            chunks.append({
                'id': chunk_id,
                'text': current_chunk.strip(),
                'char_count': len(current_chunk),
                'type': 'semantic'
            })
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Deli tekst na paragrafe."""
        # Podeli po duplim novim linijama ili po oznakama stranica
        paragraphs = re.split(r'\n\s*\n|---\s*Stranica\s+\d+\s*---', text)
        
        # Ukloni prazne paragrafe i whitespace
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """Deli veliki paragraf na manje delove."""
        # Podeli po rečenicama
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    # Dodaj preklapanje
                    if self.overlap > 0:
                        current_chunk = current_chunk[-self.overlap:] + " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    # Rečenica je sama po sebi veća od chunk_size
                    chunks.append(sentence)
                    current_chunk = ""
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks


class FixedSizeChunking(ChunkingStrategy):
    """
    Fiksna veličina chunk-ova sa preklapanjem.
    
    Jednostavna strategija koja deli tekst na delove fiksne veličine.
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Inicijalizuje fixed size chunking.
        
        Args:
            chunk_size: Veličina chunk-a u karakterima
            overlap: Preklapanje između chunk-ova u karakterima
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, text: str) -> List[Dict]:
        """
        Deli tekst na delove fiksne veličine.
        
        Args:
            text: Tekst za deljenje
            
        Returns:
            Lista chunk-ova
        """
        chunks = []
        chunk_id = 0
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunks.append({
                'id': chunk_id,
                'text': chunk_text.strip(),
                'char_count': len(chunk_text),
                'type': 'fixed'
            })
            
            chunk_id += 1
            start = end - self.overlap
        
        return chunks


class SentenceChunking(ChunkingStrategy):
    """
    Deljenje po rečenicama.
    
    Grupiše rečenice u chunk-ove do određene veličine.
    """
    
    def __init__(self, chunk_size: int = 500, overlap_sentences: int = 1):
        """
        Inicijalizuje sentence chunking.
        
        Args:
            chunk_size: Ciljna veličina chunk-a u karakterima
            overlap_sentences: Broj rečenica za preklapanje
        """
        self.chunk_size = chunk_size
        self.overlap_sentences = overlap_sentences
    
    def chunk(self, text: str) -> List[Dict]:
        """
        Deli tekst po rečenicama.
        
        Args:
            text: Tekst za deljenje
            
        Returns:
            Lista chunk-ova
        """
        # Podeli na rečenice
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        chunk_id = 0
        current_sentences = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Ako dodavanje rečenice prelazi chunk_size
            if current_length + sentence_length > self.chunk_size and current_sentences:
                # Sačuvaj trenutni chunk
                chunk_text = ' '.join(current_sentences)
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text.strip(),
                    'char_count': len(chunk_text),
                    'sentence_count': len(current_sentences),
                    'type': 'sentence'
                })
                chunk_id += 1
                
                # Počni novi chunk sa preklapanjem
                if self.overlap_sentences > 0:
                    current_sentences = current_sentences[-self.overlap_sentences:]
                    current_length = sum(len(s) for s in current_sentences)
                else:
                    current_sentences = []
                    current_length = 0
            
            current_sentences.append(sentence)
            current_length += sentence_length
        
        # Dodaj poslednji chunk
        if current_sentences:
            chunk_text = ' '.join(current_sentences)
            chunks.append({
                'id': chunk_id,
                'text': chunk_text.strip(),
                'char_count': len(chunk_text),
                'sentence_count': len(current_sentences),
                'type': 'sentence'
            })
        
        return chunks


def get_chunking_strategy(strategy: str, **kwargs) -> ChunkingStrategy:
    """
    Factory funkcija za kreiranje chunking strategije.
    
    Args:
        strategy: Tip strategije ('semantic', 'fixed', 'sentence')
        **kwargs: Parametri za strategiju
        
    Returns:
        ChunkingStrategy instanca
        
    Raises:
        ValueError: Ako strategija nije podržana
    """
    strategies = {
        'semantic': SemanticChunking,
        'fixed': FixedSizeChunking,
        'sentence': SentenceChunking
    }
    
    if strategy not in strategies:
        raise ValueError(f"Nepoznata strategija: {strategy}. Dostupne: {list(strategies.keys())}")
    
    return strategies[strategy](**kwargs)

# Made with Bob
