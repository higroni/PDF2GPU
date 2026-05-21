"""
Legal Metrics - Specijalizovane metrike za pravnu tematiku.

Ove metrike su dizajnirane specifično za evaluaciju RAG sistema
koji radi sa pravnim dokumentima na srpskom jeziku.
"""

from typing import List, Set, Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)


# Whitelist pravnih termina (proširiti po potrebi)
LEGAL_TERMS = {
    # Poreski termini
    "obveznik", "poreska", "osnovica", "stopa", "prijava",
    "rezident", "nerezident", "dohodak", "prihod", "rashod",
    "oporezivanje", "poreska", "godišnji", "mesečni", "kvartalni",
    "akontacija", "konačan", "porez", "doprinosi", "oslobođenje",
    
    # Pravni termini
    "zakon", "član", "stav", "tačka", "alineja", "propis",
    "uredba", "pravilnik", "odluka", "rešenje", "presuda",
    "lice", "fizičko", "pravno", "preduzetnik", "društvo",
    
    # Proceduralni termini
    "podnošenje", "dostavljanje", "rok", "prijava", "izveštaj",
    "evidencija", "knjiga", "račun", "faktura", "dokument",
    
    # Dodatni termini (dodati više po potrebi)
    "obaveza", "pravo", "dužnost", "odgovornost", "sankcija",
    "kazna", "prekršaj", "krivica", "naknada", "šteta"
}


def extract_legal_terms(text: str, legal_terms_set: Optional[Set[str]] = None) -> Set[str]:
    """
    Ekstraktuje pravne termine iz teksta.
    
    Args:
        text: Tekst za analizu
        legal_terms_set: Set pravnih termina (default: LEGAL_TERMS)
        
    Returns:
        Set pronađenih pravnih termina
    """
    if legal_terms_set is None:
        legal_terms_set = LEGAL_TERMS
    
    # Normalizuj tekst (lowercase)
    text_lower = text.lower()
    
    # Pronađi sve pravne termine
    found_terms = set()
    for term in legal_terms_set:
        # Proveri da li je term prisutan kao cela reč
        pattern = r'\b' + re.escape(term) + r'\w*\b'
        if re.search(pattern, text_lower):
            found_terms.add(term)
    
    return found_terms


def extract_article_references(text: str) -> Set[str]:
    """
    Ekstraktuje reference na članke zakona iz teksta.
    
    Prepoznaje formate:
    - "Član 15"
    - "čl. 15"
    - "član 15, stav 2"
    - "Člana 15"
    
    Args:
        text: Tekst za analizu
        
    Returns:
        Set pronađenih referenci (normalizovano na "Član X")
    """
    references = set()
    
    # Pattern za različite formate
    patterns = [
        r'\bčlan[a]?\s+(\d+)',  # član 15, člana 15
        r'\bčl\.\s*(\d+)',       # čl. 15
        r'\bČlan[a]?\s+(\d+)',  # Član 15, Člana 15
        r'\bČl\.\s*(\d+)',       # Čl. 15
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            article_num = match.group(1)
            # Normalizuj na "Član X"
            references.add(f"Član {article_num}")
    
    return references


def calculate_legal_term_accuracy(
    generated: str,
    reference: str,
    legal_terms_set: Optional[Set[str]] = None
) -> Dict[str, float]:
    """
    Računa tačnost korišćenja pravnih termina.
    
    Args:
        generated: Generisani odgovor
        reference: Referentni odgovor
        legal_terms_set: Set pravnih termina
        
    Returns:
        Dict sa precision, recall i f1 score
    """
    gen_terms = extract_legal_terms(generated, legal_terms_set)
    ref_terms = extract_legal_terms(reference, legal_terms_set)
    
    if not gen_terms and not ref_terms:
        # Nema pravnih termina ni u jednom
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    
    if not gen_terms:
        # Generisani nema termine, a referentni ima
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    if not ref_terms:
        # Referentni nema termine, a generisani ima (false positives)
        return {"precision": 0.0, "recall": 1.0, "f1": 0.0}
    
    # Izračunaj precision i recall
    correct = len(gen_terms & ref_terms)
    precision = correct / len(gen_terms) if gen_terms else 0.0
    recall = correct / len(ref_terms) if ref_terms else 0.0
    
    # F1 score
    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def calculate_citation_accuracy(generated: str, reference: str) -> float:
    """
    Računa tačnost citiranja članaka zakona.
    
    Args:
        generated: Generisani odgovor
        reference: Referentni odgovor
        
    Returns:
        Accuracy score (0.0 - 1.0)
    """
    gen_citations = extract_article_references(generated)
    ref_citations = extract_article_references(reference)
    
    if not ref_citations:
        # Nema citata u referenci
        if not gen_citations:
            # Nema citata ni u generisanom - tačno
            return 1.0
        else:
            # Generisani ima citate, a referentni nema - netačno
            return 0.0
    
    if not gen_citations:
        # Referentni ima citate, a generisani nema
        return 0.0
    
    # Izračunaj accuracy
    correct = len(gen_citations & ref_citations)
    total = len(ref_citations)
    
    return correct / total if total > 0 else 0.0


def calculate_completeness_score(generated: str, reference: str) -> float:
    """
    Računa da li odgovor pokriva sve aspekte pitanja.
    
    Jednostavna heuristika bazirana na pokrivanju rečenica.
    
    Args:
        generated: Generisani odgovor
        reference: Referentni odgovor
        
    Returns:
        Completeness score (0.0 - 1.0)
    """
    # Podeli na rečenice (jednostavno - po tački)
    ref_sentences = [s.strip() for s in reference.split('.') if s.strip()]
    gen_sentences = [s.strip() for s in generated.split('.') if s.strip()]
    
    if not ref_sentences:
        return 1.0
    
    # Proveri koliko referentnih rečenica je pokriveno
    covered = 0
    for ref_sent in ref_sentences:
        # Jednostavna heuristika: proveri da li su ključne reči pokrivene
        ref_words = set(ref_sent.lower().split())
        
        for gen_sent in gen_sentences:
            gen_words = set(gen_sent.lower().split())
            # Ako je >50% reči pokriveno, smatramo da je rečenica pokrivena
            overlap = len(ref_words & gen_words)
            if overlap / len(ref_words) > 0.5:
                covered += 1
                break
    
    return covered / len(ref_sentences) if ref_sentences else 0.0


def calculate_all_legal_metrics(
    generated: str,
    reference: str,
    legal_terms_set: Optional[Set[str]] = None
) -> Dict[str, float]:
    """
    Računa sve pravne metrike odjednom.
    
    Args:
        generated: Generisani odgovor
        reference: Referentni odgovor
        legal_terms_set: Set pravnih termina
        
    Returns:
        Dict sa svim metrikama
    """
    term_accuracy = calculate_legal_term_accuracy(generated, reference, legal_terms_set)
    citation_accuracy = calculate_citation_accuracy(generated, reference)
    completeness = calculate_completeness_score(generated, reference)
    
    return {
        "legal_term_precision": term_accuracy["precision"],
        "legal_term_recall": term_accuracy["recall"],
        "legal_term_f1": term_accuracy["f1"],
        "citation_accuracy": citation_accuracy,
        "completeness_score": completeness
    }


# Made with Bob