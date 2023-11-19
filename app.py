from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sse_starlette import EventSourceResponse, ServerSentEvent
import asyncio
from radio import available_radios

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

radios = available_radios()
radio_indices = {radio.name: n for n, radio in enumerate(radios)}

class Stream:
    def __init__(self) -> None:
        self._queue = asyncio.Queue[ServerSentEvent]()

    def __aiter__(self) -> "Stream":
        return self

    async def __anext__(self) -> ServerSentEvent:
        try:
            return await self._queue.get()
        except asyncio.CancelledError as e:
            print(e)
            raise e

    async def asend(self, value: ServerSentEvent) -> None:
        await self._queue.put(value)

_streams: list[Stream] = []


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "radios": radios})

@app.get("/radio/{radio_name}")
async def radio_html(radio_name: str, request: Request):
    radio = radios[radio_indices[radio_name]]
    print(f"Request for {radio.name}")

    context = {"request": request, "radio_name": radio_name, "song": radio.current_song}

    return templates.TemplateResponse("song.html", context)

async def combine_generators(gens):
    iterators = [gen.__aiter__() for gen in gens]

    while iterators:
        done, _ = await asyncio.wait(iterators, return_when=asyncio.FIRST_COMPLETED)
        for it in done:
            try:
                result = await it.__anext__()
                yield result
            except StopAsyncIteration:
                iterators.remove(it)

@app.get("/radio_stream")
async def listen_update(request: Request):
    print("Starting stream from client ", request.client.host, "on port ", request.client.port)
    stream = Stream()
    _streams.append(stream)

    return EventSourceResponse(stream)


async def poll_radios():
    queue = asyncio.Queue()
    for radio in radios:
        asyncio.create_task(radio.poll(10, queue))
    while True:
        radio = await queue.get()
        print("Got update for ", radio.name)
        print("Running: ", len(asyncio.all_tasks()))
        queue.task_done()
        event = ServerSentEvent(data=radio.name, event=f"update_{radio.name}")
        for stream in _streams:
            await stream.asend(event)
    

@app.on_event('startup')
async def app_startup():
    asyncio.create_task(poll_radios())
