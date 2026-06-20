from mcstatus import JavaServer
from pydantic import Field
from pydantic.dataclasses import dataclass

from astrbot.api import logger
from astrbot.core.agent.run_context import ContextWrapper
from astrbot.core.agent.tool import FunctionTool, ToolExecResult
from astrbot.core.astr_agent_context import AstrAgentContext


@dataclass
class JEMSSTool(FunctionTool[AstrAgentContext]):
    name: str = "je_server_status"  # 工具名称
    description: str = "A tool to get Minecraft JE server status."  # 工具描述
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

    """
    TODO:说不定以后可以实现模组查询
    """
    async def call(
        self, context: ContextWrapper[AstrAgentContext], **kwargs
    ) -> ToolExecResult:
        server_address = kwargs["server_address"]
        try:
            server = await JavaServer.async_lookup(server_address)
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
                    "channels": server_status.forge_data.channels,
                    "mods": [
                        {"name": mod.name, "marker": mod.marker}
                        for mod in server_status.forge_data.mods
                    ],
                }
            return str(tool_result)
        except Exception as e:
            logger.error(f"Tool Can't get server information {server_address}")
            logger.error(f"Tool Error info: {e}")
            return f"Failed to get server status: {e}"
