# Mistral-7B-Instruct Setup Guide - 4-bit Quantization

## Pregled

Ovaj vodič pokazuje kako da preuzmete i konfigurišete Mistral-7B-Instruct model sa 4-bit quantization-om za vaš RAG sistem.

---

## Opcija 1: Automatsko Preuzimanje (PREPORUČENO)

Model se automatski preuzima pri prvom korišćenju. Evo kompletnog Python script-a:

### 1.1 Instalacija Potrebnih Paketa

```bash
# Instalirajte potrebne biblioteke
pip install transformers>=4.35.0
pip install accelerate>=0.24.0
pip install bitsandbytes>=0.41.0
pip install torch>=2.1.0
```

**Napomena**: `bitsandbytes` zahteva CUDA. Ako imate problema, instalirajte:
```bash
pip install bitsandbytes-windows  # Za Windows
```

### 1.2 Python Script za Preuzimanje i Testiranje

Kreirajte fajl `setup_mistral.py`:

```python
"""
Setup script za Mistral-7B-Instruct sa 4-bit quantization
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import os

def setup_mistral_7b(model_name="mistralai/Mistral-7B-Instruct-v0.2", cache_dir="./models"):
    """
    Preuzima i konfiguriše Mistral-7B model sa 4-bit quantization
    
    Args:
        model_name: HuggingFace model ID
        cache_dir: Direktorijum za čuvanje modela
    """
    print("=" * 80)
    print("MISTRAL-7B-INSTRUCT SETUP - 4-BIT QUANTIZATION")
    print("=" * 80)
    
    # Proveri CUDA dostupnost
    if not torch.cuda.is_available():
        print("❌ UPOZORENJE: CUDA nije dostupna!")
        print("   Model će raditi na CPU-u (VEOMA SPORO)")
        print("   Instalirajte CUDA toolkit: https://developer.nvidia.com/cuda-downloads")
        response = input("\nNastaviti sa CPU? (y/n): ")
        if response.lower() != 'y':
            return None, None
    else:
        print(f"✅ CUDA dostupna: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Kreiraj cache direktorijum
    os.makedirs(cache_dir, exist_ok=True)
    
    print(f"\n📥 Preuzimanje modela: {model_name}")
    print(f"   Cache direktorijum: {cache_dir}")
    print(f"   Veličina: ~14 GB (originalni model)")
    print(f"   Posle quantization-a: ~3.5 GB u memoriji")
    print("\n⏳ Ovo može potrajati 10-30 minuta (zavisno od internet brzine)...")
    
    # Konfiguriši 4-bit quantization
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    try:
        # Preuzmi tokenizer
        print("\n1️⃣ Preuzimanje tokenizer-a...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True
        )
        print("   ✅ Tokenizer preuzet")
        
        # Preuzmi i quantize model
        print("\n2️⃣ Preuzimanje i quantization modela...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto",
            cache_dir=cache_dir,
            trust_remote_code=True,
            torch_dtype=torch.float16
        )
        print("   ✅ Model preuzet i quantized")
        
        # Proveri memoriju
        if torch.cuda.is_available():
            memory_used = torch.cuda.memory_allocated() / 1024**3
            print(f"\n📊 GPU memorija korišćena: {memory_used:.2f} GB")
        
        print("\n" + "=" * 80)
        print("✅ SETUP USPEŠAN!")
        print("=" * 80)
        
        return model, tokenizer
        
    except Exception as e:
        print(f"\n❌ GREŠKA: {e}")
        print("\nMoguća rešenja:")
        print("1. Proverite internet konekciju")
        print("2. Proverite da li imate dovoljno prostora na disku (~15 GB)")
        print("3. Proverite CUDA instalaciju")
        print("4. Pokušajte ponovo (ponekad HuggingFace ima timeout)")
        return None, None


def test_model(model, tokenizer):
    """
    Testira model sa jednostavnim promptom
    """
    print("\n" + "=" * 80)
    print("TESTIRANJE MODELA")
    print("=" * 80)
    
    # Test prompt
    prompt = """Ti si AI asistent. Odgovori kratko i jasno.

Pitanje: Šta je poreski obveznik?

Odgovor:"""
    
    print(f"\n📝 Test prompt:\n{prompt}")
    print("\n⏳ Generisanje odgovora...")
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.1,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Izvuci samo odgovor (posle "Odgovor:")
    if "Odgovor:" in response:
        answer = response.split("Odgovor:")[-1].strip()
    else:
        answer = response
    
    print(f"\n💬 Odgovor:\n{answer}")
    print("\n" + "=" * 80)
    print("✅ TEST USPEŠAN!")
    print("=" * 80)


def main():
    """
    Glavni setup proces
    """
    # Setup model
    model, tokenizer = setup_mistral_7b()
    
    if model is None:
        print("\n❌ Setup nije uspeo. Pokušajte ponovo.")
        return
    
    # Test model
    test_response = input("\nŽelite li da testirate model? (y/n): ")
    if test_response.lower() == 'y':
        test_model(model, tokenizer)
    
    print("\n" + "=" * 80)
    print("SLEDEĆI KORACI:")
    print("=" * 80)
    print("1. Model je sačuvan u ./models direktorijumu")
    print("2. Možete ga koristiti u vašem RAG sistemu")
    print("3. Primer koda za integraciju:")
    print("""
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        "mistralai/Mistral-7B-Instruct-v0.2",
        quantization_config=quantization_config,
        device_map="auto",
        cache_dir="./models"
    )
    
    tokenizer = AutoTokenizer.from_pretrained(
        "mistralai/Mistral-7B-Instruct-v0.2",
        cache_dir="./models"
    )
    """)
    print("\n✅ Setup završen!")


if __name__ == "__main__":
    main()
```

