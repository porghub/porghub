from pathlib import Path
import dotenv

dotenv.load_dotenv()

import uuid
import aiofiles
from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Request,
    Depends,
    HTTPException,
    UploadFile,
    status,
    Form,
)
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
import secrets
import os
from tortoise.contrib.fastapi import register_tortoise

import db
from models.memes import MemeResponse, Memes

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)
app.mount(
    "/attachments",
    StaticFiles(directory="attachments"),
    name="attachments",
)

admin_auth = HTTPBasic()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/sent", response_class=HTMLResponse)
async def sent(request: Request):
    return templates.TemplateResponse("sent.html", {"request": request})


@app.post("/sent", response_class=HTMLResponse)
async def sent(
    request: Request,
    background_tasks: BackgroundTasks,
    credit: str | None = Form(None),
    media: UploadFile = File(None),
):
    id = uuid.uuid4().hex

    meme = await Memes.create(credit=credit, image=id)
    filename = f"uploads/{meme.image}"

    async with aiofiles.open(filename, "wb") as image_file:
        while content := await media.read(1024):
            await image_file.write(content)

    background_tasks.add_task(process_image, filename, meme.image)

    return templates.TemplateResponse("sent.html", {"request": request})


def process_image(original_file: str, meme_id: str):
    new_file = f"attachments/{meme_id}.png"

    with Image.open(original_file) as image:
        image.save(new_file)

    os.remove(original_file)


@app.get("/oldies-but-goldies", response_class=HTMLResponse)
async def oldies(request: Request):
    porghub = sorted(Path("static/porghub").iterdir(), key=os.path.getmtime)
    alcohol = sorted(
        Path("static/porg_memes_for_alcoholic_teens").iterdir(),
        key=os.path.getmtime,
    )

    return templates.TemplateResponse(
        "oldies.html",
        {"request": request, "porghub": porghub, "alcohol": alcohol},
    )


def get_admin_auth(credentials: HTTPBasicCredentials = Depends(admin_auth)):
    correct_username = secrets.compare_digest(
        os.getenv("PORGHUB_USERNAME"), credentials.username
    )
    correct_password = secrets.compare_digest(
        os.getenv("PORGHUB_PASSWORD"), credentials.password
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Co tady sakra zkoušíš?",
        )


@app.get("/admin", response_class=HTMLResponse)
async def admin(
    request: Request,
    _=Depends(get_admin_auth),
):
    memes = await MemeResponse.from_queryset(
        Memes.all().order_by("-created_at")
    )

    return templates.TemplateResponse(
        "admin.html", {"request": request, "memes": memes}
    )


register_tortoise(
    app,
    config=db.TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)
