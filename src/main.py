from src.middlewares import AddProcessTimeHeader
from src.logger import setup_logger
from src.modules.generation.service import generation_settings, allow_request
from fastapi import BackgroundTasks, FastAPI, Depends
from src.settings import settings
from src.enums import Environment
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader

setup_logger()


app = FastAPI(title="qnai.sewb.dev Model API")
header_scheme = APIKeyHeader(name="x-caller-token")


origins = (
    ["http://localhost:3000"]
    if settings.ENVIRONMENT == Environment.DEVELOPMENT.value
    else ["https://qnai.sewb.dev"]
)


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
app.add_middleware(AddProcessTimeHeader)


@app.post("/generate")
async def create_generate(
    text: str,
    numOfQuestions: int,
    background_tasks: BackgroundTasks,
    caller_token: str = Depends(header_scheme),
):
    allow_request(caller_token)

    generationId = str(generation_settings.generation_id())
    background_tasks.add_task(
        generation_settings.generate, text, numOfQuestions, generationId
    )
    return {"generationId": generationId}


@app.get("/generate/${id}")
async def get_generation(
    id: str,
    caller_token: str = Depends(header_scheme),
):
    allow_request(caller_token)
    response = await generation_settings.generation_status(generationId=id)
    return response
