"""
Generate X/Twitter slide images — dark theme, mixed font rendering (English version)
With emoji support via pilmoji
"""
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
import os, unicodedata

# ── 配置 ──
W, H = 1200, 1500
OUT_DIR = "/mnt/shared-storage-user/renyiming/projects/gen/gene-bench/x_images/en"
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
    cp = ord(ch)
    if 0x4E00 <= cp <= 0x9FFF: return True
    if 0x3400 <= cp <= 0x4DBF: return True
    if 0x20000 <= cp <= 0x2A6DF: return True
    if 0x3000 <= cp <= 0x303F: return True
    if 0xFF00 <= cp <= 0xFFEF: return True
    if ch in '「」『』【】（）——…、。，：；！？～·《》""''': return True
    return False

# ── 混合字体文本渲染 ──
def mixed_text(draw, xy, text, fill, size, mono=False):
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

def emoji_at(img, x, y, em, size=32):
    """在指定位置绘制 emoji"""
    f = _get_font(FONT_LATIN, size)
    with Pilmoji(img) as pm:
        pm.text((int(x), int(y)), em, font=f, fill=WHITE)

# ══════════════════════════════════════════════════════
# Slide 1: Skill Docs
# ══════════════════════════════════════════════════════
def render_image_1():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    y = 48
    y = draw_header(d, y, "01", "Skill Docs: What Helps vs. Hurts",
                    "We tested expert docs paragraph by paragraph. Results are surprising.")
    y += 24

    # ── 有用 ──
    rrect(d, [48, y, 290, y + 34], fill=GREEN, r=8)
    mixed_text(d, (62, y + 5), "Useful Components", BG, 22)
    emoji_at(img, 300, y - 2, "✅", 28)
    y += 46

    good = [
        ("Code Examples (examples.md)", "+6.2%", "~200 tok", "Most valuable part", "💻"),
        ("Pitfalls Top 3 (truncated)", "+7.6%", "~120 tok", "Less is more", "⚠️"),
        ("Workflow First 3 Steps (truncated)", "+4.2%", "~80 tok", "First few steps suffice", "🔄"),
    ]
    for name, val, tok, note, em in good:
        rrect(d, [48, y, W-48, y+100], fill=BG_CARD, r=12)
        emoji_at(img, 72, y+8, em, 26)
        mixed_text(d, (108, y+12), name, WHITE, 26)
        mixed_text(d, (72, y+50), f"{tok}  ·  {note}", GRAY, 22)
        vw = mixed_len(val, 28, mono=True)
        mixed_text(d, (W-72-vw, y+32), val, GREEN, 28, mono=True)
        y += 116

    y += 16
    # ── 有害 ──
    rrect(d, [48, y, 320, y+34], fill=RED, r=8)
    mixed_text(d, (62, y+5), "Useless or Harmful", BG, 22)
    emoji_at(img, 330, y-2, "❌", 28)
    y += 46

    bad = [
        ("API Reference (api_notes.md)", "-0.4%", "~80 tok", "Model already knows the API", "📖"),
        ("Full Pitfalls (all 5 items)", "-1.3%", "~120 tok", "Info overload hurts", "😵"),
        ("Full SKILL.md", "=Gene", "~600 tok", "5x tokens, no better results", "🗑️"),
    ]
    for name, val, tok, note, em in bad:
        rrect(d, [48, y, W-48, y+100], fill=BG_CARD, r=12)
        emoji_at(img, 72, y+8, em, 26)
        mixed_text(d, (108, y+12), name, WHITE, 26)
        mixed_text(d, (72, y+50), f"{tok}  ·  {note}", GRAY, 22)
        vc = RED if val.startswith("-") else YELLOW
        vw = mixed_len(val, 28, mono=True)
        mixed_text(d, (W-72-vw, y+32), val, vc, 28, mono=True)
        y += 116

    y += 24
    # ── 结论 ──
    rrect(d, [48, y, W-48, y+140], fill=(30,50,40), r=12)
    d.rectangle([48, y, 54, y+140], fill=GREEN)
    emoji_at(img, 80, y+10, "💡", 28)
    mixed_text(d, (116, y+14), "Takeaway", GREEN, 28)
    mixed_text(d, (80, y+52), "- More docs != better. Top 3 items beat the full doc.", WHITE, 22)
    mixed_text(d, (80, y+82), "- Code examples are the most valuable part (+6.2%)", WHITE, 22)
    mixed_text(d, (80, y+112), "- Full doc 600tok = Gene 120tok. 5x tokens wasted.", WHITE, 22)
    y += 164

    # ── 条形图 ──
    emoji_at(img, 48, y-4, "📊", 24)
    mixed_text(d, (80, y), "Performance Comparison", CYAN, 24)
    y += 36
    bars = [
        ("Pitfalls Top 3 (trunc)", +7.6, GREEN),
        ("Code Examples", +6.2, GREEN),
        ("Workflow First 3", +4.2, GREEN),
        ("API Reference", -0.4, RED),
        ("Pitfalls Full Text", -1.3, RED),
    ]
    for label, val, color in bars:
        mixed_text(d, (48, y+2), label, GRAY, 20)
        bx, bw, bh = 340, 540, 22
        cx = bx + bw // 2
        rrect(d, [bx, y, bx+bw, y+bh], fill=(40,46,54), r=4)
        if val > 0:
            fw = int((bw/2) * val / 10.0)
            if fw > 4: rrect(d, [cx, y, cx+fw, y+bh], fill=color, r=4)
        else:
            fw = int((bw/2) * abs(val) / 10.0)
            if fw > 4: rrect(d, [cx-fw, y, cx, y+bh], fill=color, r=4)
        vt = f"{val:+.1f}%"
        mixed_text(d, (bx+bw+12, y), vt, color, 20, mono=True)
        y += 34

    watermark(d)
    img.save(os.path.join(OUT_DIR, "slide_01_skill_en.png"), quality=95)
    print("OK slide_01_en")