### 1.3 Pokretanje Setup Script-a

```bash
# Pokrenite script
python setup_mistral.py
```

**Šta će se desiti:**
1. Provera CUDA dostupnosti
2. Kreiranje `./models` direktorijuma
3. Preuzimanje modela sa HuggingFace (~14 GB)
4. Automatski 4-bit quantization
5. Test generisanja odgovora

**Vreme**: 10-30 minuta (zavisno od internet brzine)

---

## Opcija 2: Ručno Preuzimanje (Ako imate sporu internet vezu)

### 2.1 Preuzimanje sa HuggingFace

1. Idite na: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
2. Kliknite na "Files and versions"
3. Preuzmite sledeće fajlove:
   - `config.json`
   - `tokenizer.json`
   - `tokenizer_config.json`
   - `special_tokens_map.json`
   - `model-00001-of-00003.safetensors`
   - `model-00002-of-00003.safetensors`
   - `model-00003-of-00003.safetensors`
   - `model.safetensors.index.json`

4. Stavite ih u: `./models/mistralai/Mistral-7B-Instruct-v0.2/`

### 2.2 Učitavanje Lokalnog Modela

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# Učitaj iz lokalnog direktorijuma
model = AutoModelForCausalLM.from_pretrained(
    "./models/mistralai/Mistral-7B-Instruct-v0.2",
    quantization_config=quantization_config,
    device_map="auto",
    local_files_only=True  # Koristi samo lokalne fajlove
)

tokenizer = AutoTokenizer.from_pretrained(
    "./models/mistralai/Mistral-7B-Instruct-v0.2",
    local_files_only=True
)
```

---

## Opcija 3: Korišćenje Pre-Quantized Modela (NAJBRŽE)

Možete preuzeti već quantized model (manje preuzimanje):

```python
# GGUF format (za llama.cpp)
# Preuzmi sa: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF

# Ili AWQ quantized (za vLLM)
model_name = "TheBloke/Mistral-7B-Instruct-v0.2-AWQ"

