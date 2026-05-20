"""
Models Router
API endpoints za dinamičko otkrivanje dostupnih modela
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import subprocess
import json
from pathlib import Path

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/llm", response_model=List[Dict[str, Any]])
async def get_available_llm_models():
    """
    Vraća listu dostupnih LLM modela iz Ollama
    
    Returns:
        List[Dict]: Lista modela sa name, size, modified
    """
    try:
        # Pozovi ollama list komandu
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get Ollama models: {result.stderr}"
            )
        
        # Parse output
        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:  # Header + at least one model
            return []
        
        models = []
        for line in lines[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 3:
                models.append({
                    "name": parts[0],
                    "size": parts[1] if len(parts) > 1 else "unknown",
                    "modified": " ".join(parts[2:]) if len(parts) > 2 else "unknown"
                })
        
        return models
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Ollama request timed out")
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Ollama is not installed or not in PATH"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting LLM models: {str(e)}")


@router.get("/embeddings", response_model=List[Dict[str, Any]])
async def get_available_embedding_models():
    """
    Vraća listu dostupnih embedding modela
    
    Returns:
        List[Dict]: Lista modela sa name, source, dimensions
    """
    try:
        from sentence_transformers import SentenceTransformer
        
        # Hardcoded lista popularnih modela koji su testirani
        # U produkciji bi ovo moglo da se dinamički detektuje iz cache-a
        known_models = [
            {
                "name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "source": "sentence-transformers",
                "dimensions": 384,
                "description": "Multilingual model, good for Serbian"
            },
            {
                "name": "sentence-transformers/all-MiniLM-L6-v2",
                "source": "sentence-transformers",
                "dimensions": 384,
                "description": "Fast and efficient, English-focused"
            },
            {
                "name": "sentence-transformers/all-mpnet-base-v2",
                "source": "sentence-transformers",
                "dimensions": 768,
                "description": "High quality, English-focused"
            },
            {
                "name": "BAAI/bge-small-en-v1.5",
                "source": "huggingface",
                "dimensions": 384,
                "description": "BGE small model, good performance"
            },
            {
                "name": "BAAI/bge-base-en-v1.5",
                "source": "huggingface",
                "dimensions": 768,
                "description": "BGE base model, better quality"
            }
        ]
        
        # Proveri koji su instalirani
        installed_models = []
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        if cache_dir.exists():
            for model_info in known_models:
                model_name = model_info["name"]
                # Proveri da li postoji u cache-u
                model_cache_name = "models--" + model_name.replace("/", "--")
                if (cache_dir / model_cache_name).exists():
                    model_info["installed"] = True
                else:
                    model_info["installed"] = False
                installed_models.append(model_info)
        else:
            # Ako nema cache-a, vrati sve kao neinstalirane
            for model_info in known_models:
                model_info["installed"] = False
                installed_models.append(model_info)
        
        return installed_models
        
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="sentence-transformers library is not installed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting embedding models: {str(e)}"
        )


@router.get("/rerankers", response_model=List[Dict[str, Any]])
async def get_available_reranker_models():
    """
    Vraća listu dostupnih reranker modela
    
    Returns:
        List[Dict]: Lista modela sa name, source, description
    """
    try:
        # Hardcoded lista popularnih reranker modela
        known_models = [
            {
                "name": "cross-encoder/ms-marco-MiniLM-L-6-v2",
                "source": "sentence-transformers",
                "description": "Fast cross-encoder for reranking"
            },
            {
                "name": "cross-encoder/ms-marco-MiniLM-L-12-v2",
                "source": "sentence-transformers",
                "description": "Better quality cross-encoder"
            },
            {
                "name": "BAAI/bge-reranker-base",
                "source": "huggingface",
                "description": "BGE reranker, good performance"
            },
            {
                "name": "BAAI/bge-reranker-large",
                "source": "huggingface",
                "description": "BGE reranker, best quality"
            }
        ]
        
        # Proveri koji su instalirani
        installed_models = []
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        if cache_dir.exists():
            for model_info in known_models:
                model_name = model_info["name"]
                model_cache_name = "models--" + model_name.replace("/", "--")
                if (cache_dir / model_cache_name).exists():
                    model_info["installed"] = True
                else:
                    model_info["installed"] = False
                installed_models.append(model_info)
        else:
            for model_info in known_models:
                model_info["installed"] = False
                installed_models.append(model_info)
        
        return installed_models
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting reranker models: {str(e)}"
        )


@router.post("/install/{model_type}/{model_name:path}")
async def install_model(model_type: str, model_name: str):
    """
    Instalira model (samo za Ollama LLM modele)
    
    Args:
        model_type: Tip modela (llm, embeddings, rerankers)
        model_name: Ime modela
        
    Returns:
        Dict: Status instalacije
    """
    if model_type == "llm":
        try:
            # Pokreni ollama pull
            result = subprocess.run(
                ["ollama", "pull", model_name],
                encoding='utf-8',
                errors='replace',
                capture_output=True,
                text=True,
                timeout=300  # 5 minuta timeout
            )
            
            if result.returncode != 0:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to install model: {result.stderr}"
                )
            
            return {
                "status": "success",
                "message": f"Model {model_name} installed successfully",
                "output": result.stdout
            }
            
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=504,
                detail="Model installation timed out"
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail="Ollama is not installed or not in PATH"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error installing model: {str(e)}"
            )
    
    elif model_type in ["embeddings", "rerankers"]:
        # Za HuggingFace modele, samo vrati instrukcije
        return {
            "status": "info",
            "message": f"HuggingFace models are downloaded automatically on first use",
            "instructions": f"The model '{model_name}' will be downloaded when you first use it in an evaluation"
        }
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model type: {model_type}"
        )


# Made with Bob