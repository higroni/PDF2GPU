"""
Setup script za Mistral-7B-Instruct sa 4-bit quantization
Autor: Bob (AI Assistant)
Datum: 2026-05-21
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import os
import sys

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
        sys.exit(1)
    
    # Test model
    test_response = input("\nŽelite li da testirate model? (y/n): ")
    if test_response.lower() == 'y':
        test_model(model, tokenizer)
    
    print("\n" + "=" * 80)
    print("SLEDEĆI KORACI:")
    print("=" * 80)
    print("1. Model je sačuvan u ./models direktorijumu")
    print("2. Možete ga koristiti u vašem RAG sistemu")
    print("3. Pogledajte MISTRAL_7B_SETUP_GUIDE.md za integraciju")
    print("\n✅ Setup završen!")


if __name__ == "__main__":
    main()

# Made with Bob
