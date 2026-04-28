from PIL import Image, ImageDraw, ImageFont
import os

# ================= CANVAS =================
WIDTH, HEIGHT = 1080, 1920
BG_COLOR = (245, 245, 245)
CARD_COLOR = "white"
RED = (220, 0, 0)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (46, 204, 113)
DARK_GREEN = (30, 130, 76)

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(BASE_DIR, "assets", "fonts")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "File_To_Upload")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TITLE_FONT = ImageFont.truetype(
    os.path.join(FONT_DIR, "NotoSansDevanagari-Bold.ttf"), 90
)
QUESTION_FONT = ImageFont.truetype(
    os.path.join(FONT_DIR, "NotoSansDevanagari-Bold.ttf"), 76
)
OPTION_FONT = ImageFont.truetype(
    os.path.join(FONT_DIR, "NotoSansDevanagari-Regular.ttf"), 64
)

# ======================================================
# HINDI / DEVANAGARI SAFE TEXT WRAPPING
# ======================================================
def draw_wrapped_text(draw, text, font, x, y, max_width, line_spacing=12):
    """
    Unicode-safe wrapping for Hindi / Devanagari.
    Wraps by measuring rendered width, NOT by words.
    This preserves matras, ligatures, and quotes.
    """
    current_line = ""
    lines = []

    for char in text:
        test_line = current_line + char
        width = draw.textlength(test_line, font=font)

        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = char

    if current_line:
        lines.append(current_line)

    for line in lines:
        draw.text((x, y), line, fill=BLACK, font=font)
        y += font.size + line_spacing

    return y

# ======================================================
# MAIN IMAGE GENERATOR (2 IMAGES PER QUESTION)
# ======================================================
def generate_quiz_images(question, options, correct_answer, output_prefix):
    for mode in ["question", "answer"]:

        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # ---------- CARD ----------
        card_margin = 60
        card_radius = 40
        draw.rounded_rectangle(
            (
                card_margin,
                card_margin,
                WIDTH - card_margin,
                HEIGHT - card_margin
            ),
            radius=card_radius,
            fill=CARD_COLOR
        )

        # ---------- HEADER ----------
        header_height = 180
        draw.rounded_rectangle(
            (
                card_margin,
                card_margin,
                WIDTH - card_margin,
                card_margin + header_height
            ),
            radius=card_radius,
            fill=RED
        )

        draw.text(
            (WIDTH // 2, card_margin + header_height // 2),
            "GK Challenge",
            fill="white",
            font=TITLE_FONT,
            anchor="mm"
        )

        # ---------- QUESTION ----------
        x = card_margin + 60
        y = card_margin + header_height + 60
        max_width = WIDTH - (card_margin + 120)

        question_text = f"Q. {question}"

        y = draw_wrapped_text(
            draw,
            question_text,
            QUESTION_FONT,
            x,
            y,
            max_width
        )

        # ---------- DIVIDER ----------
        y += 30
        draw.line(
            (x, y, WIDTH - card_margin - 60, y),
            fill=GRAY,
            width=3
        )

        # ---------- OPTIONS ----------
        y += 50
        option_height = 110
        option_radius = 25

        for key, value in options.items():
            is_correct = (mode == "answer" and key == correct_answer)

            box_fill = GREEN if is_correct else None
            box_outline = DARK_GREEN if is_correct else GRAY

            draw.rounded_rectangle(
                (
                    x,
                    y,
                    WIDTH - card_margin - 60,
                    y + option_height
                ),
                radius=option_radius,
                fill=box_fill,
                outline=box_outline,
                width=4
            )

            draw.text(
                (x + 30, y + option_height // 2),
                f"{key}. {value}",
                fill=BLACK,
                font=OPTION_FONT,
                anchor="lm"
            )

            y += option_height + 30

        # ---------- SAVE ----------
        output_path = os.path.join(
            OUTPUT_DIR,
            f"{output_prefix}_{mode}.png"
        )

        img.save(output_path)
        print(f"✅ Image saved: {output_path}")