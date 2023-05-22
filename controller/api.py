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


@app.post("/lle/start_settling")
async def lle_start_settling() -> dict:
    """
    Starts the settling process of the LLE.
    """
    response = await root_controller.lle.start_settling()
    return response


@app.post("/lle/start_draining")
async def lle_start_draining() -> dict:
    """
    Starts the draining process of the LLE.
    """
    response = await root_controller.lle.start_draining()
    return response


@app.get("/lle/status")
async def lle_status() -> dict:
    """
    Returns the status of the LLE.
    """
    status = await root_controller.lle.get_status()
    return {"status": status}


@app.get("/lle/results")
async def lle_results() -> dict:
    """
    Returns the results of the LLE.
    """
    results = await root_controller.lle.get_results()
    return {"results": results}


@app.get("/plc/is-started")
async def plc_status() -> dict:
    """
    Returns if LLE should be started.
    """
    is_started = await root_controller.plc.should_start()
    return {"is_started": is_started}


@app.put("/plc/is-started")
async def plc_set_is_started(value: bool) -> dict:
    """
    Sets if LLE should be started.
    """
    await root_controller.plc.set_is_started(value)
    return {"is_started": value}


@app.exception_handler(BaseLLEException)
async def base_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": exc.message})
