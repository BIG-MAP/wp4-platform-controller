import logging
import os

from controller.root import RootController
from controller.system_lle import BaseLLEException, LLESystem
from controller.system_lle_settings import Settings as LLEAPISettings
from controller.system_plc import PLCClientSettings, PLCSystem
from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)

app = FastAPI()

plc_system = PLCSystem(
    name="PLC",
    url="opc.tcp://localhost:4840",
    client_settings=PLCClientSettings(
        namespace_id=2, lle_id=1, lle_is_started_id=2, lle_status_id=3, lle_results_id=4
    ),
)

lle_api_settings_path = os.environ.get("LLE_API_SETTINGS_PATH", "lle_settings.json")
lle_api_settings = LLEAPISettings.from_file(lle_api_settings_path)
logging.info("LLE API settings: %s", lle_api_settings)
lle_system = LLESystem(
    name="LLE",
    url="http://localhost:8000",
    settings=lle_api_settings,
)

root_controller = RootController(plc_system, lle_system)


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
