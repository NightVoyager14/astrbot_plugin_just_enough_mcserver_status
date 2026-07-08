from pydantic import BaseModel, model_validator


class PingThresholds(BaseModel):
    is_opened: bool = True
    excellent: int = 50
    good: int = 100
    medium: int = 200
    bad: int = 500

    @model_validator(mode="after")
    def check_order(self) -> "PingThresholds":
        if not (self.excellent < self.good < self.medium < self.bad):
            raise ValueError("Config item ping_thresholds has wrong order.The order must be excellent < good < medium < bad")
        return self


class PluginConfig(BaseModel):
    ping_thresholds: PingThresholds
