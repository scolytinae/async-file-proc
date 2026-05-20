from typing import Dict
from pydantic import BaseModel

class FileProcessingResult(BaseModel):
    words_count: int
    average_word_length: int
    words_top: Dict[str, int]
    