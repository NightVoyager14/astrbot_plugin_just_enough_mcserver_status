from copy import deepcopy

from pydantic import BaseModel, ValidationError, field_validator, model_validator

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
    def check_duplicate_quick_server(cls, servers: list[QuickPingServerConfig]):
        # 注意，此处检测出的重复字段都只会保留后检测到的重复的index而不会保留第一次检测到的index
        # 检查重复quick_name
        checked_quick_names = []
        duplicated_quick_name_indexes = []
        duplicated_quick_names = set()
        for index, server in enumerate(servers):
            if server.quick_name in checked_quick_names:
                duplicated_quick_name_indexes.append(index)
                duplicated_quick_names.add(server.quick_name)
            else:
                checked_quick_names.append(server.quick_name)
        if duplicated_quick_name_indexes:
            names = ", ".join(f"'{name}'" for name in duplicated_quick_names)
            raise ConfigException(
                PluginErrorCode.CFG_DUPLICATE_QUICK_NAME,
                f"Duplicate quick_name {names} in config quick_ping.servers.",
                indexes=duplicated_quick_name_indexes,
            )
        # 检查重复的default server
        is_default_server_identified = False
        duplicated_default_server_indexes = []
        duplicated_default_server_names = []
        for index, server in enumerate(servers):
            if server.is_default:
                if not is_default_server_identified:
                    is_default_server_identified = True
                else:
                    duplicated_default_server_indexes.append(index)
                    duplicated_default_server_names.append(server.quick_name)
        if duplicated_default_server_indexes:
            names = ", ".join(f"'{name}'" for name in duplicated_default_server_names)
            raise ConfigException(
                PluginErrorCode.CFG_DUPLICATE_DEFAULT_SERVER,
                f"Duplicate default server {names} in config quick_ping.servers.",
                indexes=duplicated_default_server_indexes,
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


class TimestampConfig(BaseModel):
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
    timestamp: TimestampConfig = TimestampConfig()
    background: BackgroundConfig = BackgroundConfig()


class TextInfoConfig(BaseModel):
    is_markdown_enabled: bool = True


class PluginConfig(BaseModel):
    general: GeneralConfig = GeneralConfig()
    quick_ping: QuickPingConfig = QuickPingConfig()
    text_info: TextInfoConfig = TextInfoConfig()
    info_card: InfoCardConfig = InfoCardConfig()


def build_config_with_fallback(origin_config: dict) -> tuple[PluginConfig, list[str]]:
    """构建完整且合法的配置"""
    MAX = 10  # 最大校验次数
    notes = []

    # 深度拷贝传入配置防止更改
    sanitized_config = deepcopy(dict(origin_config))
    for _ in range(MAX):
        try:
            config = PluginConfig.model_validate(sanitized_config)
            return config, notes
        except ConfigException as e:
            # 重复快捷名称剔除
            if e.code == PluginErrorCode.CFG_DUPLICATE_QUICK_NAME:
                notes.append(
                    f"[{PluginErrorCode.CFG_DUPLICATE_QUICK_NAME}] {e.message}"
                )
                # 原本indexes是升序，这里调换为降序以便逐一删除
                for index in reversed(e.indexes):
                    del sanitized_config["quick_ping"]["servers"][index]
            # 修正重复的默认服务器
            elif e.code == PluginErrorCode.CFG_DUPLICATE_DEFAULT_SERVER:
                notes.append(
                    f"[{PluginErrorCode.CFG_DUPLICATE_DEFAULT_SERVER}] {e.message}"
                )
                for index in e.indexes:
                    sanitized_config["quick_ping"]["servers"][index]["is_default"] = (
                        False
                    )
            elif e.code == PluginErrorCode.CFG_INVALID_PING_THRESHOLDS:
                notes.append(
                    f"[{PluginErrorCode.CFG_INVALID_PING_THRESHOLDS}] {e.message}"
                )
                sanitized_config["info_card"]["ping_indicator"]["ping_thresholds"] = {}
        # 修正其他错误
        # TODO:细化错误分类
        except ValidationError as e:
            # 将字段与列表索引分开处理
            field_paths: list[tuple] = []
            list_drops: dict[
                tuple, set
            ] = {}  # 注意因为此处从中截取路径导致后面路径信息抛弃，pydantic可能对同一路径多次报错，所以用集合去重
            for detail in e.errors():
                location = detail["loc"]
                # 防止location为空的整个配置出现问题的情况
                if not location:
                    notes.append(
                        f"[{PluginErrorCode.CFG_VALIDATION_ERROR}] Top-level config error, falling back entirely."
                    )
                    return PluginConfig(), notes
                notes.append(
                    f"[{PluginErrorCode.CFG_VALIDATION_ERROR}] Error type: {detail['type']}\nConfig location: {detail['loc']}\nMessage: {detail['msg']}\nValue: {detail['input']}"
                )
                is_list = False
                for index, key in enumerate(location):
                    if isinstance(key, int):
                        list_drops.setdefault(location[:index], set()).add(
                            location[index]
                        )
                        is_list = True
                        break
                if not is_list:
                    field_paths.append(location)

            # 对纯字段进行清洗
            for path in field_paths:
                parent = sanitized_config
                for key in path[:-1]:
                    parent = parent[key]
                parent.pop(path[-1], None)

            # 对含有列表项路径进行清洗
            for path, indexes in list_drops.items():
                target = sanitized_config
                for key in path:
                    target = target[key]
                for index in sorted(indexes, reverse=True):
                    del target[index]

    notes.append(
        f"[{PluginErrorCode.CFG_VALIDATION_ERROR}] Cannot fix config error, falling back entirely."
    )
    return PluginConfig(), notes
