from enum import StrEnum


class PluginErrorCode(StrEnum):
    """JEMSSPlugin的错误代码"""

    # SECURITY 安全类
    SEC_PATH_TRAVERSAL = "SEC001"

    # CONFIG 配置类
    CFG_INVALID_PING_THRESHOLDS = "CFG001"
    CFG_EMPTY_OUTPUT = "CFG002"
    CFG_DUPLICATE_QUICK_NAME = "CFG003"

    # RENDER 渲染类
    RND_TEMP_CLEAN = "RND003"
    RND_BACKGROUND_LOAD = "RND004"

    # NETWORK 网络类
    NET_DNS_RESOLUTION = "NET001"
    NET_CONNECTION_REFUSED = "NET002"
    NET_CONNECTION_TIMEOUT = "NET003"
    NET_UNEXPECTED = "NET009"

    # INPUT 输入类
    INP_INVALID_QUICK_NAME = "INP001"
    INP_INVALID_SERVER_ADDRESS = "INP002"

    # 其他
    UNKNOWN_ERROR = "ERR000"


class PluginException(Exception):
    """插件异常基类"""

    def __init__(
        self, code: PluginErrorCode, message: str = "", detail: str | None = None
    ):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class SecurityException(PluginException):
    """安全相关异常"""

    def __init__(self, code: PluginErrorCode, message: str, detail: str | None = None):
        super().__init__(code, message, detail)


class RenderException(PluginException):
    """渲染相关异常"""

    def __init__(self, code: PluginErrorCode, message: str, detail: str | None = None):
        super().__init__(code, message, detail)


class ConfigException(PluginException):
    """配置相关异常"""

    def __init__(self, code: PluginErrorCode, message: str, detail: str | None = None):
        super().__init__(code, message, detail)