from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
```

---

## Integracija u Vaš RAG Sistem

### Korak 1: Kreirajte `backend/llm/mistral_service.py`

```python
"""
Mistral-7B LLM Service za RAG sistem
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MistralLLMService:
    """Service za Mistral-7B-Instruct model"""
    
    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.2", cache_dir: str = "./models"):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Učitaj model sa 4-bit quantization"""
        logger.info(f"Loading Mistral-7B model: {self.model_name}")
        
        # Quantization config
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            trust_remote_code=True
        )
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=quantization_config,
            device_map="auto",
            cache_dir=self.cache_dir,
            trust_remote_code=True,
            torch_dtype=torch.float16
        )
        
        logger.info("Model loaded successfully")
    
    def generate_answer(
        self,
        question: str,
        context: str,
        max_tokens: int = 512,
        temperature: float = 0.1,
        top_p: float = 0.9
    ) -> str:
        """
        Generiši odgovor na osnovu pitanja i konteksta
        
        Args:
            question: Korisničko pitanje
            context: Relevantni kontekst iz dokumenata
            max_tokens: Maksimalan broj tokena u odgovoru
            temperature: Temperatura za sampling (niža = deterministički)
            top_p: Nucleus sampling parametar
        
        Returns:
            Generisani odgovor
        """
        # Kreiraj prompt
        prompt = f"""Ti si AI asistent specijalizovan za srpsko zakonodavstvo i pravne propise.

PRAVILA:
1. Odgovaraj ISKLJUČIVO na osnovu dostavljenog konteksta
2. Ako informacija nije u kontekstu, reci "Na osnovu dostavljenih dokumenata, ne mogu dati precizan odgovor"
3. Uvek navedi izvor (naziv zakona, broj člana)
4. Koristi preciznu pravnu terminologiju
5. Odgovaraj na srpskom jeziku, gramatički ispravno

KONTEKST:
{context}

PITANJE: {question}

ODGOVOR:"""
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Izvuci samo odgovor (posle "ODGOVOR:")
        if "ODGOVOR:" in response:
            answer = response.split("ODGOVOR:")[-1].strip()
        else:
            answer = response
        
        return answer


# Singleton instance
_mistral_service: Optional[MistralLLMService] = None


def get_mistral_service() -> MistralLLMService:
    """Get singleton instance of Mistral service"""
    global _mistral_service
    if _mistral_service is None:
        _mistral_service = MistralLLMService()
    return _mistral_service
```

### Korak 2: Integriši u RAG Engine

U `backend/rag/rag_engine.py`, dodaj opciju za Mistral:

```python
from backend.llm.mistral_service import get_mistral_service

class RAGEngine:
    def __init__(self, use_mistral: bool = False):
        self.use_mistral = use_mistral
        if use_mistral:
            self.llm_service = get_mistral_service()
    
    def generate_answer(self, question: str, context_chunks: List[str]) -> str:
        if self.use_mistral:
            context = "\n\n".join(context_chunks)
            return self.llm_service.generate_answer(question, context)
        else:
            # Koristi Ollama ili drugi LLM
            return self.generate_with_ollama(question, context_chunks)
```

---

## Troubleshooting

### Problem 1: "CUDA out of memory"

**Rešenje:**
```python
# Smanji batch size ili max_tokens
outputs = model.generate(
    **inputs,
    max_new_tokens=256,  # Smanji sa 512
    batch_size=1
)

# Ili očisti cache
torch.cuda.empty_cache()
```

### Problem 2: "bitsandbytes not found"

**Rešenje:**
```bash
# Za Windows
pip uninstall bitsandbytes
pip install bitsandbytes-windows

# Za Linux
pip install bitsandbytes
```

### Problem 3: Sporo generisanje

**Rešenje:**
```python
# Koristi flash attention (ako je dostupno)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
    device_map="auto",
    attn_implementation="flash_attention_2"  # Brže
)
```

### Problem 4: Model ne preuzima

**Rešenje:**
```bash
# Postavite HuggingFace token (ako je potrebno)
huggingface-cli login

# Ili koristite environment variable
export HF_TOKEN="your_token_here"
```

---

## Provera Instalacije

```python
# Test script
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA version:", torch.version.cuda)
    print("GPU:", torch.cuda.get_device_name(0))

# Proveri bitsandbytes
try:
    import bitsandbytes
    print("bitsandbytes version:", bitsandbytes.__version__)
except ImportError:
    print("bitsandbytes NOT installed")
```

---

## Dodatni Resursi

- **HuggingFace Model**: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
- **Dokumentacija**: https://huggingface.co/docs/transformers/main/en/model_doc/mistral
- **bitsandbytes**: https://github.com/TimDettmers/bitsandbytes
- **Quantization Guide**: https://huggingface.co/docs/transformers/main/en/quantization

---

**Napomena**: Prvi put kada pokrenete model, preuzimanje može potrajati. Posle toga, model se učitava iz cache-a (~10-30 sekundi).