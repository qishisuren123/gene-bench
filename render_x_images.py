"""
生成 X/Twitter 推文配图 — 深色主题、混合字体渲染
Lato-Bold 渲染英文/数字，DroidSansFallback 渲染中文/符号
"""
from PIL import Image, ImageDraw, ImageFont
import os, unicodedata

# ── 配置 ──
W, H = 1200, 1500
OUT_DIR = "/mnt/shared-storage-user/renyiming/projects/gen/gene-bench/x_images"
os.makedirs(OUT_DIR, exist_ok=True)

# 字体路径
FONT_CJK = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
FONT_LATIN = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"
FONT_LATIN_REG = "/usr/share/fonts/truetype/lato/Lato-Regular.ttf"
FONT_MONO_EN = "/usr/share/fonts/truetype/noto/NotoSansMono-Bold.ttf"

# 颜色
BG = (13, 17, 23)
BG_CARD = (22, 27, 34)
CYAN = (88, 166, 255)
GREEN = (63, 185, 80)
RED = (248, 81, 73)
YELLOW = (210, 153, 34)
WHITE = (230, 237, 243)
GRAY = (139, 148, 158)
ORANGE = (255, 166, 87)
PURPLE = (188, 140, 255)

# ── 字体缓存 ──
_font_cache = {}

def _get_font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]

def _is_cjk(ch):
    """判断字符是否需要 CJK 字体"""
    cp = ord(ch)
    # CJK 统一汉字
    if 0x4E00 <= cp <= 0x9FFF: return True
    if 0x3400 <= cp <= 0x4DBF: return True
    if 0x20000 <= cp <= 0x2A6DF: return True
    # CJK 标点
    if 0x3000 <= cp <= 0x303F: return True
    if 0xFF00 <= cp <= 0xFFEF: return True
    # 中文引号等
    if ch in '「」『』【】（）——…、。，：；！？～·《》""''': return True
    return False

# ── 混合字体文本渲染 ──
def mixed_text(draw, xy, text, fill, size, mono=False):
    """逐字符渲染，英文用 Lato/Mono，中文用 DroidSansFallback"""
    x, y = xy
    if mono:
        f_en = _get_font(FONT_MONO_EN, size)
    else:
        f_en = _get_font(FONT_LATIN, size)
    f_cn = _get_font(FONT_CJK, size)

    for ch in text:
        f = f_cn if _is_cjk(ch) else f_en
        draw.text((x, y), ch, fill=fill, font=f)
        bbox = f.getbbox(ch)
        if bbox:
            x += bbox[2] - bbox[0] + 1
        else:
            x += size // 2

def mixed_len(text, size, mono=False):
    """计算混合字体文本宽度"""
    if mono:
        f_en = _get_font(FONT_MONO_EN, size)
    else:
        f_en = _get_font(FONT_LATIN, size)
    f_cn = _get_font(FONT_CJK, size)
    w = 0
    for ch in text:
        f = f_cn if _is_cjk(ch) else f_en
        bbox = f.getbbox(ch)
        if bbox:
            w += bbox[2] - bbox[0] + 1
        else:
            w += size // 2
    return w

# ── 通用绘图工具 ──
def rrect(draw, xy, fill, r=16):
    draw.rounded_rectangle(xy, radius=r, fill=fill)

def draw_header(draw, y, num, title, subtitle=""):
    # 编号标签
    rrect(draw, [48, y, 108, y + 40], fill=CYAN, r=8)
    mixed_text(draw, (58, y + 6), num, BG, 26, mono=True)
    mixed_text(draw, (124, y + 2), title, WHITE, 36)
    draw.line([(48, y + 54), (W - 48, y + 54)], fill=(48, 54, 61), width=2)
    if subtitle:
        mixed_text(draw, (48, y + 66), subtitle, GRAY, 22)
        return y + 98
    return y + 68

def watermark(draw):
    t = "github.com/qishisuren123/gene-bench  |  evomap.ai"
    tw = mixed_len(t, 18, mono=True)
    mixed_text(draw, ((W - tw) / 2, H - 40), t, GRAY, 18, mono=True)

# ══════════════════════════════════════════════════════
# PLACEHOLDER_REST
