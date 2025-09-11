import re
import json

from .models import Term, TermCategory
from app.constants import TERMINOLOGY_FILE_PATH

terminology: list[Term] = []

def search_terminology(query: str, category: TermCategory | None = None) -> list[Term]:
    global terminology
    if not terminology:
        __init__()

    results = [v for v in terminology if (re.search(v.index_regex, query) and (not category or category in v.categories))]
    return results

def __init__():
    global terminology
    
    file = open(TERMINOLOGY_FILE_PATH, "r")
    data = json.load(file)
    terminology = [Term(**glossary) for glossary in data]                                   