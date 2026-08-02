from pydantic import BaseModel, field_validator, model_validator

from .exceptions import ConfigException, PluginErrorCode


class GeneralConfig(BaseModel):
    is_info_card_enabled: bool = True
    is_info_text_enabled: bool = True


class QuickPingConfig(BaseModel):
    servers: list = []

    # TODO:地址是否合规也应该检查
    @field_validator("servers", mode="after")
    @classmethod
    def check_duplicate_quick_name(cls, servers: list):
        seen_quick_names = []
        for server in servers:
            if server["quick_name"] in seen_quick_names:
                raise ConfigException(
                    PluginErrorCode.CFG_DUPLICATE_QUICK_NAME,
                    f"Duplicate quick_name '{server['quick_name']}' in config quick_ping.servers.",
                )
            else:
                seen_quick_names.append(server["quick_name"])
        return servers


class QuickPingServersConfig(BaseModel):
    template_key: str
    quick_name: str
    is_bedrock: bool = False
    address: str
    display_name: str


class PingThresholdsConfig(BaseModel):
    excellent: int = 50
    good: int = 100
    medium: int = 200
    bad: int = 500

    @model_validator(mode="after")
    def check_order(self) -> "PingThresholdsConfig":
        if not (self.excellent < self.good < self.medium < self.bad):
            raise ConfigException(
                PluginErrorCode.CFG_INVALID_PING_THRESHOLDS,
                "Config item ping_indicator's ping_thresholds has wrong order.The order must be excellent < good < medium < bad",
            )
        return self


class PingIndicatorConfig(BaseModel):
    is_enabled: bool = True
    ping_thresholds: PingThresholdsConfig = PingThresholdsConfig()


class IconConfig(BaseModel):
    is_enabled: bool = True


class TitleConfig(BaseModel):
    is_enabled: bool = True


class MotdConfig(BaseModel):
    is_enabled: bool = True
    leading: int = 10


class PlayerCountConfig(BaseModel):
    is_enabled: bool = True


class BackgroundConfig(BaseModel):
    is_custom_enabled: bool = False
    upload: list[str] = []


class InfoCardConfig(BaseModel):
    ping_indicator: PingIndicatorConfig = PingIndicatorConfig()
    icon: IconConfig = IconConfig()
    title: TitleConfig = TitleConfig()
    motd: MotdConfig = MotdConfig()
    player_count: PlayerCountConfig = PlayerCountConfig()
    background: BackgroundConfig = BackgroundConfig()


class TextInfoConfig(BaseModel):
    is_markdown_enabled: bool = True


class PluginConfig(BaseModel):
    general: GeneralConfig = GeneralConfig()
    quick_ping: QuickPingConfig = QuickPingConfig()
    text_info: TextInfoConfig = TextInfoConfig()
    info_card: InfoCardConfig = InfoCardConfig()
