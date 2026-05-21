# Mistral Setup sa Ollama - Brzi Vodič

## Zašto Ollama?

✅ **Mnogo jednostavnije** - jedna komanda za preuzimanje
✅ **Automatski quantization** - Ollama automatski optimizuje model
✅ **Automatska integracija** - Pojavljuje se u dropdown listi
✅ **Manje memorije** - Ollama efikasnije upravlja memorijom
✅ **Brže** - Optimizovano za lokalno izvršavanje

---

## Korak 1: Preuzmite Mistral sa Ollama

Otvorite terminal i pokrenite:

```bash
ollama pull mistral
```

**To je sve!** 🎉

Ollama će:
1. Preuzeti Mistral-7B-Instruct model (~4.1 GB)
2. Automatski ga quantize-ovati (4-bit)
3. Optimizovati za vaš hardware
4. Učiniti ga dostupnim za korišćenje

**Vreme**: 5-15 minuta (zavisno od internet brzine)

---

## Korak 2: Testirajte Model

```bash
# Testirajte da li radi
ollama run mistral "Šta je poreski obveznik?"
```

Trebalo bi da vidite odgovor od modela.

---

## Korak 3: Model se Automatski Pojavljuje u Dropdown Listi

Vaš sistem već ima implementiran **model discovery** koji automatski detektuje sve Ollama modele!

Kada otvorite **EvaluationConfigPage** i dođete do **LLM Configuration** sekcije, u dropdown listi za "LLM Model" će se automatski pojaviti:

- `mistral` ✅ (novi model koji ste upravo preuzeli)
- `llama3.2` (ako ga imate)
- `qwen2.5` (ako ga imate)
- ... svi drugi Ollama modeli

**Ništa ne morate ručno da konfigurišete!**

---

## Dodatni Mistral Modeli (Opciono)

Ollama ima nekoliko verzija Mistral modela:

### 1. Mistral (7B) - PREPORUČENO
```bash
ollama pull mistral
```
- Veličina: ~4.1 GB
- VRAM: ~6-8 GB
- Brzina: Brz
- Kvalitet: Odličan

### 2. Mistral-Small (22B) - Ako imate više VRAM-a
```bash
ollama pull mistral-small
```
- Veličina: ~13 GB
- VRAM: ~16-20 GB
- Brzina: Sporiji
- Kvalitet: Bolji od 7B

### 3. Mistral-Large (123B) - Za production (cloud GPU)
```bash
ollama pull mistral-large
```
- Veličina: ~70 GB
- VRAM: ~80+ GB
- Brzina: Spor
- Kvalitet: Najbolji

**Za vaš use case (lokalni hardware)**: Koristite **`mistral`** (7B verziju)

---

## Kako Vaš Sistem Detektuje Modele

Vaš backend ima endpoint `/api/models/llms` koji automatski:

1. Poziva `ollama list` komandu
2. Parsira listu dostupnih modela
3. Vraća ih frontend-u
4. Frontend ih prikazuje u dropdown listi

**Kod** (već implementiran u `backend/routers/models.py`):

```python
@router.get("/llms")
async def get_llm_models():
    """Vraća listu dostupnih LLM modela iz Ollama"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        models = []
        for line in result.stdout.strip().split('\n')[1:]:
            parts = line.split()
            if parts:
                model_name = parts[0].split(':')[0]
                models.append({
                    "name": model_name,
                    "full_name": parts[0],
                    "size": parts[1] if len(parts) > 1 else "unknown"
                })
        
        return {"models": models}
    except Exception as e:
        return {"models": [], "error": str(e)}
```

---

## Provera Instaliranih Modela

```bash
# Vidite sve instalirane Ollama modele
ollama list
```

Trebalo bi da vidite:

```
NAME                    ID              SIZE    MODIFIED
mistral:latest          abc123def       4.1 GB  2 minutes ago
llama3.2:latest         xyz789ghi       2.0 GB  1 day ago
```

---

## Korišćenje u Evaluaciji

1. Idite na **Konfiguracije** (Evaluations page)
2. Kliknite **"+ Nova Konfiguracija"**
3. Popunite osnovne informacije
4. U **LLM Configuration** sekciji:
   - Dropdown "LLM Model" će automatski pokazati `mistral`
   - Izaberite `mistral`
5. Kliknite **"Save & Run"**