# ══════════════════════════════════════════════════════
# Slide 2: Format > Content
# ══════════════════════════════════════════════════════
def render_image_2():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    y = 48
    y = draw_header(d, y, "02", "Format Matters More Than Content",
                    "Same content, different format: from harmful to effective")
    y += 20

    # ── 核心对比 ──
    rrect(d, [48, y, W-48, y+230], fill=BG_CARD, r=16)
    mixed_text(d, (80, y+16), "Same Common Pitfalls, only format differs:", GRAY, 22)

    # 左：Markdown
    rrect(d, [72, y+56, 560, y+200], fill=(50,30,30), r=12)
    emoji_at(img, 96, y+64, "💀", 26)
    mixed_text(d, (130, y+68), "Markdown Original", RED, 26)
    mixed_text(d, (96, y+110), "-1.3%", RED, 48, mono=True)
    mixed_text(d, (96, y+168), "Harmful", RED, 22)

    # 右：XML
    rrect(d, [600, y+56, W-72, y+200], fill=(25,50,35), r=12)
    emoji_at(img, 624, y+64, "✨", 26)
    mixed_text(d, (658, y+68), "XML Tag Format", GREEN, 26)
    mixed_text(d, (624, y+110), "+9.4%", GREEN, 48, mono=True)
    mixed_text(d, (624, y+168), "Effective", GREEN, 22)

    mixed_text(d, (568, y+116), "→", CYAN, 32)
    y += 248

    # 差距强调
    rrect(d, [48, y, W-48, y+50], fill=(30,40,60), r=10)
    emoji_at(img, 200, y+8, "🤯", 28)
    gt = "10.7% gap  -  Only difference is format"
    gw = mixed_len(gt, 26)
    mixed_text(d, ((W-gw)/2 + 20, y+10), gt, CYAN, 26)
    y += 72

    # ── 更多发现 ──
    emoji_at(img, 48, y-4, "🔍", 28)
    mixed_text(d, (84, y), "More Surprising Findings", CYAN, 28)
    y += 44

    pairs = [
        ('"You are a coding newbie"', "+8.0%", GREEN, "👶",
         '"You are a domain expert"', "+0.9%", YELLOW, "🧑‍🔬"),
        ("Absurd warning (code gaining\nsentience)", "+5.0%", GREEN, "🤣",
         "Plausible-sounding\nfailure cases", "= 0%", RED, "😐"),
    ]
    for ll, lv, lc, lem, rl, rv, rc, rem in pairs:
        rrect(d, [48, y, 576, y+96], fill=BG_CARD, r=12)
        emoji_at(img, 72, y+6, lem, 24)
        mixed_text(d, (104, y+10), ll, WHITE, 22)
        mixed_text(d, (72, y+46), lv, lc, 28, mono=True)
        rrect(d, [600, y, W-48, y+96], fill=BG_CARD, r=12)
        emoji_at(img, 624, y+6, rem, 24)
        mixed_text(d, (656, y+10), rl, WHITE, 22)
        mixed_text(d, (624, y+46), rv, rc, 28, mono=True)
        y += 112

    y += 8
    # ── 框架排名 ──
    emoji_at(img, 48, y-4, "🏆", 28)
    mixed_text(d, (84, y), "Framing Style Rankings", CYAN, 28)
    y += 42

    fws = [
        ("WARNING Frame", "+10.5%", GREEN, '"Not doing X will cause failure"', "🚨"),
        ("Socratic Questioning", "+6.6%", GREEN, '"Have you considered..."', "🤔"),
        ("Suggestion", "+4.1%", GREEN, '"You might consider..."', "💬"),
        ("Command", "-0.1%", YELLOW, '"You must..."', "👊"),
        ("Teaching", "-6.9%", RED, '"The principle behind this is..."', "📚"),
    ]
    for name, val, color, desc, em in fws:
        rrect(d, [48, y, W-48, y+58], fill=BG_CARD, r=10)
        emoji_at(img, 72, y+10, em, 22)
        mixed_text(d, (102, y+14), name, WHITE, 22)
        mixed_text(d, (360, y+14), desc, GRAY, 20)
        vw = mixed_len(val, 24, mono=True)
        mixed_text(d, (W-72-vw, y+14), val, color, 24, mono=True)
        y += 68

    y += 16
    # ── 结论 ──
    rrect(d, [48, y, W-48, y+100], fill=(30,50,40), r=12)
    d.rectangle([48, y, 54, y+100], fill=GREEN)
    emoji_at(img, 80, y+10, "💡", 28)
    mixed_text(d, (116, y+14), "Takeaway", GREEN, 28)
    mixed_text(d, (80, y+50), "Models don't care if you're right. They care about tone & format.", ORANGE, 22)
    mixed_text(d, (80, y+78), "WARNING > Suggestion > Command > Teaching (Teaching hurts -6.9%)", WHITE, 20)

    watermark(d)
    img.save(os.path.join(OUT_DIR, "slide_02_format_en.png"), quality=95)
    print("OK slide_02_en")

