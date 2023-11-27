from typing import Union
from src.modules.generation.service import generation_settings
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


@app.get("/")
def status():
    return "ok"


@app.post("/generate")
async def create_generate(
    text: str, numOfQuestions: int, background_tasks: BackgroundTasks
):
    generationId = str(generation_settings.generation_id())
    background_tasks.add_task(
        generation_settings.generate, text, numOfQuestions, generationId
    )
    return {"generationId": generationId}


@app.get("/generate/${id}")
async def get_generation(id: str):
    response = await generation_settings.generation_status(generationId=id)
    return response
