"""
Utility za konverziju srpske ćirilice u latinicu.

Ova funkcija konvertuje srpski tekst sa ćirilice na latinicu,
čuvajući specifične srpske karaktere (đ, č, ć, š, ž, lj, nj, dž).
"""


def convert_to_latin(text: str) -> str:
    """
    Konvertuje srpski tekst sa ćirilice na latinicu.
    
    Args:
        text: Tekst na ćirilici
        
    Returns:
        Tekst na latinici
        
    Example:
        >>> convert_to_latin("Неопорезиви износ")
        'Neoporezivi iznos'
        
        >>> convert_to_latin("Годишњи порез на доходак грађана")
        'Godišnji porez na dohodak građana'
    """
    # Mapiranje srpskih ćiriličnih karaktera u latinicu
    cyrillic_to_latin_map = {
        # Velika slova
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Ђ': 'Đ', 'Е': 'E', 'Ж': 'Ž', 'З': 'Z', 'И': 'I',
        'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj', 'М': 'M',
        'Н': 'N', 'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R',
        'С': 'S', 'Т': 'T', 'Ћ': 'Ć', 'У': 'U', 'Ф': 'F',
        'Х': 'H', 'Ц': 'C', 'Ч': 'Č', 'Џ': 'Dž', 'Ш': 'Š',
        
        # Mala slova
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'ђ': 'đ', 'е': 'e', 'ж': 'ž', 'з': 'z', 'и': 'i',
        'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj', 'м': 'm',
        'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'ћ': 'ć', 'у': 'u', 'ф': 'f',
        'х': 'h', 'ц': 'c', 'ч': 'č', 'џ': 'dž', 'ш': 'š'
    }
    
    # Konvertuj karakter po karakter
    result = []
    for char in text:
        # Ako je ćirilični karakter, konvertuj ga
        if char in cyrillic_to_latin_map:
            result.append(cyrillic_to_latin_map[char])
        else:
            # Inače, zadrži originalni karakter (brojevi, interpunkcija, itd.)
            result.append(char)
    
    return ''.join(result)


def is_cyrillic(text: str) -> bool:
    """
    Proverava da li tekst sadrži ćirilične karaktere.
    
    Args:
        text: Tekst za proveru
        
    Returns:
        True ako tekst sadrži bar jedan ćirilični karakter, False inače
        
    Example:
        >>> is_cyrillic("Неопорезиви износ")
        True
        
        >>> is_cyrillic("Neoporezivi iznos")
        False
    """
    cyrillic_chars = set('АБВГДЂЕЖЗИЈКЛЉМНЊОПРСТЋУФХЦЧЏШабвгдђежзијклљмнњопрстћуфхцчџш')
    return any(char in cyrillic_chars for char in text)


def convert_mixed_text(text: str) -> str:
    """
    Konvertuje tekst koji može sadržati i ćirilicu i latinicu.
    Ćirilični delovi se konvertuju, latinični ostaju nepromenjeni.
    
    Args:
        text: Tekst sa mešanom ćirilicom i latinicom
        
    Returns:
        Tekst u potpunosti na latinici
        
    Example:
        >>> convert_mixed_text("Неопорезиви iznos је 5.439.096 dinara")
        'Neoporezivi iznos je 5.439.096 dinara'
    """
    return convert_to_latin(text)

# Made with Bob
