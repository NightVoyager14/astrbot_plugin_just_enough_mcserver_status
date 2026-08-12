from enum import Enum


class BedrockInfoCardPalette(Enum):
    """Bedrock 版本的 InfoCard 颜色调色盘"""

    BORDER = (30, 30, 31)
    BACKGROUND = (36, 37, 38)
    TITLE = (255, 255, 255)
    TITLE_BACKGROUND = (72, 73, 74)
    CONTENT = (203, 204, 207)
    CONTENT_BACKGROUND = (49, 50, 51)
    LEFT_SHADOW = (74, 74, 75)
    RIGHT_SHADOW = (65, 66, 67)

    STATUS_BAR_CENTER = (60, 133, 39)
    STATUS_BAR_CORNER = (136, 180, 122)
    STATUS_BAR_TOP = (119, 170, 104)
    STATUS_BAR_BOTTOM = (84, 148, 65)
    STATUS_BAR_SHADOW = (42, 100, 28)


class BedrockInfoCardLayout(Enum):
    BORDER_BOX = [(5, 5), (1243, 139)]
    TITLE_BOX = [(7, 7), (1241, 55)]

    STATUS_BAR_TOP_BOX = [(7, 56), (1239, 57)]
    STATUS_BAR_LEFT_BOX = [(7, 58), (8, 61)]
    STATUS_BAR_CENTER_BOX = [(9, 58), (1239, 61)]
    STATUS_BAR_BOTTOM_BOX = [(9, 62), (1241, 63)]
    STATUS_BAR_RIGHT_BOX = [(1240, 58), (1241, 61)]
    STATUS_BAR_LEFT_CORNER_BOX = [(7, 62), (8, 63)]
    STATUS_BAR_RIGHT_CORNER_BOX = [(1240, 56), (1241, 57)]
    STATUS_BAR_SHADOW_BOX = [(7, 64), (1241, 65)]

    CONTENT_BOX = [(7, 66), (1241, 137)]
