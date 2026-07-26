import json
import random
from pathlib import Path
from socket import gaierror

from mcstatus import JavaServer
from mcstatus.responses.bedrock import BedrockStatusResponse
from mcstatus.responses.java import JavaStatusResponse
from pydantic import ValidationError

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api.star import Context, Star
from astrbot.core.utils import astrbot_path

from .config import PluginConfig
from .exceptions import ConfigException, PluginErrorCode
from .renderer import Renderer
from .tools import JEMSSTool


class JEMSSPlugin(Star):
    # TODO:改进Metadata与程序版本的同步
    __version__ = "v1.1.0"

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        # fmt: off
        # 注册插件
        self.context.add_llm_tools(JEMSSTool())
        # 获取并检查基本路径
        self.plugin_path = (
            Path(astrbot_path.get_astrbot_plugin_path())
            / "astrbot_plugin_just_enough_mcserver_status"
        )
        self.temp_path = Path(astrbot_path.get_astrbot_temp_path()) / "JEMSSPlugin_temp_pics"
        self.temp_path.mkdir(exist_ok=True)
        self.data_path = Path(astrbot_path.get_astrbot_data_path()) / "plugin_data/astrbot_plugin_just_enough_mcserver_status"
        logger.info(f"JEMSSPlugin Path: {self.plugin_path}")
        logger.info(f"Temporary files Path: {self.temp_path}")
        logger.info(f"Plugin data Path: {self.data_path}")
        # 加载配置
        self.verified_config = self._verify_config(config)
        logger.debug(f"Original Config: {json.dumps(config, ensure_ascii=False, indent=4)}")
        logger.debug(f"Verified Config: {self.verified_config.model_dump_json(indent=4)}")
        # 加载渲染器
        self.renderer = Renderer(self.plugin_path, self.verified_config, self.temp_path, self.data_path)
        # 加载其他资源
        with open(self.plugin_path / "assets/splashes.txt", encoding="utf-8") as splashes_file:
            self.splashes = splashes_file.readlines()
        # fmt: on

    def _verify_config(self, user_config: AstrBotConfig):
        try:
            return PluginConfig.model_validate(user_config)
        except (ConfigException, ValidationError) as e:
            logger.warning(
                f"[{PluginErrorCode.CFG_VALIDATION_FAILED}] Plugin config validation failed."
            )
            logger.warning(f"{e}")
            logger.warning("Falling back to default config.")
            return PluginConfig()

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    @filter.command_group("jemss")
    def jemss(self):
        """JEMSS的相关指令"""
        pass

    @jemss.command("version")
    async def get_version(self, event: AstrMessageEvent):
        """获得JEMSS的版本"""
        user_name = event.get_sender_name()

        yield event.plain_result(
            f"你好 {user_name}\n"
            "欢迎使用 AstrBot plugin Just Enough McServer Status\n"
            f"Version: {self.__version__}\n"
            "License: AGPL-3.0 license https://www.gnu.org/licenses/agpl-3.0\n"
            "Repo: https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status\n"
        )

    @jemss.command("help")
    async def help(self, event: AstrMessageEvent):
        """JEMSS的有关帮助"""
        yield event.plain_result(
            "JEMSS 帮助信息\n"
            "```text\n"
            "├── /jeping —— 服务器状态查询\n"
            "│   └── status <服务器地址[:服务器端口]> [名称]\n"
            "│        └── 获取 Java 版状态信息\n"
            "\n"
            "└── /jemss —— 插件工具集\n"
            "    ├── version\n"
            "    │    └── 查看插件版本\n"
            "    ├── splash\n"
            "    │    └── 随机获取启动标语\n"
            "    ├── admin (仅管理员)\n"
            "    │    └── 管理员测试指令\n"
            "    └── help\n"
            "         └── 显示此帮助信息\n"
            "```\n"
            "示例：`/jeping status 127.0.0.1:25565 LocalServer`"
        )

    @jemss.command("splash")
    async def splash(self, event: AstrMessageEvent):
        """来抽一个spalsh吧"""
        splash_num = random.randint(1, len(self.splashes))
        random_splash = self.splashes[splash_num - 1].strip("\n")
        yield event.plain_result(f"{random_splash}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @jemss.command("admin")
    async def admin(self, event: AstrMessageEvent):
        """像admin一样回答"""
        user_name = event.get_sender_name()
        yield event.plain_result(f"WOW, {user_name} 管理员来了呢！")

    @filter.command_group("jeping")
    def jeping(self):
        """查询Minecraft服务器有关信息"""
        pass

    """
    TODO:什么时候把基岩版的查询加上
    """

    @jeping.command("status")
    async def get_status(
        self,
        event: AstrMessageEvent,
        server_address: str,
        server_name: str | None = None,
    ):
        """获取JE服务器状态 参数：/jeping status [服务器域名或ip地址与端口] [(选填)服务器名称]"""
        # 用户输入处理
        server_address = server_address.strip()

        # 服务器信息获取
        try:
            server = await JavaServer.async_lookup(server_address)
            server_status = await server.async_status()
        # TODO:更细致的异常反馈，但是由于mcstatus现在异常处理过于粗略，暂且搁置
        except gaierror as e:
            logger.error(
                f"[{PluginErrorCode.NET_DNS_RESOLUTION}] Cannot get address info: {e}"
            )
            yield event.plain_result(
                "无法解析服务器地址\n"
                "--------------------------\n"
                "可能的原因：\n"
                "- 服务器域名已过期或更改\n"
                "- 输入的地址格式不正确\n"
                "- 本地 DNS 解析服务异常\n"
                "- 网络连接不可用\n"
                "--------------------------\n"
                "请检查服务器地址是否正确，或稍后重试"
            )
            return
        except OSError as e:
            logger.error(f"[{PluginErrorCode.NET_UNEXPECTED}] {e}")
            yield event.plain_result(
                "无法连接到服务器\n"
                "--------------------------\n"
                "可能的原因：\n"
                "- 服务器未开启或正在重启\n"
                "- 端口号错误或未开放\n"
                "- 服务器已开启但被防火墙拦截\n"
                "- 该端口并非 Minecraft Java 版服务\n"
                "- 网络连接不稳定或超时\n\n"
                "--------------------------\n"
                "请稍后重试，或核对服务器地址与端口号是否正确"
            )
            return

        # 信息图片渲染
        if self.verified_config.general.is_info_card_enabled:
            info_pic = self.renderer.server_info_render(
                server, server_status, event, server_name
            )
            yield event.image_result(info_pic)

        # 消息输出信息图片和文字
        motd_text = server_status.motd.to_plain()
        display_name = server_name or server_address

        if self.verified_config.general.is_info_text_enabled:
            if self.verified_config.text_info.is_markdown_enabled:
                # HACK:此处为了排版用了零宽字符，对复制不友好，会引入看不见的字符，但目前认为想到解决办法
                yield event.plain_result(
                    f"## {display_name} \n\n"
                    "| 项目 | 状态 |\n"
                    "| :--- | :--- |\n"
                    f"| **服务器版本** | {server_status.version.name}（协议 {server_status.version.protocol}） |\n"
                    f"| **在线人数** | {server_status.players.online} / {server_status.players.max} |\n"
                    f"| **延迟** | {round(server_status.latency, 2)} ms |\n"
                    f"| **解析地址** | {server.address.host}:{server.address.port} |\n"
                    "### MOTD\n"
                    "```text \n"
                    f"\u200b{motd_text}\n"
                    "```"
                )
            else:
                yield event.plain_result(
                    f"🖥  {display_name}\n"
                    "═══════════════════════════\n"
                    f"📋  服务器版本：{server_status.version.name}（协议 {server_status.version.protocol}）\n"
                    f"👥  在线人数：{server_status.players.online} / {server_status.players.max}\n"
                    f"⚡  延   迟：{round(server_status.latency, 2)} ms\n"
                    f"🌐  解析地址：{server.address.host}:{server.address.port}\n"
                    f"💬  MOTD：\n{motd_text}\n"
                    "═══════════════════════════"
                )

            logger.info(server_status.motd.to_plain())

        if (
            not self.verified_config.general.is_info_card_enabled
            and not self.verified_config.general.is_info_text_enabled
        ):
            logger.warning(
                f"[{PluginErrorCode.CFG_EMPTY_OUTPUT}] Both info card generation and text output are disabled in the plugin configuration. As a result, the plugin will produce no visible output."
            )
            yield event.plain_result(
                "请检查插件配置，其中中信息卡片渲染与信息文字输出都被禁用，这会导致插件无法产生任何有用的输出。"
            )
            yield event.plain_result("如果你是不是管理员，请将以上文本发送给Bot管理员")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
