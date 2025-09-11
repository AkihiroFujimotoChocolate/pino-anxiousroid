import re
import json

from .models import AditionalRule
from app.constants import ADDITIONAL_RULES_FILE_PATH

additional_rules: list[AditionalRule] = []

def search_additional_rules(query:str) -> list[AditionalRule]:
    global additional_rules
    if not additional_rules:
        __init__()

    results = [v for v in additional_rules if re.search(v.index_regex, query)]
    return results

def __init__():
    global additional_rules
    
    file = open(ADDITIONAL_RULES_FILE_PATH, "r")
    data = json.load(file)
    additional_rules = [AditionalRule(**rule) for rule in data]                                   