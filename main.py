import base64
import io
import os
import random
from datetime import datetime
from pathlib import Path

from mcstatus import JavaServer
from mcstatus.responses.bedrock import BedrockStatusResponse
from mcstatus.responses.java import JavaStatusResponse
from PIL import Image, ImageDraw, ImageFont
from tomlkit import dump, exceptions, load

import astrbot.api.message_components as Comp
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api.star import Context, Star
from astrbot.core.utils import astrbot_path

from .motdinfo import JAVA_COLORS, JAVA_FORMATS, JavaFormatting, JavaMinecraftColor
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
        self.temp_path = Path(astrbot_path.get_astrbot_temp_path()) / "JEMSSPlugin_temp_pic"
        self.temp_path.mkdir(exist_ok=True)
        logger.info(f"JEMSSPlugin Path: {self.plugin_path}")
        logger.info(f"Temporary files Path: {self.temp_path}")
        # 加载配置
        self.config_path = self.plugin_path / "config.toml"
        self.config = self._load_config()
        # 加载字体资源
        self.font_title = ImageFont.truetype(
            self.plugin_path / "fonts/minecraft.ttf", size=50
        )
        self.font_motd_regular = ImageFont.truetype(
            self.plugin_path / "fonts/minecraft.ttf", size=40
        )
        self.font_motd_italic = ImageFont.truetype(
            self.plugin_path / "fonts/minecraft-italic.ttf", size=40
        )
        self.font_motd_bold = ImageFont.truetype(
            self.plugin_path / "fonts/minecraft-bold.ttf", size=40
        )
        self.font_motd_bold_italic = ImageFont.truetype(
            self.plugin_path / "fonts/minecraft-bold-italic.ttf", size=40
        )
        self.font_player = ImageFont.truetype(
            self.plugin_path / "fonts/minecraft.ttf", size=30
        )
        # 加载贴图
        self.ping_icons = {
            "ping1": Image.open(self.plugin_path / "assets/ping_1.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
            "ping2": Image.open(self.plugin_path / "assets/ping_2.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
            "ping3": Image.open(self.plugin_path / "assets/ping_3.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
            "ping4": Image.open(self.plugin_path / "assets/ping_4.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
            "ping5": Image.open(self.plugin_path / "assets/ping_5.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
            "unreachable": Image.open(self.plugin_path / "assets/unreachable.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
        }
        self.unknown_icon = (
            Image.open(self.plugin_path / "assets/unknown_server.png")
            .resize((128, 128))
            .convert("RGBA")
        )
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
        info_pic = self._server_info_render(server, server_status, event, server_name)

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

    """
    TODO:这里功能的实现太集中了，要分割成多个函数
    TODO:渐变色一类的webcolor支持
    TODO:随机代码支持
    """

    def _server_info_render(
        self,
        server: JavaServer,
        status: JavaStatusResponse,
        event: AstrMessageEvent,
        name: str | None,
    ) -> str:
        pic = Image.new("RGBA", (1248, 144))
        pic_drawer = ImageDraw.Draw(pic)

        # 设置背景
        background = Image.open(self.plugin_path / "assets/background_dark.png")
        pic.paste(background, (0, 0))

        # 添加服务器头像
        if status.icon and status.icon.startswith("data:image/png;base64,"):
            icon_data = base64.b64decode(status.icon.split(",")[1])
            icon = Image.open(io.BytesIO(icon_data), formats=["PNG"])
            icon_resized = icon.resize((128, 128)).convert("RGBA")
            pic.paste(icon_resized, (20, 8), mask=icon_resized)
        else:
            logger.warning("Can't parse the server icon")
            pic.paste(self.unknown_icon, (20, 8), mask=self.unknown_icon)

        if name:
            pic_drawer.text(
                (160, 8),
                f"{name}",
                font=self.font_title,
            )
        else:
            # 添加服务器地址
            pic_drawer.text(
                (160, 8),
                f"{server.address.host}:{server.address.port}",
                font=self.font_title,
            )

        # 添加延迟显示
        if status.latency <= self.config["ping_thresholds"]["excellent"]:
            pic.paste(
                self.ping_icons["ping5"], (1200, 10), mask=self.ping_icons["ping5"]
            )
        elif status.latency <= self.config["ping_thresholds"]["good"]:
            pic.paste(
                self.ping_icons["ping4"], (1200, 10), mask=self.ping_icons["ping4"]
            )
        elif status.latency <= self.config["ping_thresholds"]["medium"]:
            pic.paste(
                self.ping_icons["ping3"], (1200, 10), mask=self.ping_icons["ping3"]
            )
        elif status.latency <= self.config["ping_thresholds"]["bad"]:
            pic.paste(
                self.ping_icons["ping2"], (1200, 10), mask=self.ping_icons["ping2"]
            )
        elif status.latency > self.config["ping_thresholds"]["bad"]:
            pic.paste(
                self.ping_icons["ping1"], (1200, 10), mask=self.ping_icons["ping1"]
            )

        # 添加在线人数显示
        player_length = pic_drawer.textlength(
            f"{status.players.online}/{status.players.max}", font=self.font_player
        )
        pic_drawer.text(
            (1190 - player_length, 15),
            f"{status.players.online}/{status.players.max}",
            font=self.font_player,
            fill=(128, 128, 128),
        )

        # 解析motd
        motd = status.motd.parsed

        # 设置状态机的状态
        initial_position = (160, 60)
        current_x, current_y = initial_position
        current_length = 0
        current_color = JAVA_COLORS[JavaMinecraftColor.WHITE]["rgb"]
        current_bold = False
        current_italic = False
        current_strikethrough = False
        current_underlined = False
        current_obfuscated = False
        current_font = self.font_motd_regular
        # 开始渲染
        for component in motd:
            logger.debug(f"{component} | {isinstance(component, str)}")
            if isinstance(component, str):
                current_font = self._get_motd_font(current_bold, current_italic)
                # 处理有换行符的情况
                if "\n" in component:
                    component_multiline = component.split("\n")
                    for line_num in range(len(component_multiline)):
                        pic_drawer.text(
                            (current_x, current_y),
                            component_multiline[line_num],
                            current_color,
                            current_font,
                        )
                        self._set_motd_line(
                            pic_drawer,
                            (current_x, current_y),
                            current_font,
                            component_multiline[line_num],
                            current_underlined,
                            current_strikethrough,
                            current_color,
                        )
                        # 最后一位中断换行，正常向后渲染
                        if line_num == (len(component_multiline) - 1):
                            # 计算当前渲染部分的长度
                            current_length = pic_drawer.textlength(
                                component_multiline[line_num], current_font
                            )
                            current_x += current_length
                            continue
                        current_y = current_y + 30
                        current_x = initial_position[0]
                else:
                    pic_drawer.text(
                        (current_x, current_y), component, current_color, current_font
                    )
                    self._set_motd_line(
                        pic_drawer,
                        (current_x, current_y),
                        current_font,
                        component,
                        current_underlined,
                        current_strikethrough,
                        current_color,
                    )
                    # 计算当前渲染部分的长度
                    current_length = pic_drawer.textlength(component, current_font)
                    current_x += current_length
            # 处理颜色符号
            elif isinstance(component, JavaMinecraftColor):
                current_color = JAVA_COLORS[component]["rgb"]
                # JE特性：格式代码仅仅在颜色代码前生效
                current_bold = False
                current_italic = False
                current_strikethrough = False
                current_underlined = False
                current_obfuscated = False
            # 处理格式符号
            elif isinstance(component, JavaFormatting):
                if component == JavaFormatting.BOLD:
                    current_bold = True
                elif component == JavaFormatting.ITALIC:
                    current_italic = True
                elif component == JavaFormatting.UNDERLINED:
                    current_underlined = True
                elif component == JavaFormatting.STRIKETHROUGH:
                    current_strikethrough = True
                elif component == JavaFormatting.RESET:
                    current_color = JAVA_COLORS[JavaMinecraftColor.WHITE]["rgb"]
                    current_bold = False
                    current_italic = False
                    current_strikethrough = False
                    current_underlined = False
                    current_obfuscated = False

        # TODO:优化缓存
        # 设置缓存文件路径
        session_id = event.get_session_id()
        # 删除同对话的之前缓存
        old_files = self.temp_path.glob(f"JEMSSPlugin_temp_img_{session_id}*.png")
        for old_file in old_files:
            try:
                os.remove(old_file)
            except Exception as e:
                logger.warning(f"Cannot remove tempfile: {old_file}")
                logger.warning(f"Reason: {e}")
                logger.warning("You can delete it by yourself.")
        logger.info(datetime.now())
        pic_temp_path = (
            self.temp_path
            / f"JEMSSPlugin_temp_img_{session_id}_{datetime.now().strftime('%y%m%d%H%M%S%f')}.png"
        )
        logger.info(f"Temp server info picture path: {pic_temp_path}")

        # 保存文件
        pic.save(pic_temp_path, "PNG")

        return str(pic_temp_path)

    def _get_motd_font(self, bold_status: bool, italic_status: bool):
        """获取italic与bold对应的字体"""
        if bold_status and not italic_status:
            return self.font_motd_bold
        elif not bold_status and italic_status:
            return self.font_motd_italic
        elif bold_status and italic_status:
            return self.font_motd_bold_italic
        else:
            return self.font_motd_regular

    def _set_motd_line(
        self,
        pic_drawer: ImageDraw.ImageDraw,
        position: tuple,
        font: ImageFont.FreeTypeFont,
        component: str,
        underlined_status: bool,
        strikethrough_status: bool,
        color: tuple[int, int, int],
    ):
        """实现下划线与删除线的渲染"""
        box = pic_drawer.textbbox(position, component, font)
        ascent, descent = font.getmetrics()
        baseline = position[1] + ascent

        line_width = 3
        if underlined_status:
            # 此处将下划线定位于基线处
            underline_y = baseline
            underline_position = [(box[0], underline_y), (box[2], underline_y)]
            pic_drawer.line(underline_position, color, line_width)
        if strikethrough_status:
            # 此处将删除线定位于Ascent * 0.4处
            strikethrough_y = baseline - ascent * 0.4
            strikethrough_position = [
                (box[0], strikethrough_y),
                (box[2], strikethrough_y),
            ]
            pic_drawer.line(strikethrough_position, color, line_width)

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
