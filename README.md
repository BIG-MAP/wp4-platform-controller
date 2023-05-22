# Robotic Synthesis Platform Operational Control

![CI](https://github.com/BIG-MAP/wp4-platform-controller/actions/workflows/build.yaml/badge.svg)
![Version](https://img.shields.io/github/v/tag/BIG-MAP/wp4-platform-controller)

## Getting Started with Docker

This pulls the latest version of the software:

```shell
docker pull nokal/wp4-platform-controller
```

Run it with:

```shell
docker run -p 9000:9000 -e LLE_API_URL=http://lle:8000 -e PLC_API_URL=opc.tcp://plc:4840 nokal/wp4-platform-controller
```

The controller is accessible at port 9000:

```
curl localhost:9000/start
```

## Getting Started from Source

This project uses [Poetry](https://python-poetry.org/docs/#installation) for dependencies management. 

Install Poetry with pip and the current package with the following commands:

```shell
pip install poetry
poetry install
```

Start the server with HTTP API at port 9000:

```shell
poetry run uvicorn controller.main:app --port 9000
```

Start querying the API:

```shell
curl localhost:9000/start
```

## Configuration

Environmental variable `LLE_API_SETTINGS_PATH` can be used to specify the path to the configuration file inside a container. 

To use a custom configuration file, mount it to the container and set the environmental variable to the path inside the container.

The default value is `lle_settings.json`. 

Default settings are the following:

```json
{
    "liquid_type": "ethyl", // ethyl or dichloro
    "settlingSettings": {
        "scanInterval": 20,
        "maxTime": 120
    },
    "scanSettings": {
        "initialLEDs": 4,
        "deltaLEDs": 16,
        "travelDistance": 169
    },
    "detectionSettings": {
        "smoothWindowSize": 7,
        "smoothProminence": 0.06666666666666667,
        "gradient2Prominence": 0.3333333333333333
    },
    "drainSettings": {
        "portLower": 1,
        "portUpper": 2,
        "mlToDrainUpper": 500
    }
}
```

## Getting Started with Airflow

This project also contains an [Apache Airflow](https://airflow.apache.org) workflow that can be used instead of the RootController's internal state management (which is triggered by calling `localhost:9000/start`).

Airflow-related dependencies are optional and can be installed with:

```shell
poetry install --with airflow
```

Airflow-related files and scripts are located in the `./airflow` directory. It contains the following files:

- `dags` directory with the Airflow DAGs
- `docker-compose.yml` Docker Compose manifest to start Airflow and all related services

To start Airflow and all related services, run the following command from `./airflow` directory:

```shell
docker compose up
```

After all services are started successfully, the Airflow UI is accessible at [localhost:8080](http://localhost:8080). 

The DAGs are automatically loaded from the `./airflow/dags` directory. 

Default username is `airflow`, password is `airflow`.