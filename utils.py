import re
from typing import List

def extractString(string) -> List[int]:
    pattern = r'\d+'
    numbers = re.findall(pattern, string)
    numbers = [int(num) for num in numbers]
    return numbers

def formatDateString(string) -> str:
    pattern = r'[^\w\s]'
    cleaned_string = re.sub(pattern, '', string)
    return cleaned_string
