from pydantic import BaseModel, model_validator

from .exceptions import ConfigException, PluginErrorCode


class GeneralConfig(BaseModel):
    isInfoCardEnabled: bool = True
    isInfoTextEnabled: bool = True


class PingThresholdsConfig(BaseModel):
    excellent: int = 50
    good: int = 100
    medium: int = 200
    bad: int = 500

    @model_validator(mode="after")
    def check_order(self) -> "PingThresholdsConfig":
        if not (self.excellent < self.good < self.medium < self.bad):
            raise ConfigException(
                PluginErrorCode.CFG_VALIDATION_FAILED,
                "Config item ping_indicator's ping_thresholds has wrong order.The order must be excellent < good < medium < bad",
            )
        return self


class PingIndicatorConfig(BaseModel):
    isEnabled: bool = True
    ping_thresholds: PingThresholdsConfig = PingThresholdsConfig()


class IconConfig(BaseModel):
    isEnabled: bool = True


class TitleConfig(BaseModel):
    isEnabled: bool = True


class MotdConfig(BaseModel):
    isEnabled: bool = True


class PlayerCountConfig(BaseModel):
    isEnabled: bool = True


class BackgroundConfig(BaseModel):
    isCustomEnabled: bool = False
    upload: list[str] = []


class InfoCardConfig(BaseModel):
    ping_indicator: PingIndicatorConfig = PingIndicatorConfig()
    icon: IconConfig = IconConfig()
    title: TitleConfig = TitleConfig()
    motd: MotdConfig = MotdConfig()
    player_count: PlayerCountConfig = PlayerCountConfig()
    background: BackgroundConfig = BackgroundConfig()


class PluginConfig(BaseModel):
    general: GeneralConfig = GeneralConfig()
    info_card: InfoCardConfig = InfoCardConfig()
