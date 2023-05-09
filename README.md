# Robotic Synthesis Platform Operational Control

## Installation

This project uses [Poetry](https://python-poetry.org/docs/#installation) for dependecies management. 

Install Poetry with pip and the current package with the following commands:

```shell
pip install poetry
poetry install
```

## Getting Started

Start the server with HTTP API at port 9000:

```shell
poetry run uvicorn controller.main:app --port 9000
```

Start querying the API:

```shell
curl localhost:9000/start
```

## Configuration

Environmental variable `LLE_API_SETTINGS_PATH` can be used to specify the path to the configuration file. The default value is `lle_settings.json`. 

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