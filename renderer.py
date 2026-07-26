import base64
import io
import os
import random
from datetime import datetime
from pathlib import Path

from mcstatus import JavaServer
from mcstatus.motd.components import ParsedMotdComponent
from mcstatus.responses.bedrock import BedrockStatusResponse
from mcstatus.responses.java import JavaStatusResponse
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent

from .config import PluginConfig
from .exceptions import PluginErrorCode, SecurityException
from .motdinfo import JAVA_COLORS, JAVA_FORMATS, JavaFormatting, JavaMinecraftColor


class Renderer:
    """实现MOTD的渲染逻辑"""

    def __init__(
        self, plugin_path: Path, config: PluginConfig, temp_path: Path, data_path: Path
    ):
        # fmt: off
        self.config = config
        self.plugin_path = plugin_path
        self.temp_path = temp_path
        self.data_path = data_path
        # 加载字体资源
        self.font_title = ImageFont.truetype(
            plugin_path / "fonts/minecraft.ttf", size=50
        )
        self.font_motd_regular = ImageFont.truetype(
            plugin_path / "fonts/minecraft.ttf", size=40
        )
        self.font_motd_italic = ImageFont.truetype(
            plugin_path / "fonts/minecraft-italic.ttf", size=40
        )
        self.font_motd_bold = ImageFont.truetype(
            plugin_path / "fonts/minecraft-bold.ttf", size=40
        )
        self.font_motd_bold_italic = ImageFont.truetype(
            plugin_path / "fonts/minecraft-bold-italic.ttf", size=40
        )
        self.font_player = ImageFont.truetype(
            plugin_path / "fonts/minecraft.ttf", size=30
        )
        # 加载默认贴图
        self.default_background = Image.open(
            self.plugin_path / "assets/background_dark.png"
        )
        self.ping_icons = {
            "ping1": Image.open(plugin_path / "assets/ping_1.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
            "ping2": Image.open(plugin_path / "assets/ping_2.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
            "ping3": Image.open(plugin_path / "assets/ping_3.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
            "ping4": Image.open(plugin_path / "assets/ping_4.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
            "ping5": Image.open(plugin_path / "assets/ping_5.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
            "unreachable": Image.open(plugin_path / "assets/unreachable.png")
            .resize((40, 32), resample=0)
            .convert("RGBA"),
        }
        self.unknown_icon = (
            Image.open(plugin_path / "assets/unknown_server.png")
            .resize((128, 128))
            .convert("RGBA")
        )
        # fmt:on

    """
    TODO:渐变色一类的webcolor支持
    TODO:随机代码支持
    """

    def server_info_render(
        self,
        server: JavaServer,
        status: JavaStatusResponse,
        event: AstrMessageEvent,
        title: str | None,
    ) -> str:
        pic = Image.new("RGBA", (1248, 144))
        pic_drawer = ImageDraw.Draw(pic)

        # 设置背景
        self._set_background(pic)

        # 添加服务器标题
        if self.config.info_card.title.is_enabled:
            self._add_server_title(title, server, pic_drawer)

        # 添加服务器图标
        if self.config.info_card.icon.is_enabled:
            self._add_server_icon(status, pic)

        # 添加延迟显示
        if self.config.info_card.ping_indicator.is_enabled:
            self._add_ping_indicator(status, pic)

        # 添加在线人数显示
        if self.config.info_card.player_count.is_enabled:
            self._add_player_count(status, pic_drawer)

        # 解析motd
        if self.config.info_card.motd.is_enabled:
            motd = status.motd.parsed
            self._add_motd(motd, pic_drawer)

        # TODO:优化缓存
        # 设置缓存文件路径
        session_id = event.get_session_id()
        # 删除同对话的之前缓存
        old_files = self.temp_path.glob(f"JEMSSPlugin_temp_img_{session_id}*.png")
        for old_file in old_files:
            try:
                os.remove(old_file)
            except PermissionError:
                logger.warning(
                    f"[{PluginErrorCode.RND_TEMP_CLEAN}] No permission to access the file."
                )
        pic_temp_path = (
            self.temp_path
            / f"JEMSSPlugin_temp_img_{session_id}_{datetime.now().strftime('%y%m%d%H%M%S%f')}.png"
        )
        logger.info(f"Temp server info picture path: {pic_temp_path}")

        # 保存文件
        pic.save(pic_temp_path, "PNG")

        return str(pic_temp_path)

    # TODO:更加完善的自定义背景机制
    def _set_background(self, pic: Image.Image):
        if (
            self.config.info_card.background.is_custom_enabled
            and self.config.info_card.background.upload
        ):
            # 防止路径穿越
            # TODO:自动回退为默认与错误带代码和文档设置
            user_background_path = self.data_path.joinpath(
                random.choice(self.config.info_card.background.upload)
            ).resolve()
            try:
                if not user_background_path.is_relative_to(self.data_path.resolve()):
                    raise SecurityException(
                        PluginErrorCode.SEC_PATH_TRAVERSAL,
                        "Directory Traversal is blocked.",
                    )
                user_background = Image.open(user_background_path).resize((1248, 144))
                pic.paste(user_background, (0, 0))
            except FileNotFoundError:
                logger.warning(
                    f"[{PluginErrorCode.RND_BACKGROUND_LOAD}] Can not find the background file."
                )
                logger.warning("Now reverting to the default background.")
                pic.paste(self.default_background, (0, 0))
            except UnidentifiedImageError:
                logger.warning(
                    f"[{PluginErrorCode.RND_BACKGROUND_LOAD}] Can not open and identify the background file"
                )
                logger.warning("Now reverting to the default background.")
                pic.paste(self.default_background, (0, 0))
            except SecurityException as e:
                logger.error(f"[{e.code}] {e.message}")
                logger.error("Now reverting to the default background.")
                pic.paste(self.default_background, (0, 0))
        else:
            pic.paste(self.default_background, (0, 0))

    def _add_server_icon(self, status: JavaStatusResponse, pic: Image.Image):
        """添加服务器头像"""
        if status.icon and status.icon.startswith("data:image/png;base64,"):
            icon_data = base64.b64decode(status.icon.split(",")[1])
            icon = Image.open(io.BytesIO(icon_data), formats=["PNG"])
            icon_resized = icon.resize((128, 128)).convert("RGBA")
            pic.paste(icon_resized, (20, 8), mask=icon_resized)
        else:
            logger.warning("Can't parse the server icon")
            pic.paste(self.unknown_icon, (20, 8), mask=self.unknown_icon)

    def _add_server_title(
        self, title: str | None, server: JavaServer, pic_drawer: ImageDraw.ImageDraw
    ):
        """添加展示的标题"""
        if title:
            pic_drawer.text(
                (160, 8),
                f"{title}",
                font=self.font_title,
            )
        else:
            # 添加服务器地址
            pic_drawer.text(
                (160, 8),
                f"{server.address.host}:{server.address.port}",
                font=self.font_title,
            )

    def _add_ping_indicator(self, status: JavaStatusResponse, pic: Image.Image):
        """添加延迟图标"""
        if (
            status.latency
            <= self.config.info_card.ping_indicator.ping_thresholds.excellent
        ):
            pic.paste(
                self.ping_icons["ping5"], (1200, 10), mask=self.ping_icons["ping5"]
            )
        elif (
            status.latency <= self.config.info_card.ping_indicator.ping_thresholds.good
        ):
            pic.paste(
                self.ping_icons["ping4"], (1200, 10), mask=self.ping_icons["ping4"]
            )
        elif (
            status.latency
            <= self.config.info_card.ping_indicator.ping_thresholds.medium
        ):
            pic.paste(
                self.ping_icons["ping3"], (1200, 10), mask=self.ping_icons["ping3"]
            )
        elif status.latency <= self.config.info_card.ping_indicator.ping_thresholds.bad:
            pic.paste(
                self.ping_icons["ping2"], (1200, 10), mask=self.ping_icons["ping2"]
            )
        else:
            pic.paste(
                self.ping_icons["ping1"], (1200, 10), mask=self.ping_icons["ping1"]
            )

    def _add_player_count(
        self, status: JavaStatusResponse, pic_drawer: ImageDraw.ImageDraw
    ):
        """添加在线人数显示"""
        player_length = pic_drawer.textlength(
            f"{status.players.online}/{status.players.max}", font=self.font_player
        )
        pic_drawer.text(
            (1190 - player_length, 15),
            f"{status.players.online}/{status.players.max}",
            font=self.font_player,
            fill=(128, 128, 128),
        )

    def _add_motd(
        self, motd: list[ParsedMotdComponent], pic_drawer: ImageDraw.ImageDraw
    ):
        """格式化渲染状态机"""
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
        # 计算基本常量
        regular_motd_box = pic_drawer.textbbox((0, 0), "你好！Great, you have a Minecraft world.", current_font)
        regular_motd_line_height = regular_motd_box[3] - regular_motd_box[1]
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
                        current_y = current_y + regular_motd_line_height + self.config.info_card.motd.leading
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
