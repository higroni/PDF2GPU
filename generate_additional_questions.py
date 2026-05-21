"""
Skripta za generisanje dodatnih 100 pitanja iz PDF-a o godišnjem porezu na dohodak građana
"""
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import SessionLocal
from backend.rag.pdf_processor import PDFProcessor
from backend.rag.embedding_service import EmbeddingService
from backend.rag.qdrant_service import QdrantService
from backend.rag.rag_engine import RAGEngine
from backend.config import settings

def load_existing_questions():
    """Učitaj postojeća pitanja"""
    with open('test_examples_50.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['test_examples']

def generate_questions_from_pdf():
    """Generiši dodatna pitanja iz PDF-a"""
    
    # Inicijalizuj servise
    pdf_processor = PDFProcessor()
    embedding_service = EmbeddingService()
    qdrant_service = QdrantService()
    
    # Učitaj PDF
    pdf_path = "uploads/1779349915.470375_Годишњи_порез_на_доходак_грађана.pdf"
    
    print(f"Učitavam PDF: {pdf_path}")
    chunks = pdf_processor.process_pdf(pdf_path)
    print(f"Ekstrahovano {len(chunks)} chunk-ova")
    
    # Dodatna pitanja bazirana na različitim aspektima zakona
    additional_questions = []
    
    # Kategorije pitanja sa varijacijama
    question_templates = [
        # Osnovni pojmovi i definicije
        ("Šta predstavlja godišnji porez na dohodak građana?", "porez na dohodak definicija"),
        ("Kako se definiše dohodak u smislu ovog zakona?", "definicija dohotka"),
        ("Ko je obveznik godišnjeg poreza na dohodak?", "obveznik poreza"),
        ("Šta znači termin 'rezident' u poreskom smislu?", "rezident definicija"),
        ("Šta znači termin 'nerezident' u poreskom smislu?", "nerezident definicija"),
        
        # Poreska osnovica i stope
        ("Kako se utvrđuje poreska osnovica za godišnji porez?", "poreska osnovica utvrđivanje"),
        ("Koje su poreske stope za godišnji porez na dohodak?", "poreske stope"),
        ("Da li postoji progresivno oporezivanje dohotka?", "progresivno oporezivanje"),
        ("Kako se obračunava porez na različite nivoe dohotka?", "obračun poreza nivoi"),
        
        # Vrste prihoda
        ("Koji prihodi se smatraju zaradom?", "zarada definicija"),
        ("Šta spada u prihode od samostalne delatnosti?", "samostalna delatnost prihodi"),
        ("Koji prihodi se ostvaruju od autorskih prava?", "autorska prava prihodi"),
        ("Šta su prihodi od nepokretnosti?", "prihodi nepokretnosti"),
        ("Koji prihodi se ostvaruju od zakupa pokretnih stvari?", "zakup pokretnih stvari"),
        ("Šta su prihodi sportista?", "prihodi sportista"),
        ("Koji su drugi prihodi koji podležu oporezivanju?", "drugi prihodi oporezivanje"),
        
        # Umanjenja i oslobođenja
        ("Koji rashodi umanjuju poresku osnovicu?", "rashodi umanjenje osnovice"),
        ("Da li postoje oslobođenja od plaćanja poreza?", "oslobođenja poreza"),
        ("Koji prihodi su oslobođeni poreza?", "oslobođeni prihodi"),
        ("Kako se primenjuje neoporezivi iznos?", "neoporezivi iznos primena"),
        ("Šta je poreski kredit i kako se koristi?", "poreski kredit"),
        
        # Doprinosi
        ("Koji doprinosi se plaćaju uz porez na dohodak?", "doprinosi vrste"),
        ("Kolika je stopa doprinosa za penzijsko osiguranje?", "doprinos penzijsko"),
        ("Kolika je stopa doprinosa za zdravstveno osiguranje?", "doprinos zdravstveno"),
        ("Kolika je stopa doprinosa za osiguranje od nezaposlenosti?", "doprinos nezaposlenost"),
        ("Šta je najviša godišnja osnovica doprinosa?", "najviša osnovica doprinosa"),
        
        # Poreska prijava i plaćanje
        ("Ko je dužan da podnese poresku prijavu?", "poreska prijava obaveza"),
        ("Kada se podnosi poreska prijava za godišnji porez?", "rok poreska prijava"),
        ("Koji dokumenti se prilažu uz poresku prijavu?", "dokumenti poreska prijava"),
        ("Kako se plaća godišnji porez na dohodak?", "plaćanje poreza način"),
        ("Koji su rokovi za plaćanje poreza?", "rokovi plaćanje"),
        
        # Posebne kategorije obveznika
        ("Kako se oporezuju prihodi poljoprivrednika?", "poljoprivrednici oporezivanje"),
        ("Kako se oporezuju prihodi preduzetnika?", "preduzetnici oporezivanje"),
        ("Kako se oporezuju prihodi iz inostranstva?", "inostrani prihodi"),
        ("Kako se oporezuju prihodi od kapitala?", "prihodi kapital"),
        
        # Poreske olakšice
        ("Koje poreske olakšice postoje za mlade?", "olakšice mladi"),
        ("Da li postoje olakšice za ulaganja?", "olakšice ulaganja"),
        ("Koje olakšice postoje za izdržavane članove porodice?", "olakšice porodica"),
        ("Kako se primenjuju olakšice za dobrovoljno penzijsko osiguranje?", "olakšice penzijsko"),
        
        # Kontrola i kazne
        ("Ko vrši kontrolu plaćanja godišnjeg poreza?", "kontrola poreza"),
        ("Koje kazne postoje za neplaćanje poreza?", "kazne neplaćanje"),
        ("Šta se dešava u slučaju nepodношenja prijave?", "kazne nepodnošenje prijave"),
        ("Kako se obračunavaju kamate na neplaćeni porez?", "kamate neplaćeni porez"),
        
        # Specifična pitanja o iznosima za 2025
        ("Koliki je trostruki iznos prosečne godišnje zarade za 2025?", "trostruki iznos 2025"),
        ("Koliki je prag za obavezu plaćanja godišnjeg poreza u 2025?", "prag obveze 2025"),
        ("Koliko iznosi umanjenje za mlade u 2025. godini?", "umanjenje mladi 2025"),
        
        # Proceduralna pitanja
        ("Gde se podnosi poreska prijava?", "mesto podnošenja prijave"),
        ("Kako se ispravlja greška u poreskoj prijavi?", "ispravka prijave"),
        ("Šta je poresko rešenje?", "poresko rešenje"),
        ("Kako se podnosi žalba na poresko rešenje?", "žalba rešenje"),
        
        # Međunarodni aspekti
        ("Kako se izbegava dvostruko oporezivanje?", "dvostruko oporezivanje"),
        ("Šta su međunarodni ugovori o izbegavanju dvostrukog oporezivanja?", "međunarodni ugovori"),
        ("Kako se oporezuju strani državljani u Srbiji?", "strani državljani oporezivanje"),
        
        # Specifični slučajevi
        ("Kako se oporezuju prihodi od prodaje nepokretnosti?", "prodaja nepokretnosti porez"),
        ("Kako se oporezuju prihodi od dividendi?", "dividende oporezivanje"),
        ("Kako se oporezuju prihodi od kamata?", "kamate oporezivanje"),
        ("Kako se oporezuju prihodi od autorskih honorara?", "autorski honorari"),
        
        # Računovodstveni aspekti
        ("Koja evidencija se vodi za potrebe godišnjeg poreza?", "evidencija poreza"),
        ("Kako se vodi knjiga prihoda i rashoda?", "knjiga prihoda rashoda"),
        ("Koji dokumenti služe kao dokaz o prihodima?", "dokazi prihodi"),
        
        # Prelazne i završne odredbe
        ("Kada je stupio na snagu zakon o godišnjem porezu?", "stupanje snagu zakon"),
        ("Kako se primenjuju prelazne odredbe?", "prelazne odredbe"),
        ("Šta se dešava sa starim propisima?", "stari propisi"),
        
        # Dodatna varijanta pitanja
        ("U kom slučaju fizičko lice postaje obveznik poreza?", "obveznik uslovi"),
        ("Koje su posledice nepodnošenja poreske prijave?", "posledice nepodnošenje"),
        ("Kako se utvrđuje prebivalište u poreskom smislu?", "prebivalište utvrđivanje"),
        ("Šta je centar poslovnih i životnih interesa?", "centar interesa"),
        ("Kako se računa period boravka od 183 dana?", "183 dana računanje"),
        ("Koji prihodi se ne uključuju u godišnji porez?", "prihodi isključeni"),
        ("Kako se tretiraju prihodi ostvareni u inostranstvu?", "inostrani prihodi tretman"),
        ("Šta je paušalno oporezivanje?", "paušalno oporezivanje"),
        ("Kako se oporezuju prihodi od zakupa stana?", "zakup stan oporezivanje"),
        ("Koje su obaveze poslodavca u vezi sa godišnjim porezom?", "poslodavac obaveze"),
        ("Kako se prijavljuju prihodi od više izvora?", "više izvora prijava"),
        ("Šta je potvrda o prihodima?", "potvrda prihodi"),
        ("Kako se dokazuje plaćeni porez?", "dokaz plaćeni porez"),
        ("Šta je poreska kartica?", "poreska kartica"),
        ("Kako se vrši povraćaj preplaćenog poreza?", "povraćaj poreza"),
        ("U kom roku se vrši povraćaj poreza?", "rok povraćaj"),
        ("Kako se obračunava porez na prihode od prodaje akcija?", "akcije porez"),
        ("Šta su kapitalni dobici?", "kapitalni dobici"),
        ("Kako se oporezuju prihodi od prodaje udela u društvu?", "udeli prodaja porez"),
        ("Koje su obaveze notara u vezi sa porezom?", "notar obaveze"),
        ("Kako se prijavljuju prihodi od nasledstva?", "nasledstvo prijava"),
        ("Da li se oporezuju prihodi od poklona?", "pokloni oporezivanje"),
        ("Kako se tretiraju prihodi od osiguranja?", "osiguranje prihodi"),
        ("Šta su prihodi od igara na sreću?", "igre sreća prihodi"),
        ("Kako se oporezuju prihodi sportskih kladionica?", "kladionice oporezivanje"),
        ("Koje su obaveze banaka u vezi sa porezom?", "banke obaveze"),
        ("Kako se prijavljuju prihodi od freelance rada?", "freelance prijava"),
        ("Šta su prihodi od intelektualne svojine?", "intelektualna svojina"),
        ("Kako se oporezuju prihodi od licenci?", "licence oporezivanje"),
        ("Šta su prihodi od franšize?", "franšiza prihodi"),
        ("Kako se tretiraju prihodi od konsultantskih usluga?", "konsultantske usluge"),
        ("Koje su obaveze poreskog savetnika?", "poreski savetnik obaveze"),
        ("Kako se vrši poreska revizija?", "poreska revizija"),
        ("Šta je poreska kontrola?", "poreska kontrola"),
        ("Koje su nadležnosti poreske uprave?", "poreska uprava nadležnosti"),
        ("Kako se podnosi zahtev za odlaganje plaćanja poreza?", "odlaganje plaćanja"),
        ("U kojim slučajevima se odobrava odlaganje?", "odlaganje uslovi"),
        ("Šta je poresko oslobođenje?", "poresko oslobođenje"),
        ("Kako se dobija poresko oslobođenje?", "oslobođenje dobijanje"),
        ("Koje su obaveze izvršitelja testamenta?", "izvršilac testamenta"),
        ("Kako se prijavljuju prihodi od autorskih prava nasleđenih?", "nasleđena autorska prava"),
    ]
    
    print(f"\nGenerišem dodatna pitanja iz PDF-a...")
    
    # Inicijalizuj RAG engine
    rag_engine = RAGEngine(
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
        llm_model=settings.LLM_MODEL
    )
    
    # Generiši pitanja
    for i, (question, search_query) in enumerate(question_templates[:100], 1):
        print(f"Generišem pitanje {i}/100: {question[:50]}...")
        
        try:
            # Pretraži relevantne chunk-ove
            results = qdrant_service.search(
                collection_name="bane-proba1",  # Pretpostavljam da je PDF već uploadovan
                query_text=search_query,
                limit=3
            )
            
            if results:
                # Generiši odgovor koristeći RAG
                answer = rag_engine.generate_answer(
                    question=question,
                    context_chunks=results,
                    system_prompt="Ti si ekspert za poreze u Srbiji. Odgovori precizno i kratko na osnovu dostavljenog konteksta. Koristi samo informacije iz konteksta."
                )
                
                additional_questions.append({
                    "question": question,
                    "expected_answer": answer.strip()
                })
            else:
                print(f"  Nema rezultata za: {search_query}")
                
        except Exception as e:
            print(f"  Greška: {e}")
            continue
    
    return additional_questions

def main():
    """Glavna funkcija"""
    print("=== Generisanje dodatnih 100 pitanja ===\n")
    
    # Učitaj postojeća pitanja
    existing_questions = load_existing_questions()
    print(f"Učitano {len(existing_questions)} postojećih pitanja")
    
    # Generiši nova pitanja
    new_questions = generate_questions_from_pdf()
    print(f"\nGenerisano {len(new_questions)} novih pitanja")
    
    # Kombinuj pitanja
    all_questions = existing_questions + new_questions
    print(f"\nUkupno pitanja: {len(all_questions)}")
    
    # Sačuvaj u JSON
    output = {
        "test_examples": all_questions
    }
    
    output_file = "test_examples_150.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Sačuvano u: {output_file}")
    print(f"✓ Ukupno pitanja: {len(all_questions)}")

if __name__ == "__main__":
    main()

# Made with Bob
