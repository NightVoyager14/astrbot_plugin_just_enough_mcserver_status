import json

from mcstatus import BedrockServer, JavaServer
from pydantic import Field
from pydantic.dataclasses import dataclass

from astrbot.api import logger
from astrbot.core.agent.run_context import ContextWrapper
from astrbot.core.agent.tool import FunctionTool, ToolExecResult
from astrbot.core.astr_agent_context import AstrAgentContext

from .exceptions import InputException
from .validator import parse_server_address


@dataclass
class JEMSSJavaTool(FunctionTool[AstrAgentContext]):
    name: str = "mcje_server_status"  # 工具名称
    description: str = "Get Minecraft Java Edition server status."  # 工具描述
    parameters: dict = Field(
        default_factory=lambda: {
            "type": "object",
            "properties": {
                "server_address": {
                    "type": "string",
                    "description": "Minecraft Java Edition server address. Format: 'host[:port]', where port is optional and defaults to 25565. Do NOT include protocol (e.g., 'http://') or trailing slashes. Examples: 'play.example.com:25565' or '127.0.0.1'.",
                },
            },
            "required": ["server_address"],
        }
    )

    # TODO:目前由于依赖库限制，只支持Forge的mods查询
    async def call(
        self, context: ContextWrapper[AstrAgentContext], **kwargs
    ) -> ToolExecResult:
        server_address = kwargs["server_address"]
        try:
            server_host, server_port = parse_server_address(server_address)
            # 重新构建合规地址
            if server_port:
                java_server_address = f"{server_host}:{server_port}"
            else:
                java_server_address = f"{server_host}"
            server = await JavaServer.async_lookup(java_server_address, timeout=3)
            server_status = await server.async_status()
            tool_result = {
                "address": f"{server.address.host}:{server.address.port}",
                "version": {
                    "name": server_status.version.name,
                    "protocol": server_status.version.protocol,
                },
                "player": {
                    "online": server_status.players.online,
                    "max": server_status.players.max,
                    "sample": None,
                },
                "latency": server_status.latency,
                "modinfo": None,
                "motd": server_status.motd.to_html(),
            }
            # sample player于modinfo滞后处理，防止为None
            if server_status.players.sample:
                tool_result["player"]["sample"] = [
                    {player.name: player.id} for player in server_status.players.sample
                ]
            if server_status.forge_data:
                tool_result["modinfo"] = {
                    "fml_network_version": server_status.forge_data.fml_network_version,
                    "mods": [
                        {"name": mod.name, "marker": mod.marker}
                        for mod in server_status.forge_data.mods
                    ],
                }
            return json.dumps(tool_result, ensure_ascii=False, separators=(",", ":"))
        except InputException as e:
            logger.error(f"Tool Can't get server information {server_address}")
            logger.error(f"Tool Error info: {e}")
            return "Invalid input address."
        except Exception as e:
            logger.error(f"Tool Can't get server information {server_address}")
            logger.error(f"Tool Error info: {e}")
            return f"Failed to get server status: {e}"


@dataclass
class JEMSSBedrockTool(FunctionTool[AstrAgentContext]):
    name: str = "mcbe_server_status"  # 工具名称
    description: str = "Get Minecraft Bedrock Edition server status."  # 工具描述
    parameters: dict = Field(
        default_factory=lambda: {
            "type": "object",
            "properties": {
                "server_address": {
                    "type": "string",
                    "description": "Minecraft Bedrock Edition server address. Format: 'host[:port]', where port is optional and defaults to 19132. Do NOT include protocol (e.g., 'http://') or trailing slashes. Examples: 'play.example.com:19132' or '127.0.0.1'.",
                },
            },
            "required": ["server_address"],
        }
    )

    async def call(
        self, context: ContextWrapper[AstrAgentContext], **kwargs
    ) -> ToolExecResult:
        server_address = kwargs["server_address"]
        try:
            parsed_address = parse_server_address(server_address)
            server_host = parsed_address[0]
            # 由于 mcstatus 会在 port 为 None 自动补为默认端口，所以这里不做处理
            server_port = parsed_address[1]
            server = BedrockServer(server_host, server_port, timeout=3)
            server_status = await server.async_status()
            tool_result = {
                "address": f"{server.address.host}:{server.address.port}",
                "version": {
                    "name": server_status.version.name,
                    "protocol": server_status.version.protocol,
                    "brand": None,
                },
                "map_name": server_status.map_name,
                "game_mode": server_status.gamemode,
                "player": {
                    "online": server_status.players.online,
                    "max": server_status.players.max,
                },
                "latency": server_status.latency,
                "motd": server_status.motd.to_html(),
            }
            if server_status.version.brand == "MCPE":
                tool_result["version"]["brand"] = "Bedrock Edition"
            elif server_status.version.brand == "MCEE":
                tool_result["version"]["brand"] = "Education Edition"
            return json.dumps(tool_result, ensure_ascii=False, separators=(",", ":"))
        except InputException as e:
            logger.error(f"Tool Can't get server information {server_address}")
            logger.error(f"Tool Error info: {e}")
            return "Invalid input address."
        except Exception as e:
            logger.error(f"Tool Can't get server information {server_address}")
            logger.error(f"Tool Error info: {e}")
            return f"Failed to get server status: {e}"
