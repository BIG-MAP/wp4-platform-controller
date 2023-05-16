import logging

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse

from controller.lle.exceptions import BaseLLEException
from controller.root_controller import setup as setup_root_controller

logging.basicConfig(level=logging.INFO)

app = FastAPI()

root_controller = setup_root_controller()


@app.get("/")
async def root():
    return {"message": "Robotic Synthesis Platform Operational Control"}


@app.get("/start")
async def start(background_tasks: BackgroundTasks):
    """
    Starts the root controller to poll the underlying systems, and waits for the PLC start signal
    to notify other systems.
    """
    await root_controller.start()
    background_tasks.add_task(root_controller.poll)
    status = await root_controller.get_status()
    return {"status": status}


@app.get("/start_draining")
async def start_draining(background_tasks: BackgroundTasks):
    """
    Starts the root controller to poll the underlying systems, and waits for the PLC start signal
    to notify other systems. This is used for draining the LLE only. It doesn't start the settling.
    """
    await root_controller.start()
    background_tasks.add_task(root_controller.poll_draining)
    status = await root_controller.get_status()
    return {"status": status}


@app.get("/stop")
async def stop():
    """
    Stops the root controller and underlying systems.
    """
    await root_controller.stop()
    status = await root_controller.get_status()
    return {"status": status}


@app.get("/status")
async def status():
    """
    Returns the status of the root controller.
    """
    status = await root_controller.get_status()
    system_statuses = await root_controller.get_system_statuses()
    return {"status": status, "systems": system_statuses}


@app.exception_handler(BaseLLEException)
async def base_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": exc.message})
