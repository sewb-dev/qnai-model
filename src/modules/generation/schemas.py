from typing import Union
from pydantic import BaseModel
from src.enums import GenerationStatus


class PostGenerateAPIResponse(BaseModel):
    generationId: str


class GetGenerationAPIResponse(BaseModel):
    status: GenerationStatus
    content: Union[str, None]
    error: Union[str, None]
    sourceText: str


class PostGenerateAPIRequest(BaseModel):
    text: str
    numOfQuestions: int = 10
