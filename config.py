from pydantic import BaseModel, model_validator


class PingIcon(BaseModel):
    is_opened: bool = True
    excellent: int = 50
    good: int = 100
    medium: int = 200
    bad: int = 500

    @model_validator(mode="after")
    def check_order(self) -> "PingIcon":
        if not (self.excellent < self.good < self.medium < self.bad):
            raise ValueError("Config item ping_icon's thresholds have wrong order.The order must be excellent < good < medium < bad")
        return self

class ServerIcon(BaseModel):
    is_opened: bool = True

class ServerTitle(BaseModel):
    is_opened: bool = True

class ServerMotd(BaseModel):
    is_opened: bool = True

class PlayerCount(BaseModel):
    is_opened: bool = True

class PluginConfig(BaseModel):
    ping_icon: PingIcon = PingIcon()
    server_icon: ServerIcon = ServerIcon()
    server_title: ServerTitle = ServerTitle()
    server_motd: ServerMotd = ServerMotd()
    player_count: PlayerCount = PlayerCount()
