from pydantic import BaseModel


class FileReadResult(BaseModel):
    file_name: str
    text: str


class FileProcessingResult(BaseModel):
    file_name: str
    words_count: int
    average_word_length: float
    words_top: dict[str, int]
