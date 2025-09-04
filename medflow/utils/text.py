# medflow/utils/text.py
import unicodedata
import re

def normalize_sans_accents(s: str) -> str:
    """
    Normaliza removendo acentos, casefold, e colapsando espaços.
    Ex.: " Térreo  " -> "terreo"
    """
    if s is None:
        return ''
    s = s.strip()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = s.casefold()
    s = re.sub(r'\s+', ' ', s)
    return s
