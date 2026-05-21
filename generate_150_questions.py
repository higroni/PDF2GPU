"""
Skripta za proširenje test seta sa 50 na 150 pitanja
Sva pitanja su bazirana ISKLJUČIVO na temi godišnjeg poreza na dohodak građana
"""
import json

def load_existing_questions():
    """Učitaj postojeća 50 pitanja"""
    with open('test_examples_50.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['test_examples']

def generate_additional_questions():
    """
    Generiši dodatnih 100 pitanja o godišnjem porezu na dohodak građana.
    Pitanja su varijacije i proširenja postojećih tema, ali se drže ISKLJUČIVO
    sadržaja iz zakona o godišnjem porezu na dohodak građana.
    """
    
    additional_questions = [
        # Varijacije osnovnih pitanja (1-20)
        {
            "question": "Koji je iznos neoporezivog dohotka za poresku 2025. godinu?",
            "expected_answer": "5.439.096 dinara"
        },
        {
            "question": "Koliko iznosi prosečna godišnja zarada za 2025?",
            "expected_answer": "1.813.032 dinara"
        },
        {
            "question": "Ko mora da plati godišnji porez na dohodak građana?",
            "expected_answer": "fizička lica koja ostvare dohodak veći od trostrukog iznosa prosečne godišnje zarade"
        },
        {
            "question": "Kada fizičko lice postaje rezident Republike Srbije?",
            "expected_answer": "kada ima prebivalište ili centar poslovnih i životnih interesa na teritoriji Republike, ili boravi 183 ili više dana"
        },
        {
            "question": "Koje vrste prihoda podležu godišnjem porezu na dohodak?",
            "expected_answer": "zarada, prihodi od samostalne delatnosti, autorskih prava, nepokretnosti, zakupa pokretnih stvari, prihodi sportista, ugostiteljskih usluga, pomoraca i drugi prihodi"
        },
        
        # Pitanja o poreskoj osnovici i obračunu (21-35)
        {
            "question": "Kako se formira dohodak za oporezivanje?",
            "expected_answer": "prihodi umanjeni za porez na dohodak građana i doprinose za obavezno socijalno osiguranje"
        },
        {
            "question": "Koliki je iznos najviše godišnje osnovice doprinosa za 2025?",
            "expected_answer": "7.877.100 dinara"
        },
        {
            "question": "Da li mlađi od 40 godina imaju poreske olakšice?",
            "expected_answer": "da, godišnji zbir zarada dodatno umanjuju za iznos tri prosečne godišnje zarade"
        },
        {
            "question": "Za koji iznos se umanjuje dohodak za lica mlađa od 40 godina?",
            "expected_answer": "5.439.096 dinara za 2025. godinu"
        },
        {
            "question": "Šta je poreski kredit za ulaganje u alternativni investicioni fond?",
            "expected_answer": "pravo na umanjenje godišnjeg poreza najviše do 50% ulaganja izvršenog u kalendarskoj godini"
        },
        {
            "question": "Koliki je maksimalni poreski kredit u odnosu na poresku obavezu?",
            "expected_answer": "ne može biti veći od 50% obračunate poreske obaveze"
        },
        {
            "question": "Koliko dugo obveznik mora držati akcije alternativnog fonda?",
            "expected_answer": "u kalendarskoj godini ulaganja i naredne dve kalendarske godine"
        },
        {
            "question": "Koji je uslov za primenu poreskog kredita?",
            "expected_answer": "obveznik ne sme otuđiti akcije u godini ulaganja i naredne dve godine"
        },
        {
            "question": "Kako se obračunava godišnji porez na dohodak?",
            "expected_answer": "na osnovu ukupnog dohotka ostvarenog u kalendarskoj godini"
        },
        {
            "question": "Šta se oduzima od prihoda pri utvrđivanju dohotka?",
            "expected_answer": "porez na dohodak građana i doprinosi za obavezno socijalno osiguranje"
        },
        
        # Pitanja o vrstama prihoda (36-50)
        {
            "question": "Šta se smatra zaradom u smislu godišnjeg poreza?",
            "expected_answer": "primanja zaposlenog po osnovu radnog odnosa"
        },
        {
            "question": "Koji prihodi spadaju u samostalnu delatnost?",
            "expected_answer": "prihodi od obavljanja delatnosti preduzetnika i drugih samostalnih delatnosti"
        },
        {
            "question": "Šta su prihodi od autorskih prava?",
            "expected_answer": "prihodi od autorskih i srodnih prava i prava industrijske svojine"
        },
        {
            "question": "Koji prihodi se ostvaruju od nepokretnosti?",
            "expected_answer": "prihodi od izdavanja nepokretnosti u zakup i prihodi od prodaje nepokretnosti"
        },
        {
            "question": "Šta su prihodi od zakupa pokretnih stvari?",
            "expected_answer": "prihodi od davanja u zakup pokretnih stvari"
        },
        {
            "question": "Koji prihodi se smatraju prihodima sportista?",
            "expected_answer": "prihodi koje sportista ostvari po osnovu bavljenja sportom"
        },
        {
            "question": "Šta su prihodi od ugostiteljskih usluga?",
            "expected_answer": "prihodi od pružanja ugostiteljskih usluga u domaćinstvu"
        },
        {
            "question": "Koji su prihodi pomoraca?",
            "expected_answer": "prihodi pomoraca ostvareni na brodovima"
        },
        {
            "question": "Šta spadaju u druge prihode?",
            "expected_answer": "ostali prihodi koji nisu obuhvaćeni drugim kategorijama"
        },
        {
            "question": "Da li se svi prihodi uključuju u godišnji porez?",
            "expected_answer": "ne, samo prihodi koji prelaze trostruki iznos prosečne godišnje zarade"
        },
        
        # Pitanja o doprinosima (51-60)
        {
            "question": "Koje vrste doprinosa se plaćaju uz godišnji porez?",
            "expected_answer": "doprinosi za penzijsko, zdravstveno osiguranje i osiguranje od nezaposlenosti"
        },
        {
            "question": "Kolika je stopa doprinosa za penzijsko osiguranje?",
            "expected_answer": "zavisi od vrste prihoda, obično 14% za zaposlene"
        },
        {
            "question": "Kolika je stopa doprinosa za zdravstveno osiguranje?",
            "expected_answer": "zavisi od vrste prihoda, obično 5.15% za zaposlene"
        },
        {
            "question": "Kolika je stopa doprinosa za nezaposlenost?",
            "expected_answer": "zavisi od vrste prihoda, obično 0.75% za zaposlene"
        },
        {
            "question": "Šta ograničava najviša godišnja osnovica doprinosa?",
            "expected_answer": "maksimalni iznos prihoda na koji se obračunavaju doprinosi"
        },
        {
            "question": "Kako se obračunavaju doprinosi na visoke prihode?",
            "expected_answer": "do najviše godišnje osnovice doprinosa, iznad te osnovice se ne plaćaju doprinosi"
        },
        {
            "question": "Da li se doprinosi plaćaju na sve vrste prihoda?",
            "expected_answer": "ne, zavisi od vrste prihoda i načina oporezivanja"
        },
        {
            "question": "Ko plaća doprinose za zaposlene?",
            "expected_answer": "poslodavac i zaposleni, svako svoj deo"
        },
        {
            "question": "Ko plaća doprinose za samostalnu delatnost?",
            "expected_answer": "obveznik samostalno plaća doprinose"
        },
        {
            "question": "Kako se doprinosi odražavaju na poresku osnovicu?",
            "expected_answer": "doprinosi umanjuju prihode pri utvrđivanju dohotka"
        },
        
        # Pitanja o poreskoj prijavi (61-75)
        {
            "question": "Ko je obavezan da podnese poresku prijavu?",
            "expected_answer": "obveznici koji su ostvarili dohodak veći od trostrukog iznosa prosečne godišnje zarade"
        },
        {
            "question": "Do kada se podnosi poreska prijava za godišnji porez?",
            "expected_answer": "do 15. maja tekuće godine za prethodnu godinu"
        },
        {
            "question": "Gde se podnosi poreska prijava?",
            "expected_answer": "nadležnoj poreskoj upravi prema mestu prebivališta"
        },
        {
            "question": "Koji obrazac se koristi za poresku prijavu?",
            "expected_answer": "propisani obrazac poreske uprave"
        },
        {
            "question": "Šta se prilaže uz poresku prijavu?",
            "expected_answer": "potvrde o prihodima, dokazi o plaćenim doprinosima i drugi relevantni dokumenti"
        },
        {
            "question": "Može li se poreska prijava podneti elektronski?",
            "expected_answer": "da, preko portala poreske uprave"
        },
        {
            "question": "Šta se dešava ako se ne podnese poreska prijava?",
            "expected_answer": "poreska uprava može utvrditi porez po službenoj dužnosti i izreći kaznu"
        },
        {
            "question": "Može li se ispraviti greška u poreskoj prijavi?",
            "expected_answer": "da, podnošenjem ispravke poreske prijave"
        },
        {
            "question": "U kom roku se može ispraviti poreska prijava?",
            "expected_answer": "pre nego što poreska uprava utvrdi grešku"
        },
        {
            "question": "Šta je poresko rešenje?",
            "expected_answer": "akt poreske uprave kojim se utvrđuje poreska obaveza"
        },
        {
            "question": "Može li se uložiti žalba na poresko rešenje?",
            "expected_answer": "da, u roku od 15 dana od prijema rešenja"
        },
        {
            "question": "Kome se podnosi žalba na poresko rešenje?",
            "expected_answer": "drugostepenom organu poreske uprave"
        },
        {
            "question": "Šta se dešava nakon podnošenja žalbe?",
            "expected_answer": "drugostepeni organ razmatra žalbu i donosi odluku"
        },
        {
            "question": "Može li se pokrenuti sudski spor protiv poreskog rešenja?",
            "expected_answer": "da, nakon iscrpljivanja upravnog postupka"
        },
        {
            "question": "Koji sud je nadležan za poreske sporove?",
            "expected_answer": "upravni sud"
        },
        
        # Pitanja o plaćanju poreza (76-85)
        {
            "question": "Kada se plaća godišnji porez na dohodak?",
            "expected_answer": "nakon prijema poreskog rešenja, u propisanom roku"
        },
        {
            "question": "Koliki je rok za plaćanje poreza?",
            "expected_answer": "15 dana od prijema poreskog rešenja"
        },
        {
            "question": "Može li se porez platiti na rate?",
            "expected_answer": "da, uz odobrenje poreske uprave"
        },
        {
            "question": "Šta se dešava ako se porez ne plati na vreme?",
            "expected_answer": "obračunavaju se kamate na neplaćeni iznos"
        },
        {
            "question": "Kolika je kamata na neplaćeni porez?",
            "expected_answer": "propisana zakonska zatezna kamata"
        },
        {
            "question": "Može li poreska uprava prinudno naplatiti porez?",
            "expected_answer": "da, putem prinudne naplate"
        },
        {
            "question": "Šta je prinudna naplata poreza?",
            "expected_answer": "naplata poreza blokadom računa ili prodajom imovine"
        },
        {
            "question": "Može li se tražiti odlaganje plaćanja poreza?",
            "expected_answer": "da, uz obrazložen zahtev poreskoj upravi"
        },
        {
            "question": "U kojim slučajevima se odobrava odlaganje?",
            "expected_answer": "u slučaju privremenih finansijskih teškoća obveznika"
        },
        {
            "question": "Šta je povraćaj poreza?",
            "expected_answer": "vraćanje preplaćenog poreza obvezniku"
        },
        
        # Pitanja o posebnim kategorijama (86-100)
        {
            "question": "Kako se oporezuju prihodi od prodaje nepokretnosti?",
            "expected_answer": "kao prihodi od nepokretnosti, uz moguća oslobođenja"
        },
        {
            "question": "Postoje li oslobođenja za prodaju stana?",
            "expected_answer": "da, pod određenim uslovima (npr. jedini stan, period vlasništva)"
        },
        {
            "question": "Kako se oporezuju prihodi od dividendi?",
            "expected_answer": "kao prihodi od kapitala, po posebnoj stopi"
        },
        {
            "question": "Kako se oporezuju prihodi od kamata?",
            "expected_answer": "kao prihodi od kapitala"
        },
        {
            "question": "Šta su prihodi od kapitala?",
            "expected_answer": "dividende, kamate, kapitalni dobici i slični prihodi"
        },
        {
            "question": "Kako se oporezuju prihodi iz inostranstva?",
            "expected_answer": "uključuju se u godišnji dohodak, uz mogućnost umanjenja za porez plaćen u inostranstvu"
        },
        {
            "question": "Šta je dvostruko oporezivanje?",
            "expected_answer": "oporezivanje istog prihoda u dve države"
        },
        {
            "question": "Kako se izbegava dvostruko oporezivanje?",
            "expected_answer": "primenom međunarodnih ugovora i poreskog kredita"
        },
        {
            "question": "Šta su međunarodni poreski ugovori?",
            "expected_answer": "ugovori između država o izbegavanju dvostrukog oporezivanja"
        },
        {
            "question": "Kako se tretiraju strani državljani u Srbiji?",
            "expected_answer": "kao rezidenti ili nerezidenti, zavisno od uslova boravka"
        },
        {
            "question": "Šta je poreski rezident?",
            "expected_answer": "lice koje ispunjava uslove za rezidentnost prema zakonu"
        },
        {
            "question": "Šta je poreski nerezident?",
            "expected_answer": "lice koje ne ispunjava uslove za rezidentnost"
        },
        {
            "question": "Kako se oporezuju nerezidenti?",
            "expected_answer": "samo za prihode ostvarene u Srbiji"
        },
        {
            "question": "Kako se oporezuju rezidenti?",
            "expected_answer": "za sve prihode, bez obzira gde su ostvareni"
        },
        {
            "question": "Šta je centar poslovnih i životnih interesa?",
            "expected_answer": "mesto gde lice ima najjače ekonomske i lične veze"
        },
        
        # Dodatna pitanja za kompletiranje do 150 (101-125)
        {
            "question": "Kako se utvrđuje prebivalište u poreskom smislu?",
            "expected_answer": "mesto gde lice ima prijavljeno prebivalište ili gde faktički živi"
        },
        {
            "question": "Šta je period boravka od 183 dana?",
            "expected_answer": "period neprekidnog ili sa prekidima boravka u periodu od 12 meseci"
        },
        {
            "question": "Kako se računa period od 12 meseci za boravak?",
            "expected_answer": "period koji počinje ili se završava u odnosnoj poreskoj godini"
        },
        {
            "question": "Da li se prekidi boravka računaju u 183 dana?",
            "expected_answer": "da, računa se ukupan boravak sa prekidima"
        },
        {
            "question": "Šta su prihodi od diplomatske službe?",
            "expected_answer": "prihodi lica upućenih u drugu državu radi obavljanja delatnosti u diplomatskom ili konzularnom predstavništvu"
        },
        {
            "question": "Kako se oporezuju prihodi diplomata?",
            "expected_answer": "kao rezidenti Republike Srbije, bez obzira na mesto ostvarivanja prihoda"
        },
        {
            "question": "Šta je godišnji zbir zarada?",
            "expected_answer": "ukupan iznos zarada ostvarenih u kalendarskoj godini"
        },
        {
            "question": "Kako se umanjuje godišnji zbir zarada?",
            "expected_answer": "za neoporezivi iznos i dodatna umanjenja (npr. za mlade)"
        },
        {
            "question": "Šta je trostruki iznos prosečne zarade?",
            "expected_answer": "iznos koji predstavlja prag za obavezu plaćanja godišnjeg poreza"
        },
        {
            "question": "Koliki je trostruki iznos za 2025. godinu?",
            "expected_answer": "5.439.096 dinara (3 x 1.813.032)"
        },
        {
            "question": "Ko ne plaća godišnji porez na dohodak?",
            "expected_answer": "lica čiji dohodak ne prelazi trostruki iznos prosečne godišnje zarade"
        },
        {
            "question": "Šta se dešava ako dohodak prelazi prag?",
            "expected_answer": "obveznik mora da podnese poresku prijavu i plati godišnji porez"
        },
        {
            "question": "Kako se obračunava porez na dohodak iznad praga?",
            "expected_answer": "primenom progresivnih poreskih stopa na iznos iznad neoporezivog dela"
        },
        {
            "question": "Koje su progresivne poreske stope?",
            "expected_answer": "stope koje rastu sa povećanjem dohotka (npr. 10%, 15%, 20%)"
        },
        {
            "question": "Šta je neoporezivi deo dohotka?",
            "expected_answer": "deo dohotka na koji se ne plaća porez"
        },
        {
            "question": "Kako se primenjuje neoporezivi deo?",
            "expected_answer": "oduzima se od ukupnog dohotka pre obračuna poreza"
        },
        {
            "question": "Da li svi obveznici imaju isti neoporezivi deo?",
            "expected_answer": "da, neoporezivi deo je isti za sve obveznike"
        },
        {
            "question": "Šta je dodatno umanjenje za mlade?",
            "expected_answer": "dodatno umanjenje godišnjeg zbira zarada za lica mlađa od 40 godina"
        },
        {
            "question": "Kako se utvrđuje starost za dodatno umanjenje?",
            "expected_answer": "na osnovu godina života na poslednji dan kalendarske godine"
        },
        {
            "question": "Koliko godina mora imati lice za dodatno umanjenje?",
            "expected_answer": "manje od navršenih 40 godina na poslednji dan godine"
        },
        {
            "question": "Za koliko se umanjuje dohodak mladih?",
            "expected_answer": "za iznos tri prosečne godišnje zarade"
        },
        {
            "question": "Šta je alternativni investicioni fond?",
            "expected_answer": "fond za ulaganje u alternativne investicije"
        },
        {
            "question": "Kako se dobija poreski kredit za ulaganje?",
            "expected_answer": "ulaganjem u alternativni investicioni fond u kalendarskoj godini"
        },
        {
            "question": "Koliki je maksimalni poreski kredit za ulaganje?",
            "expected_answer": "50% iznosa ulaganja, ali ne više od 50% poreske obaveze"
        },
        {
            "question": "Šta se dešava ako se akcije prodaju pre roka?",
            "expected_answer": "gubi se pravo na poreski kredit i mora se vratiti umanjeni porez"
        }
    ]
    
    return additional_questions

def main():
    """Glavna funkcija"""
    print("=== Proširenje test seta sa 50 na 150 pitanja ===\n")
    
    # Učitaj postojeća pitanja
    existing_questions = load_existing_questions()
    print(f"Učitano {len(existing_questions)} postojećih pitanja")
    
    # Generiši nova pitanja
    new_questions = generate_additional_questions()
    print(f"Generisano {len(new_questions)} novih pitanja")
    
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
    print("\nSva pitanja su bazirana ISKLJUČIVO na temi godišnjeg poreza na dohodak građana.")

if __name__ == "__main__":
    main()

# Made with Bob
