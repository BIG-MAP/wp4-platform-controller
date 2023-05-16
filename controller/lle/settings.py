from enum import Enum

from pydantic import BaseModel, Field


class SettlingSettings(BaseModel):
    scanInterval: int = Field(
        20,
        title="The interval for scanning",
        description="The interval for scanning the funnel in seconds",
        gt=0,
        example=4,
    )
    maxTime: int = Field(
        120,
        title="",
        description="The increase step for turning LEDs on",
        gt=0,
        example=16,
    )


class ScanSettings(BaseModel):
    initialLEDs: int = Field(
        4,
        title="The initial LEDs used",
        description="The number of initial LEDs used",
        gt=0,
        example=4,
    )
    deltaLEDs: int = Field(
        16,
        title="The increase step",
        description="The increase step for turning LEDs on",
        gt=0,
        example=16,
    )
    travelDistance: int = Field(
        169,
        title="The distance traveled in mm",
        description="The distance the sensor travels from its initial position",
        gt=0,
        le=169,
        example=169,
    )


class DetectionSettings(BaseModel):
    smoothWindowSize: int = Field(7, title="The size of window for smoothing")
    smoothProminence: float = Field(
        1 / 15,
        description="The prominence used when finding peaks in the smoothed curve",
    )
    gradient2Prominence: float = Field(
        1 / 3,
        description="The prominence used when finding peaks in the second gradient of the curve",
    )


class DrainSettings(BaseModel):
    portLower: int = Field(
        1,
        title="A port number",
        description="The port number to drain the lower phase to",
        gt=0,
        le=4,
        example=1,
    )
    portUpper: int = Field(
        2,
        title="A port number",
        description="The port number to drain the upper phase to",
        gt=0,
        le=4,
        example=1,
    )
    mlToDrainUpper: float | None = Field(
        default=500,
        title="A number of ml",
        description="The number of ml to drain",
        gt=0,
        example=100.0,
    )


class LiquidType(Enum):
    ethyl = "ethyl"
    dichloro = "dichloro"


class Settings(BaseModel):
    liquid_type: LiquidType = Field(
        LiquidType.ethyl,
        title="The liquid type",
        description="The liquid type used in the LLE",
        example=LiquidType.ethyl,
    )
    settlingSettings: SettlingSettings = SettlingSettings()
    scanSettings: ScanSettings = ScanSettings()
    detectionSettings: DetectionSettings = DetectionSettings()
    drainSettings: DrainSettings = DrainSettings()

    @staticmethod
    def from_json(json: str) -> "Settings":
        return Settings.parse_raw(json)

    @staticmethod
    def from_file(path: str) -> "Settings":
        with open(path, "r") as f:
            return Settings.from_json(f.read())
