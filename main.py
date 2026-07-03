import random
from pathlib import Path

from mcstatus import JavaServer
from mcstatus.responses.bedrock import BedrockStatusResponse
from mcstatus.responses.java import JavaStatusResponse
from tomlkit import dump, exceptions, load

import astrbot.api.message_components as Comp
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api.star import Context, Star
from astrbot.core.utils import astrbot_path

from .renderer import Renderer
from .tools import JEMSSTool


class JEMSSPlugin(Star):
    __version__ = "v1.0.0"

    def __init__(self, context: Context):
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
        logger.info(f"JEMSSPlugin Path: {self.plugin_path}")
        logger.info(f"Temporary files Path: {self.temp_path}")
        # 加载配置
        self.config_path = self.plugin_path / "config.toml"
        self.config = self._load_config()
        # 加载渲染器
        self.renderer = Renderer(self.plugin_path, self.config, self.temp_path)
        # 加载其他资源
        with open(self.plugin_path / "assets/splashes.txt", encoding="utf-8") as splashes_file:
            self.splashes = splashes_file.readlines()
        # fmt: on

    def _load_config(self):
        default_config = {
            "ping_thresholds": {
                "excellent": 50,
                "good": 100,
                "medium": 200,
                "bad": 500,
            }
        }
        # 处理当文件不存在时的情况
        if not self.config_path.exists():
            logger.warning("Cannot get config file")
            logger.warning("Create a new config file")
            with open(self.config_path, mode="w", encoding="utf-8") as config_file:
                dump(default_config, config_file)
            return default_config
        # 捕获解析错误
        try:
            with open(self.config_path, mode="rb") as config_file:
                user_config = load(config_file)
            logger.info(f"{user_config}")
            verified_config = self._verify_config(default_config, user_config)
            return verified_config
        except exceptions.TOMLKitError:
            logger.warning("Config is broken!")
            logger.warning("Please check you config")
            return default_config

    """
    TODO:这里是硬编码判断，或许以后能优化一下
    """

    def _verify_config(self, base_config, user_config):
        verified_config = {}
        if "ping_thresholds" in user_config:
            verified_config["ping_thresholds"] = {}
            for item in base_config["ping_thresholds"]:
                if item in user_config["ping_thresholds"]:
                    if isinstance(
                        user_config["ping_thresholds"][item], int
                    ) or isinstance(user_config["ping_thresholds"][item], float):
                        verified_config["ping_thresholds"][item] = user_config[
                            "ping_thresholds"
                        ][item]
                    else:
                        logger.warning(
                            f"Config item ping_thresholds.{item} have wrong content: {user_config['ping_thresholds'][item]}"
                        )
                        logger.warning("Use default config to override this item")
                        verified_config["ping_thresholds"][item] = base_config[
                            "ping_thresholds"
                        ][item]
                else:
                    logger.warning(f"Config dose not have item: ping_thresholds.{item}")
                    logger.warning("Use default config to override this item")
                    verified_config["ping_thresholds"][item] = base_config[
                        "ping_thresholds"
                    ][item]
        else:
            logger.warning("Config dose not have item: ping_thresholds")
            logger.warning("Use default config to override this item")
            verified_config["ping_thresholds"] = base_config["ping_thresholds"]

        return verified_config

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    @filter.command_group("jemss")
    def jemss(self):
        """JEMMS的相关指令"""
        pass

    @jemss.command("version")
    async def get_version(self, event: AstrMessageEvent):
        """获得JEMSS的版本"""
        user_name = event.get_sender_name()
        message_chain = event.get_messages()
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, JEMSS的版本为{self.__version__}")

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
        yield event.plain_result(f"WOW,{user_name}管理员来了呢！")

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
        except Exception as e:
            logger.error(f"Can't get server information {server_address}")
            logger.error(f"Error info: {e}")
            yield event.plain_result(
                "无法获取服务器信息，请检查输入服务器是否正确或稍后重试"
            )
            return

        # 信息图片渲染
        info_pic = self.renderer.server_info_render(server, server_status, event, server_name)

        # 消息输出信息图片和文字
        message_chain = [
            Comp.Image.fromFileSystem(info_pic),  # 从本地文件目录发送图片
            Comp.Plain(
                f"• 服务器版本:{server_status.version.name}(协议版本:{server_status.version.protocol})\n"
                f"• 游玩人数:{server_status.players.online}/{server_status.players.max}\n"
                f"• 延迟:{server_status.latency}ms\n"
                f"• DNS(RSV)解析:{server.address.host}:{server.address.port}\n"
                f"• motd:\n"
                f"{server_status.motd.to_plain()}\n"
            ),
        ]
        yield event.chain_result(message_chain)

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
