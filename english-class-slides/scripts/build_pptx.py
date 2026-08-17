#!/usr/bin/env python3
"""
build_pptx.py - Generic Automated Google-Slides-compatible PowerPoint assembly pipeline.
Part of the english-class-slides (v1.2) skill package.
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.dml.color import RGBColor
except ImportError:
    print("Error: python-pptx is not installed. Please run: pip install python-pptx")
    sys.exit(1)

SLIDE_WIDTH = Inches(13.333333)
SLIDE_HEIGHT = Inches(7.5)

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return RGBColor(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

def parse_slides_txt(filepath):
    content = Path(filepath).read_text(encoding="utf-8")
    splits = re.split(r"(?:SLIDE|DIAPOSITIVA|スライド)\s+(\d+)", content)
    slides = []
    for i in range(1, len(splits), 2):
        s_num = int(splits[i])
        s_text = splits[i+1].strip()
        slides.append((s_num, s_text))
    return slides

def parse_cover(raw):
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    data = {"title": "", "subtitle": "", "author": "", "ai_production": "", "credits": []}
    mode = None
    for l in lines:
        if re.match(r"^(?:Design|Diseño|デザイン):", l, re.I): continue
        elif re.match(r"^(?:Title|Título|タイトル):", l, re.I):
            data["title"] = re.sub(r"^(?:Title|Título|タイトル):\s*", "", l, flags=re.I).strip()
            mode = None
        elif re.match(r"^(?:Subtitle|Subtítulo|サブタイトル):", l, re.I):
            data["subtitle"] = re.sub(r"^(?:Subtitle|Subtítulo|サブタイトル):\s*", "", l, flags=re.I).strip()
            mode = None
        elif re.match(r"^(?:Author|Autor|著者):", l, re.I):
            data["author"] = re.sub(r"^(?:Author|Autor|著者):\s*", "", l, flags=re.I).strip()
            mode = None
        elif re.match(r"^(?:AI-Assisted Production|Producción asistida por IA|AI支援制作):", l, re.I):
            data["ai_production"] = re.sub(r"^(?:AI-Assisted Production|Producción asistida por IA|AI支援制作):\s*", "", l, flags=re.I).strip()
            mode = None
        elif re.match(r"^(?:Credits|Créditos|クレジット):", l, re.I):
            mode = "credits"
        elif mode == "credits":
            data["credits"].append(l)
    return data

def parse_content(raw):
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    for l in lines:
        if re.match(r"^(?:Design|Diseño|デザイン):", l, re.I): continue
        m = re.match(r"^(?:Text|Texto|本文):\s*(.*)", l, re.I)
        if m: return m.group(1).strip()
        elif not any(l.startswith(k) for k in ["SLIDE", "DIAPOSITIVA", "スライド"]):
            return l
    return ""

def parse_vocab(raw):
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    title = ""
    words = []
    for l in lines:
        if re.match(r"^(?:Title|Título|タイトル):", l, re.I):
            title = re.sub(r"^(?:Title|Título|タイトル):\s*", "", l, flags=re.I).strip()
        elif re.match(r"^\d+\.\s*", l):
            words.append(l)
    return title, words

def resolve_bg(slide_num, mapping, images_dir):
    for key, filename in mapping.items():
        if "-" in key:
            start, end = map(int, key.split("-"))
            if start <= slide_num <= end:
                return str(Path(images_dir) / filename)
        else:
            if int(key) == slide_num:
                return str(Path(images_dir) / filename)
    return ""

def get_layout_override(slide_num, overrides):
    for key, val in overrides.items():
        if "-" in key:
            start, end = map(int, key.split("-"))
            if start <= slide_num <= end:
                return val
        else:
            if int(key) == slide_num:
                return val
    return None

def build_presentation(config, lang_code, out_path=None):
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]

    if lang_code in ["en", "es"]:
        FONT_TITLE = "Cormorant Garamond"
        FONT_BODY = "Nunito Sans"
        FONT_NUM = config.get("slide_numbering", {}).get("font_name_" + lang_code, "Nunito Sans")
    else:
        FONT_TITLE = "Noto Serif JP"
        FONT_BODY = "Noto Sans JP"
        FONT_NUM = config.get("slide_numbering", {}).get("font_name_ja", "Noto Sans JP")

    COLOR_TITLE = hex_to_rgb("102238")
    COLOR_BODY = hex_to_rgb("1A2433")
    COLOR_SUBTITLE = hex_to_rgb("2C3E50")
    COLOR_CREDITS = hex_to_rgb("556270")

    images_dir = config["paths"].get("images_dir", "output/images")
    mapping = config.get("background_mapping", {})
    overrides = config.get("layout_overrides", {})
    num_cfg = config.get("slide_numbering", {})
    num_enabled = num_cfg.get("enabled", True)

    input_key = f"content_{lang_code}"
    input_file = Path(config["paths"].get(input_key, f"output/slides_content_{lang_code}.txt"))
    slides_data = parse_slides_txt(input_file)

    for slide_num, raw_text in slides_data:
        slide = prs.slides.add_slide(blank_layout)
        bg_path = resolve_bg(slide_num, mapping, images_dir)
        if os.path.exists(bg_path):
            slide.shapes.add_picture(os.path.abspath(bg_path), 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)

        if slide_num == 1:
            # Cover Slide
            cd = parse_cover(raw_text)
            tb_main = slide.shapes.add_textbox(Inches(0.223), Inches(1.098), Inches(5.038), Inches(3.545))
            tf_main = tb_main.text_frame
            tf_main.word_wrap = True
            tf_main.margin_left = Inches(0.1)
            tf_main.margin_top = Inches(0.05)

            p_title = tf_main.paragraphs[0]
            p_title.text = cd["title"]
            p_title.font.name = FONT_TITLE
            p_title.font.size = Pt(36 if lang_code == "ja" else 38)
            p_title.font.bold = True
            p_title.font.color.rgb = COLOR_TITLE
            p_title.space_after = Pt(8)
            p_title.alignment = PP_ALIGN.LEFT

            if cd["subtitle"]:
                p_sub = tf_main.add_paragraph()
                p_sub.text = cd["subtitle"]
                p_sub.font.name = FONT_TITLE
                p_sub.font.size = Pt(20 if lang_code == "ja" else 21)
                p_sub.font.italic = (lang_code != "ja")
                p_sub.font.color.rgb = COLOR_SUBTITLE
                p_sub.space_after = Pt(24)
                p_sub.alignment = PP_ALIGN.LEFT

            p_author = tf_main.add_paragraph()
            p_author.text = cd["author"]
            p_author.font.name = FONT_BODY
            p_author.font.size = Pt(14)
            p_author.font.bold = True
            p_author.font.color.rgb = COLOR_BODY
            p_author.space_after = Pt(18)
            p_author.alignment = PP_ALIGN.LEFT

            tb_cred = slide.shapes.add_textbox(Inches(0.223), Inches(6.234), Inches(6.797), Inches(1.001))
            tf_cred = tb_cred.text_frame
            tf_cred.word_wrap = True
            tf_cred.margin_left = Inches(0.1)

            p_ai = tf_cred.paragraphs[0]
            p_ai.text = cd["ai_production"]
            p_ai.font.name = FONT_BODY
            p_ai.font.size = Pt(10)
            p_ai.font.italic = (lang_code != "ja")
            p_ai.font.color.rgb = COLOR_CREDITS
            p_ai.space_after = Pt(6)

            for cr_line in cd["credits"]:
                p_cr = tf_cred.add_paragraph()
                p_cr.text = cr_line
                p_cr.font.name = FONT_BODY
                p_cr.font.size = Pt(9.5)
                p_cr.font.color.rgb = COLOR_CREDITS
                p_cr.space_after = Pt(3)

        elif 2 <= slide_num <= config.get("content_slides_count", 50) + 1:
            # Content Slide
            sentence = parse_content(raw_text)
            override = get_layout_override(slide_num, overrides)

            left = Inches(override["left_in"]) if override and "left_in" in override else Inches(0.90)
            top = Inches(override["top_in"]) if override and "top_in" in override else Inches(2.20)
            width = Inches(override["width_in"]) if override and "width_in" in override else Inches(4.70)
            height = Inches(override["height_in"]) if override and "height_in" in override else Inches(3.20)
            text_color = hex_to_rgb(override["text_color"]) if override and "text_color" in override else COLOR_BODY

            tb = slide.shapes.add_textbox(left, top, width, height)
            tf = tb.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.margin_left = Inches(0.1)
            tf.margin_right = Inches(0.1)
            tf.margin_top = Inches(0.05)
            tf.margin_bottom = Inches(0.05)

            p = tf.paragraphs[0]
            p.text = sentence
            p.font.name = FONT_BODY
            p.font.bold = True

            char_len = len(sentence)
            if lang_code in ["en", "es"]:
                font_size = Pt(30 if char_len <= 55 else (28 if char_len <= 75 else 26))
            else:
                font_size = Pt(28 if char_len <= 22 else (26 if char_len <= 30 else 25))

            p.font.size = font_size
            p.font.color.rgb = text_color
            p.alignment = PP_ALIGN.LEFT
            p.line_spacing = 1.3

            # Slide Numbering
            if num_enabled:
                content_num = slide_num - 1
                fmt = num_cfg.get("format", "{:02d}")
                num_str = fmt.format(content_num)

                num_left = Inches(override["number_left_in"]) if override and "number_left_in" in override else left
                num_top = Inches(override["number_top_in"]) if override and "number_top_in" in override else Inches(num_cfg.get("position", {}).get("top_in", 6.65))
                num_w = Inches(num_cfg.get("position", {}).get("width_in", 2.0))
                num_h = Inches(num_cfg.get("position", {}).get("height_in", 0.40))
                num_color = hex_to_rgb(override["number_color"]) if override and "number_color" in override else text_color

                tb_num = slide.shapes.add_textbox(num_left, num_top, num_w, num_h)
                tf_num = tb_num.text_frame
                tf_num.word_wrap = False
                tf_num.margin_left = Inches(0.1)
                tf_num.margin_top = Inches(0.0)

                p_num = tf_num.paragraphs[0]
                p_num.text = num_str
                p_num.font.name = FONT_NUM
                p_num.font.size = Pt(num_cfg.get("font_size_pt", 14))
                p_num.font.bold = num_cfg.get("bold", True)
                p_num.font.color.rgb = num_color
                p_num.alignment = PP_ALIGN.LEFT

        else:
            # Vocabulary Slides
            title, words = parse_vocab(raw_text)

            tb_title = slide.shapes.add_textbox(Inches(0.850), Inches(0.750), Inches(5.800), Inches(0.421))
            tf_title = tb_title.text_frame
            tf_title.word_wrap = True
            tf_title.margin_left = Inches(0.1)

            p_title = tf_title.paragraphs[0]
            p_title.text = title
            p_title.font.name = FONT_BODY
            p_title.font.size = Pt(25)
            p_title.font.bold = True
            p_title.font.color.rgb = COLOR_TITLE
            p_title.space_after = Pt(14)

            list_w = Inches(7.056 if slide_num == 52 else 7.265)
            list_h = Inches(5.362 if slide_num == 52 else 5.826)
            tb_list = slide.shapes.add_textbox(Inches(0.850), Inches(1.320), list_w, list_h)
            tf_list = tb_list.text_frame
            tf_list.word_wrap = True
            tf_list.margin_left = Inches(0.1)

            vocab_font_size = Pt(22 if lang_code == "ja" else 24)
            for idx, word_line in enumerate(words):
                p_w = tf_list.paragraphs[0] if idx == 0 else tf_list.add_paragraph()
                p_w.text = word_line
                p_w.font.name = FONT_BODY
                p_w.font.size = vocab_font_size
                p_w.font.color.rgb = COLOR_BODY
                p_w.space_after = Pt(6)

    final_out = out_path or config["paths"].get(f"output_pptx_{lang_code}", f"output/slides_{lang_code}.pptx")
    Path(final_out).parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(final_out))
    print(f"  [+] Saved {lang_code.upper()} Presentation: {final_out} ({len(prs.slides)} slides)")
    return final_out

def main():
    parser = argparse.ArgumentParser(description="Assemble multilingual PowerPoint presentations with background typography.")
    parser.add_argument("--config", default="pkg_v1.2/english-class-slides/examples/summer_vacation_japan/deck_config.json", help="Path to deck_config.json")
    parser.add_argument("--lang", choices=["all", "en", "es", "ja"], default="all", help="Target language (default: all)")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        cfg_path = Path("deck_config.json")
    
    config = json.loads(cfg_path.read_text(encoding="utf-8"))
    langs = ["en", "es", "ja"] if args.lang == "all" else [args.lang]

    print("=" * 65)
    print(f"BUILDING PRESENTATION DECKS ({config.get('deck_name', 'Slide Deck')})")
    print("=" * 65)
    for l in langs:
        build_presentation(config, l)
    print("=" * 65)

if __name__ == "__main__":
    main()
