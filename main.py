import base64
import hashlib
import io
from datetime import datetime
from pathlib import Path

from mcstatus import JavaServer
from PIL import Image, ImageDraw, ImageFont

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api.star import Context, Star
from astrbot.core.utils import astrbot_path


class JEMSSPlugin(Star):
    # 存储渲染所需的颜色代码和格式代码
    color_codes = {
        "§0": {
            "name_en": "black",
            "hex": "#000000",
            "dark_hex": "#000000",
            "rgb": [0, 0, 0],
            "dark_rgb": [0, 0, 0],
            "ansi": "\x1b[0;30m",
            "bedrock": True,
            "java": True,
        },
        "§1": {
            "name_en": "dark_blue",
            "hex": "#0000AA",
            "dark_hex": "#00002A",
            "rgb": [0, 0, 170],
            "dark_rgb": [0, 0, 42],
            "ansi": "\x1b[0;34m",
            "bedrock": True,
            "java": True,
        },
        "§2": {
            "name_en": "dark_green",
            "hex": "#00AA00",
            "dark_hex": "#002A00",
            "rgb": [0, 170, 0],
            "dark_rgb": [0, 42, 0],
            "ansi": "\x1b[0;32m",
            "bedrock": True,
            "java": True,
        },
        "§3": {
            "name_en": "dark_aqua",
            "hex": "#00AAAA",
            "dark_hex": "#002A2A",
            "rgb": [0, 170, 170],
            "dark_rgb": [0, 42, 42],
            "ansi": "\x1b[0;36m",
            "bedrock": True,
            "java": True,
        },
        "§4": {
            "name_en": "dark_red",
            "hex": "#AA0000",
            "dark_hex": "#2A0000",
            "rgb": [170, 0, 0],
            "dark_rgb": [42, 0, 0],
            "ansi": "\x1b[0;31m",
            "bedrock": True,
            "java": True,
        },
        "§5": {
            "name_en": "dark_purple",
            "hex": "#AA00AA",
            "dark_hex": "#2A002A",
            "rgb": [170, 0, 170],
            "dark_rgb": [42, 0, 42],
            "ansi": "\x1b[0;35m",
            "bedrock": True,
            "java": True,
        },
        "§6": {
            "name_en": "gold",
            "hex": "#FFAA00",
            "dark_hex": "#402A00",
            "rgb": [255, 170, 0],
            "dark_rgb": [64, 42, 0],
            "ansi": "\x1b[0;33m",
            "bedrock": True,
            "java": True,
        },
        "§7": {
            "name_en": "gray",
            "hex": "#AAAAAA",
            "dark_hex": "#2A2A2A",
            "rgb": [170, 170, 170],
            "dark_rgb": [42, 42, 42],
            "ansi": "\x1b[0;37m",
            "bedrock": True,
            "java": True,
        },
        "§8": {
            "name_en": "dark_gray",
            "hex": "#555555",
            "dark_hex": "#151515",
            "rgb": [85, 85, 85],
            "dark_rgb": [21, 21, 21],
            "ansi": "\x1b[0;90m",
            "bedrock": True,
            "java": True,
        },
        "§9": {
            "name_en": "blue",
            "hex": "#5555FF",
            "dark_hex": "#15153F",
            "rgb": [85, 85, 255],
            "dark_rgb": [21, 21, 63],
            "ansi": "\x1b[0;94m",
            "bedrock": True,
            "java": True,
        },
        "§a": {
            "name_en": "green",
            "hex": "#55FF55",
            "dark_hex": "#153F15",
            "rgb": [85, 255, 85],
            "dark_rgb": [21, 63, 21],
            "ansi": "\x1b[0;92m",
            "bedrock": True,
            "java": True,
        },
        "§b": {
            "name_en": "aqua",
            "hex": "#55FFFF",
            "dark_hex": "#153F3F",
            "rgb": [85, 255, 255],
            "dark_rgb": [21, 63, 63],
            "ansi": "\x1b[0;96m",
            "bedrock": True,
            "java": True,
        },
        "§c": {
            "name_en": "red",
            "hex": "#FF5555",
            "dark_hex": "#3F1515",
            "rgb": [255, 85, 85],
            "dark_rgb": [63, 21, 21],
            "ansi": "\x1b[0;91m",
            "bedrock": True,
            "java": True,
        },
        "§d": {
            "name_en": "light_purple",
            "hex": "#FF55FF",
            "dark_hex": "#3F153F",
            "rgb": [255, 85, 255],
            "dark_rgb": [63, 21, 63],
            "ansi": "\x1b[0;95m",
            "bedrock": True,
            "java": True,
        },
        "§e": {
            "name_en": "yellow",
            "hex": "#FFFF55",
            "dark_hex": "#3F3F15",
            "rgb": [255, 255, 85],
            "dark_rgb": [63, 63, 21],
            "ansi": "\x1b[0;93m",
            "bedrock": True,
            "java": True,
        },
        "§f": {
            "name_en": "white",
            "hex": "#FFFFFF",
            "dark_hex": "#3F3F3F",
            "rgb": [255, 255, 255],
            "dark_rgb": [63, 63, 63],
            "ansi": "\x1b[0;97m",
            "bedrock": True,
            "java": True,
        },
        "§g": {
            "name_en": "minecoin_gold",
            "hex": "#DDD605",
            "dark_hex": "#373501",
            "rgb": [221, 214, 5],
            "dark_rgb": [55, 53, 1],
            "ansi": "\x1b[0;38;2;221;214;5m",
            "bedrock": True,
            "java": False,
        },
        "§h": {
            "name_en": "material_quartz",
            "hex": "#E3D4D1",
            "dark_hex": "#383534",
            "rgb": [227, 212, 209],
            "dark_rgb": [56, 53, 52],
            "ansi": "\x1b[0;38;2;227;212;209m",
            "bedrock": True,
            "java": False,
        },
        "§i": {
            "name_en": "material_iron",
            "hex": "#CECACA",
            "dark_hex": "#333232",
            "rgb": [206, 202, 202],
            "dark_rgb": [51, 50, 50],
            "ansi": "\x1b[0;38;2;206;202;202m",
            "bedrock": True,
            "java": False,
        },
        "§j": {
            "name_en": "material_netherite",
            "hex": "#443A3B",
            "dark_hex": "#110E0E",
            "rgb": [68, 58, 59],
            "dark_rgb": [17, 14, 14],
            "ansi": "\x1b[0;38;2;68;58;59m",
            "bedrock": True,
            "java": False,
        },
        "§m": {
            "name_en": "material_redstone",
            "hex": "#971607",
            "dark_hex": "#250501",
            "rgb": [151, 22, 7],
            "dark_rgb": [37, 5, 1],
            "ansi": "\x1b[0;38;2;151;22;7m",
            "bedrock": True,
            "java": False,
        },
        "§n": {
            "name_en": "material_copper",
            "hex": "#B4684D",
            "dark_hex": "#2D1A13",
            "rgb": [180, 104, 77],
            "dark_rgb": [45, 26, 19],
            "ansi": "\x1b[0;38;2;180;104;77m",
            "bedrock": True,
            "java": False,
        },
        "§p": {
            "name_en": "material_gold",
            "hex": "#DEB12D",
            "dark_hex": "#372C0B",
            "rgb": [222, 177, 45],
            "dark_rgb": [55, 44, 11],
            "ansi": "\x1b[0;38;2;222;177;45m",
            "bedrock": True,
            "java": False,
        },
        "§q": {
            "name_en": "material_emerald",
            "hex": "#11A036",
            "dark_hex": "#04280D",
            "rgb": [17, 160, 54],
            "dark_rgb": [4, 40, 13],
            "ansi": "\x1b[0;38;2;17;160;54m",
            "bedrock": True,
            "java": False,
        },
        "§s": {
            "name_en": "material_diamond",
            "hex": "#2CBAA8",
            "dark_hex": "#0B2E2A",
            "rgb": [44, 186, 168],
            "dark_rgb": [11, 46, 42],
            "ansi": "\x1b[0;38;2;44;186;168m",
            "bedrock": True,
            "java": False,
        },
        "§t": {
            "name_en": "material_lapis",
            "hex": "#21497B",
            "dark_hex": "#08121E",
            "rgb": [33, 73, 123],
            "dark_rgb": [8, 18, 30],
            "ansi": "\x1b[0;38;2;33;73;123m",
            "bedrock": True,
            "java": False,
        },
        "§u": {
            "name_en": "material_amethyst",
            "hex": "#9A5CC6",
            "dark_hex": "#261731",
            "rgb": [154, 92, 198],
            "dark_rgb": [38, 23, 49],
            "ansi": "\x1b[0;38;2;154;92;198m",
            "bedrock": True,
            "java": False,
        },
        "§v": {
            "name_en": "material_resin",
            "hex": "#EB7114",
            "dark_hex": "#3B1D05",
            "rgb": [235, 114, 20],
            "dark_rgb": [59, 29, 5],
            "ansi": "\x1b[0;38;2;235;114;20m",
            "bedrock": True,
            "java": False,
        },
        "§w": {
            "name_en": "party_blue_color",
            "hex": "#8CB3FF",
            "dark_hex": "#232D40",
            "rgb": [140, 179, 255],
            "dark_rgb": [35, 45, 64],
            "ansi": "\x1b[0;38;2;140;179;255m",
            "bedrock": True,
            "java": False,
        },
    }
    format_codes = {
        "§k": {
            "name_en": "obfuscated",
            "ansi": "\x1b[8m",
            "bedrock": True,
            "java": True,
        },
        "§l": {"name_en": "bold", "ansi": "\x1b[1m", "bedrock": True, "java": True},
        "§m": {
            "name_en": "strikethrough",
            "ansi": "\x1b[9m",
            "bedrock": False,
            "java": True,
        },
        "§n": {
            "name_en": "underlined",
            "ansi": "\x1b[4m",
            "bedrock": False,
            "java": True,
        },
        "§o": {"name_en": "italic", "ansi": "\x1b[3m", "bedrock": True, "java": True},
        "§r": {"name_en": "reset", "ansi": "\x1b[0m", "bedrock": True, "java": True},
    }
    plugin_path = (
        Path(astrbot_path.get_astrbot_plugin_path())
        / "astrbot_plugin_just_enough_mcserver_status"
    )
    temp_path = Path(astrbot_path.get_astrbot_temp_path())
    image_font = ImageFont.truetype(plugin_path / "fonts/unifont-17.0.03.otf", size=50)
    logger.info(plugin_path / "fonts/unifont-17.0.03.otf")

    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("version")
    async def get_version(self, event: AstrMessageEvent):
        """获得JEMSS的版本"""  # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str  # 用户发的纯文本消息字符串
        message_chain = (
            event.get_messages()
        )  # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(
            f"Hello, {user_name}, 你发了 {message_str}, JEMS的版本为v1.0.0"
        )  # 发送一条纯文本消息

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("admin")
    async def admin_respon(self, event: AstrMessageEvent):
        """像admin一样回答"""
        user_name = event.get_sender_name()
        message_chain = event.get_messages()
        logger.info(message_chain)
        yield event.plain_result(f"wow,{user_name}管理员来了呢！")

    @filter.command_group("mc")
    async def mc():
        """查询服务有关信息"""
        pass

    @mc.command("status")
    async def get_status(
        self, event: AstrMessageEvent, server_host: str, server_port: int | None = None
    ):
        """获取JE服务器状态 参数：/mc status [服务器域名或ip地址] [(选填)服务器端口]"""
        # 用户输入处理
        server_host = server_host.strip()

        # 地址与端口号拼接
        if server_port is not None:
            server_address = f"{server_host}:{str(server_port)}"
        else:
            server_address = server_host
        logger.debug(f"Address after processed: {server_address}")

        # 服务器信息获取
        server = await JavaServer.async_lookup(server_address)
        server_status = await server.async_status()

        # 信息图片渲染
        info_pic = self._server_info_render(server, server_status, event)

        # 消息输出信息图片和文字
        yield event.image_result(info_pic)
        yield event.plain_result(
            f"服务器版本:{server_status.version}游玩人数:{server_status.players.online}/{server_status.players.max},延迟:{server_status.latency}ms,DNS:{server.address.host}:{server.address.port},motd:{server_status.motd.to_plain()}"
        )

    def _server_info_render(self, server, status, event):
        pic = Image.new("RGB", (1248, 144))

        # 设置背景
        background = Image.open(JEMSSPlugin.plugin_path / "assets/background_dark.png")
        pic.paste(background, pic.getbbox())

        # 添加服务器头像
        icon_data = base64.b64decode(status.icon.split(",")[1])
        icon = Image.open(io.BytesIO(icon_data), formats=["PNG"])
        icon_resized = icon.resize((128, 128)).convert("RGBA")
        pic.paste(icon_resized, (20, 8, 148, 136), mask=icon_resized)

        # 添加服务器地址
        pic_draw = ImageDraw.Draw(pic)
        pic_draw.text(
            (160, 8),
            f"{server.address.host}:{server.address.port}",
            font=JEMSSPlugin.image_font,
        )

        # 设置缓存文件路径
        pic_hash = hashlib.md5(pic.tobytes())
        logger.info(pic_hash.hexdigest()[:5])
        logger.info(datetime.now())
        pic_temp_path = (
            self.temp_path
            / f"JEMSSPlugin_temp_img_{datetime.now().strftime('%y%m%d%H%M%S')}_{event.get_session_id()}_{pic_hash.hexdigest()}.jpg"
        )
        logger.info(pic_temp_path)

        # 保存文件
        pic.save(pic_temp_path, "JPEG", quality=95)

        return str(pic_temp_path)

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
