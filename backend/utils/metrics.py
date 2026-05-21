"""
Metrics Utilities
Funkcije za računanje evaluacionih metrika
"""
import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalizuje tekst za poređenje
    
    Args:
        text: Tekst za normalizaciju
        
    Returns:
        Normalizovani tekst
    """
    # Lowercase
    text = text.lower()
    
    # Ukloni višestruke razmake
    text = re.sub(r'\s+', ' ', text)
    
    # Ukloni interpunkciju (opciono, može se konfigurisati)
    # text = re.sub(r'[^\w\s]', '', text)
    
    # Trim
    text = text.strip()
    
    return text


def calculate_bleu_score(reference: str, hypothesis: str) -> float:
    """
    Računa BLEU score između reference i hypothesis
    
    Args:
        reference: Očekivani odgovor
        hypothesis: Generisani odgovor
        
    Returns:
        BLEU score (0.0 - 1.0)
    """
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction  # type: ignore
        
        # Normalizuj tekstove
        reference = normalize_text(reference)
        hypothesis = normalize_text(hypothesis)
        
        # Tokenizuj
        reference_tokens = reference.split()
        hypothesis_tokens = hypothesis.split()
        
        # Računaj BLEU sa smoothing-om (za kratke tekstove)
        smoothing = SmoothingFunction().method1
        score = sentence_bleu(
            [reference_tokens],
            hypothesis_tokens,
            smoothing_function=smoothing
        )
        
        # sentence_bleu vraća float direktno
        return score
        
    except ImportError:
        logger.error("NLTK nije instaliran. Instaliraj sa: pip install nltk")
        return 0.0
    except Exception as e:
        logger.error(f"Error calculating BLEU score: {e}")
        return 0.0


def calculate_rouge_scores(reference: str, hypothesis: str) -> Dict[str, float]:
    """
    Računa ROUGE scores (ROUGE-1, ROUGE-2, ROUGE-L)
    
    Args:
        reference: Očekivani odgovor
        hypothesis: Generisani odgovor
        
    Returns:
        Dict sa ROUGE scores
    """
    try:
        from rouge_score import rouge_scorer  # type: ignore
        
        # Normalizuj tekstove
        reference = normalize_text(reference)
        hypothesis = normalize_text(hypothesis)
        
        # Kreiraj scorer
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=False)
        
        # Računaj scores
        scores = scorer.score(reference, hypothesis)
        
        return {
            'rouge_1': float(scores['rouge1'].fmeasure),
            'rouge_2': float(scores['rouge2'].fmeasure),
            'rouge_l': float(scores['rougeL'].fmeasure)
        }
        
    except ImportError:
        logger.error("rouge-score nije instaliran. Instaliraj sa: pip install rouge-score")
        return {'rouge_1': 0.0, 'rouge_2': 0.0, 'rouge_l': 0.0}
    except Exception as e:
        logger.error(f"Error calculating ROUGE scores: {e}")
        return {'rouge_1': 0.0, 'rouge_2': 0.0, 'rouge_l': 0.0}


def calculate_bert_score(reference: str, hypothesis: str, lang: str = "en") -> Dict[str, float]:
    """
    Računa BERTScore (precision, recall, F1)
    
    Args:
        reference: Očekivani odgovor
        hypothesis: Generisani odgovor
        lang: Jezik (default: "en", može biti "sr" za srpski ako postoji model)
        
    Returns:
        Dict sa BERTScore metrikama
    """
    try:
        from bert_score import score  # type: ignore
        
        # Use CUDA if available, otherwise CPU
        device = 'cuda' if _is_cuda_available() else 'cpu'
        
        # Računaj BERTScore - will raise error if GPU fails
        P, R, F1 = score(
            [hypothesis],
            [reference],
            lang=lang,
            verbose=False,
            device=device
        )
        
        return {
            'precision': float(P[0]),
            'recall': float(R[0]),
            'f1': float(F1[0])
        }
        
    except ImportError:
        logger.error("bert-score nije instaliran. Instaliraj sa: pip install bert-score")
        return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
    except Exception as e:
        logger.error(f"Error calculating BERTScore: {e}")
        raise  # Re-raise the error to stop execution
        return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}


def _is_cuda_available() -> bool:
    """Proveri da li je CUDA dostupan"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def calculate_all_metrics(reference: str, hypothesis: str) -> Dict[str, Any]:
    """
    Računa sve metrike odjednom
    
    Args:
        reference: Očekivani odgovor
        hypothesis: Generisani odgovor
        
    Returns:
        Dict sa svim metrikama
    """
    metrics = {}
    
    # BLEU
    try:
        metrics['bleu_score'] = calculate_bleu_score(reference, hypothesis)
    except Exception as e:
        logger.error(f"BLEU calculation failed: {e}")
        metrics['bleu_score'] = None
    
    # ROUGE
    try:
        rouge_scores = calculate_rouge_scores(reference, hypothesis)
        metrics.update(rouge_scores)
    except Exception as e:
        logger.error(f"ROUGE calculation failed: {e}")
        metrics['rouge_1'] = None
        metrics['rouge_2'] = None
        metrics['rouge_l'] = None
    
    # BERTScore
    try:
        bert_scores = calculate_bert_score(reference, hypothesis)
        metrics['bert_score_precision'] = bert_scores['precision']
        metrics['bert_score_recall'] = bert_scores['recall']
        metrics['bert_score_f1'] = bert_scores['f1']
    except Exception as e:
        logger.error(f"BERTScore calculation failed: {e}")
        metrics['bert_score_precision'] = None
        metrics['bert_score_recall'] = None
        metrics['bert_score_f1'] = None
    
    return metrics


def calculate_exact_match(reference: str, hypothesis: str) -> bool:
    """
    Proveri da li je exact match (nakon normalizacije)
    
    Args:
        reference: Očekivani odgovor
        hypothesis: Generisani odgovor
        
    Returns:
        True ako je exact match
    """
    return normalize_text(reference) == normalize_text(hypothesis)


def calculate_word_overlap(reference: str, hypothesis: str) -> float:
    """
    Računa procenat preklapanja reči
    
    Args:
        reference: Očekivani odgovor
        hypothesis: Generisani odgovor
        
    Returns:
        Procenat preklapanja (0.0 - 1.0)
    """
    ref_words = set(normalize_text(reference).split())
    hyp_words = set(normalize_text(hypothesis).split())
    
    if not ref_words:
        return 0.0
    
    overlap = len(ref_words & hyp_words)
    return overlap / len(ref_words)


# Made with Bob