from typing import Dict
from pydantic import BaseModel

class FileReadResult(BaseModel):
    file_name: str
    text: str

class FileProcessingResult(BaseModel):
    file_name: str
    words_count: int
    average_word_length: int
    # words_top: Dict[str, int]
    