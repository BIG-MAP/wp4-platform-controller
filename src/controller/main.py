import logging

from controller.system_lle import BaseLLEException, LLESystem
from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)

app = FastAPI()

lle_system = LLESystem(name="LLE", url="http://localhost:8000", polling_interval=2)


@app.get("/")
async def root():
    return {"message": "Robotic Synthesis Platform Operational Control"}


@app.get("/start")
async def start(background_tasks: BackgroundTasks):
    response = await lle_system.start()
    background_tasks.add_task(lle_system.poll)
    return response


@app.get("/stop")
async def stop():
    response = await lle_system.stop()
    return response


@app.get("/status")
async def status():
    return {"status": "running"}


@app.exception_handler(BaseLLEException)
async def base_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": exc.message})
