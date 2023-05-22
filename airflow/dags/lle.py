from datetime import datetime

import requests
from airflow.decorators import dag, task


@dag(
    schedule=None,
    start_date=datetime(2021, 1, 1),
    catchup=False,
)
def lle_main_flow():
    controller_api_url = "http://controller:9000"

    @task.sensor(poke_interval=5, timeout=60 * 60 * 24, mode="reschedule")
    def wait_for_lle_finished() -> bool:
        response = requests.get(controller_api_url + "/status").json()
        status = response["systems"]["LLE"]
        return status == "finished"

    @task.sensor(poke_interval=5, timeout=60 * 60 * 24, mode="reschedule")
    def wait_for_plc_started() -> bool:
        response = requests.get(controller_api_url + "/plc/is-started").json()
        return response["is_started"]

    @task
    def set_plc_is_started_false():
        response = requests.put(
            controller_api_url + "/plc/is-started", params={"value": False}
        ).json()
        assert response["is_started"] is False, "PLC is_started should be set to False"

    @task
    def get_status():
        status = requests.get(controller_api_url + "/status").json()
        print(status)

    @task
    def start_settling():
        response = requests.post(controller_api_url + "/lle/start_settling").json()
        assert response["status"] == "running", "LLE is not running"

    @task
    def start_draining():
        response = requests.post(controller_api_url + "/lle/start_draining").json()
        assert response["status"] == "running", "LLE is not running"

    (
        wait_for_plc_started()
        >> set_plc_is_started_false()
        >> start_settling()
        >> wait_for_lle_finished()
        >> start_draining()
        >> wait_for_lle_finished()
        >> get_status()
    )


lle_main_flow()
