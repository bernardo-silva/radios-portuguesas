from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
from radio import available_radios

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

radios = available_radios()
radio_indices = {radio.name: n for n, radio in enumerate(radios)}

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "radios": radios})

@app.get("/radio/{radio_name}")
async def update_data(radio_name: str, request: Request):
    radio = radios[radio_indices[radio_name]]
    # radio.fetch()

    context = {"request": request, "radio_name": radio_name, "song": radio.current_song}

    return templates.TemplateResponse("song.html", context)

@app.on_event('startup')
async def app_startup():
    for radio in radios:
        asyncio.create_task(radio.poll(10))
