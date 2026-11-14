import ipaddress
import re
import string

import idna

from .exceptions import InputException, PluginErrorCode

# 此处 _ASCII_CHARACTERS 不包含下划线（_）因为直接输入SRV名字是不符合SRV记录的用途的
_ASCII_CHARACTERS = frozenset(string.ascii_letters + string.digits + ".-")
_PORT_PATTERN = re.compile(r"[0-9]{1,5}")
_ATON_PART = re.compile(r"(?:[0-9]+|0[xX][0-9a-fA-F]+)")


def _validate_port(raw_port: str) -> int:
    """解析并校验端口号"""
    if not re.fullmatch(_PORT_PATTERN, raw_port):
        raise InputException(
            PluginErrorCode.INP_INVALID_SERVER_ADDRESS, "Invalid input address."
        )
    port = int(raw_port)
    if port < 1 or port > 65535:
        raise InputException(
            PluginErrorCode.INP_INVALID_SERVER_ADDRESS, "Invalid input address."
        )
    return port


# TODO:细化错误反馈
def parse_server_address(address: str) -> tuple[str, int | None]:
    """校验并返回可用的服务器 address"""
    address = address.strip()
    host: str
    port: int | None

    # 初步解析 port
    # IPv6 处理分支
    if address.startswith("["):
        end_index = address.find("]")
        if end_index == -1:
            raise InputException(
                PluginErrorCode.INP_INVALID_SERVER_ADDRESS, "Invalid input address."
            )
        host = address[1:end_index]
        rest = address[end_index + 1 :]
        if rest == "":
            port = None
        elif rest.startswith(":"):
            port = _validate_port(rest[1:])
        else:
            raise InputException(
                PluginErrorCode.INP_INVALID_SERVER_ADDRESS, "Invalid input address."
            )
    # IPv4 / 域名处理分支
    elif address.count(":") == 1:
        host, _, rest = address.partition(":")
        port = _validate_port(rest)
    elif address.count(":") == 0:
        host = address
        port = None
    # 这意味着不支持裸 IPv6
    else:
        raise InputException(
            PluginErrorCode.INP_INVALID_SERVER_ADDRESS, "Invalid input address."
        )

    # 验证 IP
    try:
        ipaddress.ip_address(host)
        return host, port
    except ValueError:
        pass

    # 验证 glibc inet_aton 风格伪装
    # 注意：这里也会把正常IP拦截，一定放在正常 IP 校验后
    if all(_ATON_PART.fullmatch(part) for part in host.split(".")):
        raise InputException(
            PluginErrorCode.INP_INVALID_SERVER_ADDRESS, "Invalid input address."
        )

    # 验证域名
    if host.isascii():
        if not set(host) <= _ASCII_CHARACTERS:
            raise InputException(
                PluginErrorCode.INP_INVALID_SERVER_ADDRESS, "Invalid input address."
            )
        # 拒绝空标签
        if any(not label for label in host.split(".")):
            raise InputException(
                PluginErrorCode.INP_INVALID_SERVER_ADDRESS, "Invalid input address."
            )
        else:
            return host.lower(), port

    try:
        encoded_host = idna.encode(host).decode()
    except idna.IDNAError:
        raise InputException(
            PluginErrorCode.INP_INVALID_SERVER_ADDRESS, "Invalid input address."
        )
    # 补 。．｡ 这类会被 IDNA 当成 label 分隔符折叠的洞
    if encoded_host.count(".") != host.count("."):
        raise InputException(
            PluginErrorCode.INP_INVALID_SERVER_ADDRESS, "Invalid input address."
        )
    return encoded_host, port