# ══════════════════════════════════════════════════════
# Slide 3: Gene + EvoMap
# ══════════════════════════════════════════════════════
def render_image_3():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    y = 48
    y = draw_header(d, y, "03", "Where Do Pitfalls Go? Gene + EvoMap",
                    "Pitfall records are the strongest guidance. How to manage them?")
    y += 20

    # ── Gene 卡片 ──
    rrect(d, [48, y, W-48, y+280], fill=BG_CARD, r=16)
    rrect(d, [72, y+16, 210, y+48], fill=CYAN, r=8)
    emoji_at(img, 86, y+16, "🧬", 22)
    mixed_text(d, (114, y+20), "Gene", BG, 22)
    mixed_text(d, (224, y+20), "Strategy template distilled from docs  ~120 tok", GRAY, 22)

    cy = y + 62
    code = [
        ('{', GRAY), ('  "signals_match": ["peak","FWHM","wavelength"],', CYAN),
        ('  "summary": "Detect absorption peaks in UV-Vis",', GREEN),
        ('  "strategy": [', WHITE),
        ('    "Apply find_peaks with prominence detection",', WHITE),
        ('    "AVOID: Convert min-distance using spacing",', ORANGE),
        ('    "AVOID: peak_widths returns indices not nm"', ORANGE),
        ('  ]', WHITE), ('}', GRAY),
    ]
    for line, color in code:
        mixed_text(d, (96, cy), line, color, 20, mono=True)
        cy += 24
    y += 296

    # Gene 特性
    props = [
        ("Author doesn't matter", "Human = GPT = Claude authored, same effect", GREEN, "👤"),
        ("Minor errors are fine", "Only completely wrong algorithm hurts (-2.4%)", GREEN, "✏️"),
        ("Strong models: cross-domain reuse", "Weak models: generic Gene only", YELLOW, "🔀"),
    ]
    for title, desc, color, em in props:
        rrect(d, [48, y, W-48, y+58], fill=BG_CARD, r=10)
        emoji_at(img, 72, y+4, em, 22)
        mixed_text(d, (102, y+6), title, color, 22)
        mixed_text(d, (102, y+32), desc, GRAY, 20)
        y += 68

    y += 12
    # ── EvoMap 记忆回路 ──
    rrect(d, [48, y, W-48, y+210], fill=BG_CARD, r=16)
    rrect(d, [72, y+16, 320, y+48], fill=PURPLE, r=8)
    emoji_at(img, 86, y+16, "🧠", 22)
    mixed_text(d, (114, y+20), "EvoMap Memory", BG, 22)
    mixed_text(d, (334, y+20), "Structured pitfall storage  ~80 tok", GRAY, 22)

    my = y + 62
    mem = [
        ('<memory-failures>', PURPLE),
        ('  Common failure patterns:', WHITE),
        ('  - Forgot to convert distance from nm to indices', ORANGE),
        ('  - peak_widths returns indices, not wavelength', ORANGE),
        ('  - NaN values cause find_peaks to silently fail', ORANGE),
        ('</memory-failures>', PURPLE),
    ]
    for line, color in mem:
        mixed_text(d, (96, my), line, color, 20, mono=True)
        my += 24
    y += 228

    # ── 效果对比三列 ──
    emoji_at(img, 48, y-4, "📊", 28)
    mixed_text(d, (84, y), "Performance Comparison", CYAN, 28)
    y += 44

    cmp = [
        ("Full Docs", "600 tok", "= 0%", YELLOW, "Info overload", "📄"),
        ("Gene", "120 tok", "+8.3%", GREEN, "Distilled strategy", "🧬"),
        ("Memory Circuit", "80 tok", "+14.6%", (100,255,130), "Best overall", "🔥"),
    ]
    bw = (W - 96 - 48) // 3
    for i, (name, tok, val, color, note, em) in enumerate(cmp):
        bx = 48 + i * (bw + 24)
        bg_c = (30,50,40) if val.startswith("+") else (40,40,30)
        rrect(d, [bx, y, bx+bw, y+160], fill=bg_c, r=12)
        emoji_at(img, bx+(bw-30)//2, y+8, em, 26)
        nw = mixed_len(name, 22); mixed_text(d, (bx+(bw-nw)/2, y+38), name, WHITE, 22)
        tw = mixed_len(tok, 20); mixed_text(d, (bx+(bw-tw)/2, y+64), tok, GRAY, 20)
        vw = mixed_len(val, 36, mono=True); mixed_text(d, (bx+(bw-vw)/2, y+90), val, color, 36, mono=True)
        nw2 = mixed_len(note, 20); mixed_text(d, (bx+(bw-nw2)/2, y+132), note, GRAY, 20)
    y += 186

    # ── 结论 ──
    rrect(d, [48, y, W-48, y+80], fill=(30,30,50), r=12)
    d.rectangle([48, y, 54, y+80], fill=PURPLE)
    emoji_at(img, 80, y+8, "⚡", 26)
    mixed_text(d, (114, y+12), "Information density is king. More is toxic.", WHITE, 26)
    mixed_text(d, (80, y+48), "→ evomap.ai", PURPLE, 26)

    watermark(d)
    img.save(os.path.join(OUT_DIR, "slide_03_gene_evomap_en.png"), quality=95)
    print("OK slide_03_en")

# ══════════════════════════════════════════════════════
# Slide 4: Recipes + Pitfall Guide
# ══════════════════════════════════════════════════════
def render_image_4():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    y = 48
    y = draw_header(d, y, "04", "Practical Recipes + Pitfall Guide",
                    "Actionable advice distilled from 4,948 experiments")
    y += 16

    # ── 配方 ──
    emoji_at(img, 48, y-4, "🍳", 28)
    mixed_text(d, (84, y), "Recipes (pick any one)", CYAN, 28)
    y += 44

    recipes = [
        ("Have docs", "Extract Pitfalls top 2-3 -> convert to XML", "+9.4%", GREEN, "📄"),
        ("Have pitfall logs", "2 items + WARNING frame", "+14.6%", (100,255,130), "⚠️"),
        ("Have nothing", 'Just say "This code goes to production"', "+7.0%", GREEN, "🚀"),
    ]
    for sc, method, val, color, em in recipes:
        rrect(d, [48, y, W-48, y+90], fill=BG_CARD, r=12)
        sw = mixed_len(sc, 22)
        rrect(d, [72, y+12, 72+sw+20, y+42], fill=(40,55,70), r=8)
        mixed_text(d, (82, y+14), sc, CYAN, 22)
        emoji_at(img, 72+sw+28, y+10, em, 22)
        mixed_text(d, (72, y+56), method, WHITE, 22)
        vw = mixed_len(val, 28, mono=True)
        mixed_text(d, (W-72-vw, y+28), val, color, 28, mono=True)
        y += 104

    y += 16
    # ── 禁忌 ──
    rrect(d, [48, y, W-48, y+190], fill=(50,25,25), r=16)
    d.rectangle([48, y, 54, y+190], fill=RED)
    emoji_at(img, 80, y+12, "🚫", 28)
    mixed_text(d, (116, y+16), "Critical Rule: Don't Mix & Match!", RED, 28)
    mixed_text(d, (80, y+58), "Three good components stacked together", WHITE, 22)
    mixed_text(d, (80, y+88), "Expected +29%  ->  Actual +4.5% (only 15.6%)", ORANGE, 22)
    mixed_text(d, (80, y+126), "Reason: All components work by activating 'caution mode'", GRAY, 22)
    mixed_text(d, (80, y+156), "Caution mode is a binary switch -- one trigger is enough", GRAY, 22)
    y += 210

    # ── 强弱模型 ──
    mixed_text(d, (48, y), "Strong vs. Weak Models", CYAN, 28)
    y += 44

    hw = (W - 96 - 24) // 2
    # 强模型
    rrect(d, [48, y, 48+hw, y+190], fill=BG_CARD, r=12)
    rrect(d, [72, y+16, 230, y+46], fill=GREEN, r=8)
    emoji_at(img, 86, y+14, "💪", 22)
    mixed_text(d, (114, y+18), "Strong (Pro)", BG, 22)
    pro = [("1. Memory Circuit","+14.6%",GREEN),("2. Gene G3","+8.3%",GREEN),
           ("3. Rubber Duck","+16.6%",(100,255,130)),("4. No guidance","baseline",GRAY)]
    py = y + 56
    for l, v, c in pro:
        mixed_text(d, (80, py), l, WHITE, 20)
        mixed_text(d, (280, py), v, c, 20, mono=True)
        py += 32

    # 弱模型
    rx = 48 + hw + 24
    rrect(d, [rx, y, rx+hw, y+190], fill=BG_CARD, r=12)
    rrect(d, [rx+24, y+16, rx+200, y+46], fill=YELLOW, r=8)
    emoji_at(img, rx+38, y+14, "🐣", 22)
    mixed_text(d, (rx+66, y+18), "Weak (Flash)", BG, 22)
    flash = [("1. Memory Circuit","+27%",GREEN),("2. Generic Gene","+13%",GREEN),
             ("3. No guidance","baseline",GRAY),("4. Domain Gene","-20%",RED)]
    py = y + 56
    for l, v, c in flash:
        mixed_text(d, (rx+32, py), l, WHITE, 20)
        mixed_text(d, (rx+230, py), v, c, 20, mono=True)
        py += 32

    y += 208

    # ── 记忆来源 ──
    emoji_at(img, 48, y-4, "🔎", 28)
    mixed_text(d, (84, y), "Where Do Pitfall Records Come From?", CYAN, 28)
    y += 42
    srcs = [
        ("Human-curated", "+10.9%", GREEN, "Best but expensive", "👨‍💻"),
        ("Auto-extracted from docs", "+9.4%", GREEN, "Only 1.5% gap, can replace manual", "🤖"),
        ("Model self-prediction", "+4.2%", YELLOW, "Not reliable", "🎯"),
    ]
    for name, val, color, note, em in srcs:
        rrect(d, [48, y, W-48, y+58], fill=BG_CARD, r=10)
        emoji_at(img, 72, y+10, em, 22)
        mixed_text(d, (102, y+14), name, WHITE, 22)
        mixed_text(d, (420, y+14), note, GRAY, 20)
        vw = mixed_len(val, 24, mono=True)
        mixed_text(d, (W-72-vw, y+14), val, color, 24, mono=True)
        y += 68

    y += 12
    # ── 底部 ──
    rrect(d, [48, y, W-48, y+76], fill=(30,30,50), r=12)
    d.rectangle([48, y, 54, y+76], fill=CYAN)
    emoji_at(img, 80, y+6, "🔗", 22)
    mixed_text(d, (110, y+10), "Full data and code", CYAN, 22)
    mixed_text(d, (80, y+40), "github.com/qishisuren123/gene-bench  ·  evomap.ai", WHITE, 22, mono=True)

    watermark(d)
    img.save(os.path.join(OUT_DIR, "slide_04_recipes_en.png"), quality=95)
    print("OK slide_04_en")


if __name__ == "__main__":
    render_image_1()
    render_image_2()
    render_image_3()
    render_image_4()
    print(f"\nAll images saved to {OUT_DIR}/")
