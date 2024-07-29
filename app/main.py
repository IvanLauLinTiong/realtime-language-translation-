
import pathlib
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from schemas import TaskResponse, TranslationRequest, TranslationStatus
from database import get_db, engine
from crud import create_translation_task, get_translation_task
from utils import perform_translation
import models



models.Base.metadata.create_all(bind=engine)
app = FastAPI()

BASE_DIR = pathlib.Path(__file__).parent

# setup templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Enable CORS (need to adjust accordingly if deploy in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/index", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/translate", response_model=TaskResponse)
def translate(request: TranslationRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    task = create_translation_task(db, request.text, request.languages)

    background_tasks.add_task(perform_translation, task.id, request.text, request.languages, db)

    return {"task_id": task.id}

@app.get("/translate/{task_id}", response_model=TranslationStatus)
def get_translate_status(task_id: int, db: Session = Depends(get_db)):

    task = get_translation_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return {"task_id": task.id, "status": task.status, "translations": task.translations}

@app.get("/translate/content/{task_id}")
def get_translate_content(task_id: int, db: Session = Depends(get_db)):

    task = get_translation_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task

