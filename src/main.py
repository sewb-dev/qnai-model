from src.logger import setup_logger
from src.modules.generation.service import generation_service, allow_request
from fastapi import BackgroundTasks, FastAPI, Depends
from src.settings import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from src.modules.generation import schemas

setup_logger()


app = FastAPI(title="QNAI Model API")
header_scheme = APIKeyHeader(name="x-caller-token")


origins = settings.BACKEND_CORS_ORIGINS


@app.get("/")
def status():
    return "ok"


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generations", response_model=schemas.PostGenerateAPIResponse)
async def create_generate(
    body: schemas.PostGenerateAPIRequest,
    background_tasks: BackgroundTasks,
    caller_token: str = Depends(header_scheme),
):
    allow_request(caller_token)

    generationId = str(generation_service.get_generation_id())
    background_tasks.add_task(
        generation_service.generate, body.text, body.numOfQuestions, generationId
    )
    return {"generationId": generationId}


@app.get("/generations/{id}", response_model=schemas.GetGenerationAPIResponse)
async def get_generation(
    id: str,
    caller_token: str = Depends(header_scheme),
):
    allow_request(caller_token)
    response = await generation_service.get_generation(generationId=id)
    return response