**To je sve!** Model će se automatski koristiti za generisanje odgovora.

---

## Poređenje: Ollama vs HuggingFace Transformers

| Aspekt | Ollama | HuggingFace Transformers |
|--------|--------|--------------------------|
| **Setup** | `ollama pull mistral` | 145 linija Python koda |
| **Veličina** | 4.1 GB | 14 GB |
| **Memorija** | 6-8 GB VRAM | 8-12 GB VRAM |
| **Brzina** | Brže (optimizovano) | Sporije |
| **Integracija** | Automatska | Ručna |
| **Quantization** | Automatski | Ručno konfigurisanje |

**Zaključak**: Za vaš use case, **Ollama je mnogo bolji izbor!**

---

## Troubleshooting

### Problem: "ollama: command not found"

**Rešenje**: Instalirajte Ollama
```bash
# Windows: Preuzmite sa https://ollama.com/download
# Linux:
curl -fsSL https://ollama.com/install.sh | sh
```

### Problem: Model se ne pojavljuje u dropdown listi

**Rešenje**: 
1. Proverite da li je Ollama pokrenut: `ollama list`
2. Restartujte backend: `Ctrl+C` pa ponovo `python -m uvicorn backend.main:app --reload`
3. Refresh frontend stranicu (F5)

### Problem: "Error: model not found"

**Rešenje**: Preuzmite model ponovo
```bash
ollama pull mistral
```

---

## Dodatni Preporučeni Modeli za Pravnu Tematiku

Pored Mistral-a, možete testirati i ove modele:

### 1. Llama 3.2 (3B) - Brži, manji
```bash
ollama pull llama3.2
```
- Veličina: ~2 GB
- VRAM: ~4 GB
- Brzina: Vrlo brz
- Kvalitet: Dobar (ali lošiji od Mistral-a)

### 2. Qwen2.5 (7B) - Odličan za non-English
```bash
ollama pull qwen2.5:7b
```
- Veličina: ~4.7 GB
- VRAM: ~6-8 GB
- Brzina: Sličan Mistral-u
- Kvalitet: Odličan za srpski jezik

### 3. Gemma2 (9B) - Google model
```bash
ollama pull gemma2:9b
```
- Veličina: ~5.4 GB
- VRAM: ~8-10 GB
- Brzina: Malo sporiji
- Kvalitet: Vrlo dobar

**Preporuka**: Preuzmite sve 4 modela i testirajte ih na vašem test setu od 150 pitanja da vidite koji daje najbolje rezultate!

```bash
ollama pull mistral
ollama pull llama3.2
ollama pull qwen2.5:7b
ollama pull gemma2:9b
```

Svi će se automatski pojaviti u dropdown listi i možete ih uporediti koristeći **Compare** funkcionalnost!

---

## Benchmark Test - Kako Uporediti Modele

1. Kreirajte 4 evaluacije sa istim test primerima, ali različitim LLM modelima:
   - Evaluacija 1: `mistral`
   - Evaluacija 2: `llama3.2`
   - Evaluacija 3: `qwen2.5:7b`
   - Evaluacija 4: `gemma2:9b`

2. Pokrenite sve 4 evaluacije

3. Idite na **Konfiguracije** page

4. Selektujte sve 4 evaluacije (checkbox)

5. Kliknite **"Compare Selected"**

6. Videćete side-by-side poređenje:
   - Tačnost (BLEU, ROUGE, BERTScore)
   - Brzina (avg time per question)
   - Performance breakdown

7. Izaberite najbolji model za vaš use case!

---

## Zaključak

**Najbrži način da počnete:**

```bash
# 1. Preuzmite Mistral
ollama pull mistral

# 2. Testirajte
ollama run mistral "Šta je poreski obveznik?"

# 3. Otvorite frontend i kreirajte novu konfiguraciju
# 4. Izaberite 'mistral' iz dropdown liste
# 5. Save & Run!
```

**To je sve!** 🚀

Nema potrebe za komplikovanim Python scriptovima, ručnim quantization-om, ili konfiguracijom. Ollama sve radi automatski.

---

**Napomena**: Fajlovi `MISTRAL_7B_SETUP_GUIDE.md` i `setup_mistral.py` su za napredne korisnike koji žele direktnu HuggingFace integraciju. Za vaš use case, **koristite Ollama** - mnogo je jednostavnije!