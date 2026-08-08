from pydantic import BaseModel, field_validator, model_validator

from .exceptions import ConfigException, PluginErrorCode


class GeneralConfig(BaseModel):
    is_info_card_enabled: bool = True
    is_info_text_enabled: bool = True


class QuickPingServerConfig(BaseModel):
    quick_name: str
    is_default: bool = False
    is_bedrock: bool = False
    address: str
    display_name: str


class QuickPingConfig(BaseModel):
    servers: list[QuickPingServerConfig] = []

    # TODO:地址是否合规也应该检查
    @field_validator("servers", mode="after")
    @classmethod
    def check_duplicate_quick_server(cls, servers: list):
        checked_quick_names = []
        is_default_server_identified = False
        for server in servers:
            if server.quick_name in checked_quick_names:
                raise ConfigException(
                    PluginErrorCode.CFG_DUPLICATE_QUICK_NAME,
                    f"Duplicate quick_name '{server.quick_name}' in config quick_ping.servers.",
                )
            else:
                checked_quick_names.append(server.quick_name)
                if server.is_default:
                    if not is_default_server_identified:
                        is_default_server_identified = True
                    else:
                        raise ConfigException(
                            PluginErrorCode.CFG_DUPLICATE_DEFAULT_SERVER,
                            f"Duplicate default server '{server.quick_name}' in config quick_ping.servers.",
                        )

        return servers


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
                "Config item ping_indicator's ping_thresholds has wrong order.The order must be excellent < good < medium < bad.",
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
