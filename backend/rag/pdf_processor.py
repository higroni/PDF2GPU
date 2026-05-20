"""
PDF Processor - Ekstrakcija teksta iz PDF dokumenata.

Koristi PyMuPDF (fitz) za najbolje performanse i podršku za ćirilicu.
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Optional
import re
from .cyrillic_to_latin import convert_to_latin, is_cyrillic


class PDFProcessor:
    """Procesor za ekstrakciju teksta iz PDF dokumenata."""
    
    def __init__(self, convert_cyrillic: bool = True):
        """
        Inicijalizuje PDF processor.
        
        Args:
            convert_cyrillic: Da li konvertovati ćirilicu u latinicu
        """
        self.convert_cyrillic = convert_cyrillic
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Ekstraktuje tekst iz PDF dokumenta.
        
        Args:
            pdf_path: Putanja do PDF fajla
            
        Returns:
            Ekstraktovani tekst
            
        Raises:
            FileNotFoundError: Ako PDF fajl ne postoji
            Exception: Ako dođe do greške pri čitanju PDF-a
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF fajl ne postoji: {pdf_path}")
        
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                
                if page_text:
                    text += f"\n--- Stranica {page_num + 1} ---\n"
                    text += page_text
            
            doc.close()
            
            # Konvertuj ćirilicu u latinicu ako je potrebno
            if self.convert_cyrillic and is_cyrillic(text):
                text = convert_to_latin(text)
            
            return text
            
        except Exception as e:
            raise Exception(f"Greška pri čitanju PDF-a: {str(e)}")
    
    def extract_with_metadata(self, pdf_path: str) -> Dict:
        """
        Ekstraktuje tekst i metadata iz PDF dokumenta.
        
        Args:
            pdf_path: Putanja do PDF fajla
            
        Returns:
            Dict sa tekstom i metapodacima
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF fajl ne postoji: {pdf_path}")
        
        try:
            doc = fitz.open(pdf_path)
            
            # Ekstraktuj metadata
            metadata = {
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'keywords': doc.metadata.get('keywords', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', ''),
                'page_count': len(doc)
            }
            
            # Ekstraktuj tekst
            text = ""
            pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                
                if page_text:
                    # Konvertuj ćirilicu ako je potrebno
                    if self.convert_cyrillic and is_cyrillic(page_text):
                        page_text = convert_to_latin(page_text)
                    
                    pages.append({
                        'page_number': page_num + 1,
                        'text': page_text,
                        'char_count': len(page_text)
                    })
                    
                    text += f"\n--- Stranica {page_num + 1} ---\n"
                    text += page_text
            
            doc.close()
            
            return {
                'text': text,
                'metadata': metadata,
                'pages': pages,
                'total_chars': len(text),
                'total_pages': len(pages)
            }
            
        except Exception as e:
            raise Exception(f"Greška pri čitanju PDF-a: {str(e)}")
    
    def extract_sections(self, pdf_path: str) -> List[Dict]:
        """
        Ekstraktuje tekst podeljen na sekcije (po naslovima).
        
        Args:
            pdf_path: Putanja do PDF fajla
            
        Returns:
            Lista sekcija sa naslovom i sadržajem
        """
        text = self.extract_text(pdf_path)
        return self._parse_sections(text)
    
    def _parse_sections(self, text: str) -> List[Dict]:
        """
        Parsira tekst i deli ga na sekcije po naslovima.
        
        Naslov = linija gde je većina karaktera velika slova (>70%)
        
        Args:
            text: Tekst dokumenta
            
        Returns:
            Lista sekcija
        """
        lines = text.split('\n')
        sections = []
        current_section = None
        current_content = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Preskoči prazne linije i oznake stranica
            if not line_stripped or line_stripped.startswith('---'):
                continue
            
            # Preskoči brojeve stranica
            if re.match(r'^\d+\s*\|\s*Стр\.$', line_stripped):
                continue
            if re.match(r'^Стр\.\s*\|\s*\d+$', line_stripped):
                continue
            
            # Proveri da li je naslov
            if self._is_heading(line_stripped):
                # Sačuvaj prethodnu sekciju
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'type': 'section'
                    })
                
                # Počni novu sekciju
                current_section = line_stripped
                current_content = []
            else:
                # Dodaj u trenutnu sekciju
                if current_section:
                    current_content.append(line_stripped)
        
        # Sačuvaj poslednju sekciju
        if current_section and current_content:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip(),
                'type': 'section'
            })
        
        return sections
    
    def _is_heading(self, line: str) -> bool:
        """
        Proverava da li je linija naslov.
        
        Naslov = većina karaktera je velika slova (>70%)
        
        Args:
            line: Linija teksta
            
        Returns:
            True ako je naslov, False inače
        """
        if len(line) < 10:  # Preskoči kratke linije
            return False
        
        # Ukloni brojeve i interpunkciju
        letters = [c for c in line if c.isalpha()]
        if not letters:
            return False
        
        # Proveri procenat velikih slova
        uppercase_count = sum(1 for c in letters if c.isupper())
        percentage = uppercase_count / len(letters)
        
        return percentage > 0.7
    
    def get_statistics(self, pdf_path: str) -> Dict:
        """
        Vraća statistiku o PDF dokumentu.
        
        Args:
            pdf_path: Putanja do PDF fajla
            
        Returns:
            Dict sa statistikom
        """
        data = self.extract_with_metadata(pdf_path)
        text = data['text']
        
        return {
            'file_name': Path(pdf_path).name,
            'file_size': Path(pdf_path).stat().st_size,
            'page_count': data['total_pages'],
            'total_chars': data['total_chars'],
            'total_words': len(text.split()),
            'total_lines': len(text.splitlines()),
            'is_cyrillic': is_cyrillic(text),
            'metadata': data['metadata']
        }

# Made with Bob
