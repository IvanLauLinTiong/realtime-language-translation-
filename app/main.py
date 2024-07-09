
import pathlib
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from schemas import TaskResponse, TranslationRequest


app = FastAPI()

BASE_DIR = pathlib.Path(__file__).parent

# setup templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/index", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Enable CORS (need to adjust accordingly if deploy in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/translate", response_model=TaskResponse)
def translate(request: TranslationRequest, background_tasks: BackgroundTasks):

    task = create_translation_task(...)

    background_tasks.add_task(perform_translation, task.id, request.text, request.languages, db)

    return {"task_id": task.id}

