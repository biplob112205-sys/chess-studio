#!/usr/bin/env python3
"""
Chess Video Generator Engine
Autonomous 1080x1920 vertical short-form chess video creator.
Synchronizes voiceover, word-by-word kinetic typography, authentic Chess.com SFX,
and broadcast-grade visual chess animations.
"""

import os, sys, math, subprocess, shutil, json, argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(SKILL_ROOT, "assets")

WIDTH = 1080
HEIGHT = 1920
FPS = 30

SQ = 120
BOARD_X = 60
BOARD_Y = 470
BOARD_SIZE = SQ * 8

# Professional Matte Neutral Color Palette
BG_COLOR = (36, 34, 30)     # Matte warm dark charcoal
LIGHT_SQ = (235, 236, 208) # #ebecd0 Chess.com buff
DARK_SQ = (115, 149, 82)   # #739552 Chess.com green
LIGHT_HL = (245, 246, 130) # #f5f682 Chess.com soft pale yellow
DARK_HL = (186, 202, 68)   # #baca44 Chess.com vibrant olive yellow-green

TEXT_WHITE = (255, 255, 255)
TEXT_MUTED = (160, 160, 160)
ACCENT_GOLD = (250, 204, 21) # Vibrant Amber/Yellow #FACC15
ALERT_RED = (248, 113, 113)  # Coral Red #F87171
ACCENT_GREEN = (74, 222, 128)# Bright Green #4ADE80
ACCENT_CYAN = (56, 189, 248) # Sky Cyan #38BDF8

font_bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
font_reg = "/System/Library/Fonts/Supplemental/Arial.ttf"
if not os.path.exists(font_bold):
    font_bold = "/System/Library/Fonts/HelveticaNeue.ttc"
if not os.path.exists(font_reg):
    font_reg = font_bold

font_header = ImageFont.truetype(font_bold, 32)
font_cap = ImageFont.truetype(font_bold, 44)
font_player_name = ImageFont.truetype(font_bold, 28)
font_player_elo = ImageFont.truetype(font_reg, 24)
font_clock = ImageFont.truetype(font_bold, 26)
font_coord = ImageFont.truetype(font_bold, 18)

font_intro_name = ImageFont.truetype(font_bold, 36)
font_intro_badge = ImageFont.truetype(font_bold, 20)

font_badge_cat = ImageFont.truetype(font_bold, 22)
font_badge_move = ImageFont.truetype(font_bold, 48)
font_badge_desc = ImageFont.truetype(font_reg, 26)

font_modal_title = ImageFont.truetype(font_bold, 44)
font_modal_sub = ImageFont.truetype(font_bold, 24)
font_speech = ImageFont.truetype(font_bold, 22)
font_stat_num = ImageFont.truetype(font_bold, 26)
font_stat_label = ImageFont.truetype(font_bold, 20)
font_btn = ImageFont.truetype(font_bold, 30)
font_btn_sm = ImageFont.truetype(font_bold, 22)

COLOR_MAP = {
    'gold': ACCENT_GOLD,
    'red': ALERT_RED,
    'green': ACCENT_GREEN,
    'cyan': ACCENT_CYAN
}

def load_assets():
    base_bg = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)

    # Pieces
    pieces = {}
    piece_dir = os.path.join(ASSETS_DIR, "pieces")
    names = {
        'K': 'wK', 'Q': 'wQ', 'R': 'wR', 'B': 'wB', 'N': 'wN', 'P': 'wP',
        'k': 'bK', 'q': 'bQ', 'r': 'bR', 'b': 'bB', 'n': 'bN', 'p': 'bP'
    }
    for char, code in names.items():
        p_path = os.path.join(piece_dir, f"{code}.png")
        if os.path.exists(p_path):
            p_img = Image.open(p_path).convert("RGBA")
            p_resized = p_img.resize((102, 102), Image.Resampling.LANCZOS)
            p_sharp = p_resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=140, threshold=2))
            pieces[char] = p_sharp

    # Avatars
    def make_avatar(pil_img, size, radius=12):
        resized = pil_img.resize((size, size), Image.Resampling.LANCZOS)
        mask = Image.new('L', (size, size), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.rounded_rectangle([0, 0, size, size], radius=radius, fill=255)
        out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        out.paste(resized, (0, 0), mask)
        bdraw = ImageDraw.Draw(out)
        bdraw.rounded_rectangle([0, 0, size-1, size-1], radius=radius, outline=(255, 255, 255, 70), width=2)
        return out

    user_avatar_path = os.path.join(ASSETS_DIR, "avatars", "user_avatar.png")
    if os.path.exists(user_avatar_path):
        user_img = Image.open(user_avatar_path)
        biplob_raw = user_img.crop((150, 140, 550, 540)) if user_img.width >= 550 else user_img
    else:
        biplob_raw = Image.new('RGBA', (200, 200), (45, 120, 200, 255))

    avatar_user_header = make_avatar(biplob_raw, 54, radius=8)
    avatar_user_card = make_avatar(biplob_raw, 80, radius=16)

    pawn_avatar_raw = Image.new('RGBA', (200, 200), (220, 225, 230, 255))
    if 'P' in pieces:
        pawn_sprite = pieces['P'].resize((150, 150), Image.Resampling.LANCZOS)
        pawn_avatar_raw.paste(pawn_sprite, (25, 25), pawn_sprite)

    avatar_opp_header = make_avatar(pawn_avatar_raw, 54, radius=8)
    avatar_opp_card = make_avatar(pawn_avatar_raw, 80, radius=16)

    # Brilliant badge
    def create_brilliant_badge(size=56):
        S = size * 2
        img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        pad = 6
        for g in range(12, 0, -2):
            draw.ellipse([pad - g, pad - g, S - pad + g, S - pad + g], fill=(20, 184, 166, 12))
        draw.ellipse([pad + 4, pad + 7, S - pad + 4, S - pad + 7], fill=(0, 0, 0, 120))
        draw.ellipse([pad, pad, S - pad, S - pad], fill=(27, 172, 166))
        draw.arc([pad+2, pad+2, S - pad-2, S - pad-2], start=180, end=360, fill=(255, 255, 255, 120), width=4)
        f = ImageFont.truetype(font_bold, int(S * 0.52))
        draw.text((S // 2, S // 2 - 2), '!!', fill=(255, 255, 255), font=f, anchor='mm')
        return img.resize((size, size), Image.Resampling.LANCZOS)

    brilliant_badge = create_brilliant_badge(56)

    # Coach avatar
    def create_coach_avatar(size=110):
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([0, 0, size, size], fill=(51, 65, 85))
        draw.chord([size*0.1, size*0.55, size*0.9, size*1.2], start=0, end=360, fill=(34, 75, 60))
        draw.polygon([(size*0.4, size*0.65), (size*0.5, size*0.78), (size*0.6, size*0.65)], fill=(255, 255, 255))
        draw.rectangle([size*0.42, size*0.5, size*0.58, size*0.66], fill=(225, 175, 140))
        draw.ellipse([size*0.3, size*0.22, size*0.7, size*0.6], fill=(225, 175, 140))
        draw.chord([size*0.28, size*0.16, size*0.72, size*0.4], start=180, end=360, fill=(80, 50, 30))
        draw.chord([size*0.38, size*0.48, size*0.62, size*0.62], start=0, end=180, fill=(80, 50, 30))
        draw.ellipse([size*0.38, size*0.36, size*0.44, size*0.41], fill=(50, 30, 20))
        draw.ellipse([size*0.56, size*0.36, size*0.62, size*0.41], fill=(50, 30, 20))
        draw.line([size*0.36, size*0.32, size*0.46, size*0.33], fill=(70, 40, 20), width=3)
        draw.line([size*0.54, size*0.33, size*0.64, size*0.32], fill=(70, 40, 20), width=3)
        mask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
        out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        out.paste(img, (0, 0), mask)
        return out

    coach_avatar = create_coach_avatar(110)

    return {
        'base_bg': base_bg,
        'pieces': pieces,
        'avatar_user_header': avatar_user_header,
        'avatar_user_card': avatar_user_card,
        'avatar_opp_header': avatar_opp_header,
        'avatar_opp_card': avatar_opp_card,
        'brilliant_badge': brilliant_badge,
        'coach_avatar': coach_avatar
    }

def draw_trophy_gold(draw, x, y, size):
    w, h = size, size
    pts = [
        (x - w*0.36, y - h*0.38),
        (x + w*0.36, y - h*0.38),
        (x + w*0.26, y + h*0.12),
        (x - w*0.26, y + h*0.12)
    ]
    draw.polygon(pts, fill=ACCENT_GOLD)
    draw.arc([x - w*0.52, y - h*0.32, x - w*0.22, y + h*0.05], start=90, end=270, fill=ACCENT_GOLD, width=3)
    draw.arc([x + w*0.22, y - h*0.32, x + w*0.52, y + h*0.05], start=270, end=90, fill=ACCENT_GOLD, width=3)
    draw.line([x, y + h*0.12, x, y + h*0.32], fill=ACCENT_GOLD, width=5)
    draw.rounded_rectangle([x - w*0.32, y + h*0.32, x + w*0.32, y + h*0.44], radius=3, fill=ACCENT_GOLD)

font_header_large = ImageFont.truetype(font_bold, 40)

def draw_header_pill(draw, title="HOW TO BEAT SCHOLAR'S MATE", cx=540, y=95):
    """
    Renders high-impact broadcast header in two complementary colors (Crisp White + Amber Gold)
    with subtle drop shadow, avoiding narrow container clipping.
    """
    # Split title into two complementary colored parts
    parts = title.split(" - ") if " - " in title else title.split(" | ") if " | " in title else None
    if not parts and len(title.split()) >= 3:
        words = title.split()
        mid = len(words) // 2
        parts = [" ".join(words[:mid]), " ".join(words[mid:])]
    elif not parts:
        parts = [title, ""]

    p1, p2 = parts[0].strip(), parts[1].strip()
    bb1 = font_header_large.getbbox(p1)
    w1 = bb1[2] - bb1[0]
    w2 = 0
    gap = 16 if p2 else 0
    if p2:
        bb2 = font_header_large.getbbox(p2)
        w2 = bb2[2] - bb2[0]

    tot_w = w1 + gap + w2
    start_x = cx - tot_w // 2

    # Drop shadow
    draw.text((start_x + 2, y + 2), p1, fill=(0, 0, 0, 180), font=font_header_large)
    if p2:
        draw.text((start_x + w1 + gap + 2, y + 2), p2, fill=(0, 0, 0, 180), font=font_header_large)

    # Main text
    draw.text((start_x, y), p1, fill=TEXT_WHITE, font=font_header_large)
    if p2:
        draw.text((start_x + w1 + gap, y), p2, fill=ACCENT_GOLD, font=font_header_large)

def draw_kinetic_captions(draw, t, phrases, cx=540, base_y=245):
    active_phrase = None
    for p in phrases:
        if p['t_start'] <= t < p['t_end']:
            active_phrase = p
            break

    if not active_phrase:
        return

    lines = active_phrase['lines']
    space_w = font_cap.getbbox(" ")[2]
    line_h = 58

    total_block_h = len(lines) * line_h
    start_y = base_y - (total_block_h - line_h) // 2

    cur_y = start_y
    for line in lines:
        word_widths = []
        for w_item in line:
            bbox = font_cap.getbbox(w_item['text'])
            word_widths.append(bbox[2] - bbox[0])

        total_line_w = sum(word_widths) + space_w * (len(line) - 1)
        cur_x = cx - total_line_w // 2

        for i, w_item in enumerate(line):
            ww = word_widths[i]
            w_start = w_item.get('start', 0.0)
            w_end = w_item.get('end', 999.0)

            if t < w_start:
                cur_x += ww + space_w
                continue

            base_col = COLOR_MAP.get(w_item.get('color'), TEXT_WHITE)
            is_active = (w_start <= t <= w_end)

            if is_active:
                pill_pad_x = 10
                pill_pad_y = 5
                pill_x1 = cur_x - pill_pad_x
                pill_y1 = cur_y - pill_pad_y
                pill_x2 = cur_x + ww + pill_pad_x
                pill_y2 = cur_y + line_h - 12 + pill_pad_y

                draw.rounded_rectangle([pill_x1, pill_y1, pill_x2, pill_y2], radius=10, fill=(52, 48, 42), outline=(250, 204, 21), width=2)
                draw.text((cur_x + 2, cur_y + 2), w_item['text'], fill=(0, 0, 0), font=font_cap)
                draw.text((cur_x, cur_y), w_item['text'], fill=base_col, font=font_cap)
            else:
                draw.text((cur_x + 2, cur_y + 2), w_item['text'], fill=(0, 0, 0), font=font_cap)
                draw.text((cur_x, cur_y), w_item['text'], fill=base_col, font=font_cap)

            cur_x += ww + space_w

        cur_y += line_h

def draw_intro_card(img, t, assets):
    if t >= 3.8:
        return
    alpha = 1.0
    shift_x = 0
    if t < 0.45:
        p = t / 0.45
        e = 1.0 - (1.0 - p) ** 3
        shift_x = int((1.0 - e) * 550)
        alpha = p
    elif t > 3.2:
        p = (t - 3.2) / 0.6
        e = p ** 3
        shift_x = int(e * 650)
        alpha = max(0.0, 1.0 - p)

    dim_a = int(90 * alpha)
    if dim_a > 0:
        dim_lay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, dim_a))
        img.paste(dim_lay, (0, 0), dim_lay)

    cw, ch = 470, 136
    card_opp = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(card_opp)
    s_img = Image.new('RGBA', (cw + 16, ch + 16), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(s_img)
    sdraw.rounded_rectangle([0, 0, cw + 16, ch + 16], radius=24, fill=(0, 0, 0, int(90 * alpha)))

    cdraw.rounded_rectangle([0, 0, cw, ch], radius=20, fill=(255, 255, 255, int(255 * alpha)))
    card_opp.paste(assets['avatar_opp_card'], (22, 28), assets['avatar_opp_card'])
    cdraw.text((120, 34), "A_mute", fill=(20, 20, 20, int(255 * alpha)), font=font_intro_name)
    draw_trophy_gold(cdraw, 130, 92, 22)
    cdraw.text((150, 92), "SILVER DIVISION", fill=(100, 116, 139, int(255 * alpha)), font=font_intro_badge, anchor="lm")

    opp_x = BOARD_X + 70 - shift_x
    opp_y = BOARD_Y + 180
    img.paste(s_img, (opp_x - 6, opp_y + 4), s_img)
    img.paste(card_opp, (opp_x, opp_y), card_opp)

    card_user = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    cdraw_u = ImageDraw.Draw(card_user)
    cdraw_u.rounded_rectangle([0, 0, cw, ch], radius=20, fill=(38, 36, 33, int(252 * alpha)), outline=(68, 65, 60, int(255 * alpha)), width=2)
    card_user.paste(assets['avatar_user_card'], (22, 28), assets['avatar_user_card'])
    cdraw_u.text((120, 34), "Biplob", fill=(255, 255, 255, int(255 * alpha)), font=font_intro_name)
    draw_trophy_gold(cdraw_u, 130, 92, 22)
    cdraw_u.text((150, 92), "GOLD DIVISION", fill=ACCENT_GOLD, font=font_intro_badge, anchor="lm")

    user_x = BOARD_X + BOARD_SIZE - cw - 70 + shift_x
    user_y = BOARD_Y + 390
    img.paste(s_img, (user_x - 6, user_y + 4), s_img)
    img.paste(card_user, (user_x, user_y), card_user)

    vs_w, vs_h = 92, 54
    vs_img = Image.new('RGBA', (vs_w, vs_h), (0, 0, 0, 0))
    vs_draw = ImageDraw.Draw(vs_img)
    vs_draw.rounded_rectangle([0, 0, vs_w, vs_h], radius=27, fill=(38, 36, 33, int(252 * alpha)), outline=(85, 80, 74, int(255 * alpha)), width=3)
    vs_draw.text((vs_w//2, vs_h//2), "VS", fill=(255, 255, 255, int(255 * alpha)), font=font_player_name, anchor="mm")

    vs_x = BOARD_X + (BOARD_SIZE - vs_w) // 2
    vs_y = BOARD_Y + 328
    img.paste(vs_img, (vs_x, vs_y), vs_img)

def draw_victory_modal(img, t, assets):
    if t < 47.6:
        return

    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 160))
    img.paste(overlay, (0, 0), overlay)

    cw, ch = 740, 780
    cx = (WIDTH - cw) // 2
    cy = 570

    card = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(card)
    cdraw.rounded_rectangle([0, 0, cw, ch], radius=28, fill=(38, 36, 33, 255), outline=(55, 52, 47, 255), width=2)

    # Header
    draw_trophy_gold(cdraw, 80, 75, 60)
    cdraw.text((130, 48), "You Won!", fill=(255, 255, 255), font=font_modal_title)
    cdraw.text((135, 96), "by checkmate", fill=TEXT_MUTED, font=font_modal_sub)
    
    xx = cw - 50
    xy = 55
    cdraw.line([xx - 12, xy - 12, xx + 12, xy + 12], fill=(140, 140, 140), width=3)
    cdraw.line([xx + 12, xy - 12, xx - 12, xy + 12], fill=(140, 140, 140), width=3)

    # Dialogue
    bx, by, bw, bh = 210, 165, 485, 160
    cdraw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=22, fill=(255, 255, 255))
    cdraw.polygon([(bx, by + 65), (bx - 20, by + 80), (bx, by + 95)], fill=(255, 255, 255))
    
    speech_lines = [
        "You executed a great",
        "checkmate attack, capitalizing",
        "on your advantage to win."
    ]
    sy = by + 28
    for line in speech_lines:
        cdraw.text((bx + 30, sy), line, fill=(20, 20, 20), font=font_speech)
        sy += 36

    card.paste(assets['coach_avatar'], (45, by + 25), assets['coach_avatar'])

    # Stats
    col1_x = 150
    col2_x = cw // 2
    col3_x = cw - 150
    stat_y = 380

    cdraw.ellipse([col1_x - 38, stat_y - 18, col1_x - 4, stat_y + 16], fill=(59, 130, 246))
    cdraw.text((col1_x - 21, stat_y - 2), "!", fill=(255, 255, 255), font=font_stat_num, anchor="mm")
    cdraw.text((col1_x + 16, stat_y - 2), "3", fill=(255, 255, 255), font=font_stat_num, anchor="mm")
    cdraw.text((col1_x - 4, stat_y + 36), "Great", fill=(96, 165, 250), font=font_stat_label, anchor="mm")

    cdraw.ellipse([col2_x - 45, stat_y - 18, col2_x - 11, stat_y + 16], fill=(34, 197, 94))
    star_cx, star_cy = col2_x - 28, stat_y - 1
    r_out, r_in = 11, 5
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        ang = -math.pi / 2 + i * math.pi / 5
        pts.append((star_cx + r * math.cos(ang), star_cy + r * math.sin(ang)))
    cdraw.polygon(pts, fill=(255, 255, 255))
    cdraw.text((col2_x + 16, stat_y - 2), "11", fill=(255, 255, 255), font=font_stat_num, anchor="mm")
    cdraw.text((col2_x - 2, stat_y + 36), "Best", fill=(74, 222, 128), font=font_stat_label, anchor="mm")

    cdraw.ellipse([col3_x - 45, stat_y - 18, col3_x - 11, stat_y + 16], fill=(132, 204, 22))
    cdraw.line([col3_x - 35, stat_y - 2, col3_x - 30, stat_y + 6], fill=(255, 255, 255), width=3)
    cdraw.line([col3_x - 30, stat_y + 6, col3_x - 20, stat_y - 8], fill=(255, 255, 255), width=3)
    cdraw.text((col3_x + 16, stat_y - 2), "9", fill=(255, 255, 255), font=font_stat_num, anchor="mm")
    cdraw.text((col3_x - 2, stat_y + 36), "Excellent", fill=(163, 230, 53), font=font_stat_label, anchor="mm")

    # Buttons
    btn_x, btn_y, btn_w, btn_h = 45, 475, cw - 90, 84
    cdraw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=16, fill=(129, 182, 76))
    cdraw.text((cw // 2, btn_y + btn_h // 2), "Game Review", fill=(255, 255, 255), font=font_btn, anchor="mm")

    b_sm_y = 595
    b_sm_h = 68
    b_sm_w = (btn_w - 20) // 2
    cdraw.rounded_rectangle([btn_x, b_sm_y, btn_x + b_sm_w, b_sm_y + b_sm_h], radius=14, fill=(48, 46, 42))
    cdraw.text((btn_x + b_sm_w//2, b_sm_y + b_sm_h//2), "New 10 | 5", fill=(220, 220, 220), font=font_btn_sm, anchor="mm")

    cdraw.rounded_rectangle([btn_x + b_sm_w + 20, b_sm_y, btn_x + btn_w, b_sm_y + b_sm_h], radius=14, fill=(48, 46, 42))
    cdraw.text((btn_x + b_sm_w + 20 + b_sm_w//2, b_sm_y + b_sm_h//2), "Rematch", fill=(220, 220, 220), font=font_btn_sm, anchor="mm")

    img.paste(card, (cx, cy), card)

def draw_realistic_chess_arrow(canvas, from_sq, to_sq, color, progress=1.0, 
                               width=18, head_len=40, head_w=44, 
                               start_off=32, end_off=22):
    f_col = ord(from_sq[0]) - ord('a')
    f_row = 8 - int(from_sq[1])
    t_col = ord(to_sq[0]) - ord('a')
    t_row = 8 - int(to_sq[1])
    f_cx = BOARD_X + f_col * SQ + SQ // 2
    f_cy = BOARD_Y + f_row * SQ + SQ // 2
    t_cx = BOARD_X + t_col * SQ + SQ // 2
    t_cy = BOARD_Y + t_row * SQ + SQ // 2

    dx = t_cx - f_cx
    dy = t_cy - f_cy
    dist = math.hypot(dx, dy)
    if dist < 10: return

    ux, uy = dx / dist, dy / dist
    px, py = -uy, ux

    s_pt = (f_cx + ux * start_off, f_cy + uy * start_off)
    e_pt = (t_cx - ux * end_off, t_cy - uy * end_off)
    tot_len = math.hypot(e_pt[0] - s_pt[0], e_pt[1] - s_pt[1])

    p = min(1.0, max(0.0, progress))
    ease = 1.0 - (1.0 - p)**3
    cur_len = tot_len * ease
    cur_tip = (s_pt[0] + ux * cur_len, s_pt[1] + uy * cur_len)

    h_scale = min(1.0, max(0.0, (p - 0.25) / 0.75))
    cur_h_len = head_len * h_scale
    cur_h_w = head_w * h_scale

    shaft_end_len = max(0.0, cur_len - cur_h_len * 0.75)
    shaft_end = (s_pt[0] + ux * shaft_end_len, s_pt[1] + uy * shaft_end_len)

    alpha = int(color[3] * min(1.0, p * 1.4)) if len(color) > 3 else int(230 * min(1.0, p * 1.4))
    fill_col = (color[0], color[1], color[2], alpha)
    shadow_col = (0, 0, 0, int(alpha * 0.38))
    s_off = (2, 3)

    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    if cur_h_len > 6:
        tip_s = (cur_tip[0] + s_off[0], cur_tip[1] + s_off[1])
        left_s = (cur_tip[0] - ux * cur_h_len + px * (cur_h_w / 2) + s_off[0],
                  cur_tip[1] - uy * cur_h_len + py * (cur_h_w / 2) + s_off[1])
        right_s = (cur_tip[0] - ux * cur_h_len - px * (cur_h_w / 2) + s_off[0],
                   cur_tip[1] - uy * cur_h_len - py * (cur_h_w / 2) + s_off[1])
        recess_s = (cur_tip[0] - ux * (cur_h_len * 0.75) + s_off[0],
                    cur_tip[1] - uy * (cur_h_len * 0.75) + s_off[1])
        draw.polygon([tip_s, left_s, recess_s, right_s], fill=shadow_col)

    draw.line([(s_pt[0] + s_off[0], s_pt[1] + s_off[1]),
               (shaft_end[0] + s_off[0], shaft_end[1] + s_off[1])],
              fill=shadow_col, width=width)
    draw.ellipse([s_pt[0] + s_off[0] - width//2, s_pt[1] + s_off[1] - width//2,
                  s_pt[0] + s_off[0] + width//2, s_pt[1] + s_off[1] + width//2], fill=shadow_col)

    draw.line([s_pt, shaft_end], fill=fill_col, width=width)
    draw.ellipse([s_pt[0] - width//2, s_pt[1] - width//2,
                  s_pt[0] + width//2, s_pt[1] + width//2], fill=fill_col)

    if cur_h_len > 6:
        tip = cur_tip
        left = (cur_tip[0] - ux * cur_h_len + px * (cur_h_w / 2),
                cur_tip[1] - uy * cur_h_len + py * (cur_h_w / 2))
        right = (cur_tip[0] - ux * cur_h_len - px * (cur_h_w / 2),
                 cur_tip[1] - uy * cur_h_len - py * (cur_h_w / 2))
        recess = (cur_tip[0] - ux * (cur_h_len * 0.75),
                  cur_tip[1] - uy * (cur_h_len * 0.75))
        draw.polygon([tip, left, recess, right], fill=fill_col)

    canvas.paste(layer, (0, 0), layer)

def render_chess_short(audio_file, timeline, phrases, title="HOW TO BEAT SCHOLAR'S MATE", output_mp4="output.mp4"):
    assets = load_assets()
    pieces = assets['pieces']
    initial_board = [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]

    # Calculate total duration from timeline
    total_duration = max(item['t_end'] for item in timeline)
    total_frames = int(total_duration * FPS)

    ffmpeg_bin = "./ffmpeg" if os.path.exists("./ffmpeg") else "ffmpeg"
    ffmpeg_cmd = [
        ffmpeg_bin, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", audio_file,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "15",
        "-b:v", "14M",
        "-maxrate", "20M",
        "-bufsize", "28M",
        "-color_primaries", "bt709",
        "-color_trc", "bt709",
        "-colorspace", "bt709",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", "48000",
        "-shortest",
        output_mp4
    ]

    print(f"🎬 Starting render: {total_frames} frames ({total_duration:.1f}s) -> {output_mp4}")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    p_offset = (SQ - 102) // 2

    for f in range(total_frames):
        t = f / FPS
        img = assets['base_bg'].copy()
        draw = ImageDraw.Draw(img)

        board = [row[:] for row in initial_board]
        animating = None
        last_move = None
        active_arrows = []
        active_target_rings = []
        active_check_ring = None
        active_badge = None
        arrow_start_time = None
        brilliant_active = False
        brilliant_land_t = None

        for item in timeline:
            t_start = item['t_start']
            t_end = item['t_end']

            if t >= t_start:
                if 'badge' in item:
                    active_badge = item['badge']
                if 'check_ring' in item:
                    active_check_ring = item['check_ring']
                else:
                    active_check_ring = None

            if t >= t_start and 'move' in item:
                m = item['move']
                f_col, f_row = ord(m['from'][0]) - ord('a'), 8 - int(m['from'][1])
                t_col, t_row = ord(m['to'][0]) - ord('a'), 8 - int(m['to'][1])
                dur = m.get('dur', 0.35)
                last_move = m

                if t < t_start + dur:
                    p = (t - t_start) / dur
                    ease_p = 1.0 - (1.0 - p) ** 3
                    cur_c = f_col + (t_col - f_col) * ease_p
                    cur_r = f_row + (t_row - f_row) * ease_p
                    animating = {'piece': m['piece'], 'c': cur_c, 'r': cur_r}
                    board[f_row][f_col] = '.'
                else:
                    board[f_row][f_col] = '.'
                    board[t_row][t_col] = m['piece']

                if item.get('is_brilliant'):
                    brilliant_active = (t >= t_start + dur)
                    brilliant_land_t = t_start + dur

            if t_start <= t < t_end:
                if 'arrows' in item:
                    m_dur = item['move']['dur'] if 'move' in item else 0.0
                    arr_ready = t_start + m_dur + 0.15
                    if t >= arr_ready:
                        active_arrows = item['arrows']
                        arrow_start_time = arr_ready
                    else:
                        active_arrows = []
                else:
                    active_arrows = []

                if 'target_rings' in item:
                    active_target_rings = item['target_rings']
                else:
                    active_target_rings = []

        # 1. Header
        draw_header_pill(draw, title=title, cx=540, y=105)

        # 2. Kinetic Captions
        draw_kinetic_captions(draw, t, phrases, cx=540, base_y=245)

        # 3. Top Player Bar: Opponent (Alex_Miller 1580)
        bar_y = BOARD_Y - 75
        img.paste(assets['avatar_opp_header'], (BOARD_X, bar_y + 10), assets['avatar_opp_header'])
        opp_name = "Alex_Miller"
        opp_elo = "(1580)"
        draw.text((BOARD_X + 68, bar_y + 14), opp_name, fill=TEXT_WHITE, font=font_player_name)
        opp_w = font_player_name.getbbox(opp_name)[2] - font_player_name.getbbox(opp_name)[0]
        draw.text((BOARD_X + 80 + opp_w, bar_y + 17), opp_elo, fill=TEXT_MUTED, font=font_player_elo)
        for i, h in enumerate([6, 10, 14, 18]):
            draw.rectangle([BOARD_X + 255 + i*5, bar_y + 36 - h, BOARD_X + 258 + i*5, bar_y + 36], fill=(34, 197, 94))
        
        clk_w, clk_h = 130, 48
        draw.rounded_rectangle([BOARD_X + BOARD_SIZE - clk_w, bar_y + 12, BOARD_X + BOARD_SIZE, bar_y + 12 + clk_h], radius=8, fill=(255, 255, 255))
        draw.text((BOARD_X + BOARD_SIZE - clk_w//2, bar_y + 12 + clk_h//2), "5:00", fill=(20, 20, 20), font=font_clock, anchor="mm")

        # 4. Board Squares
        b_shadow = Image.new('RGBA', (BOARD_SIZE + 20, BOARD_SIZE + 20), (0, 0, 0, 0))
        bsdraw = ImageDraw.Draw(b_shadow)
        bsdraw.rectangle([0, 0, BOARD_SIZE + 20, BOARD_SIZE + 20], fill=(0, 0, 0, 120))
        img.paste(b_shadow, (BOARD_X - 6, BOARD_Y - 2), b_shadow)

        board_surface = Image.new('RGBA', (BOARD_SIZE, BOARD_SIZE), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(board_surface)

        highlight_sqs = set()
        if last_move:
            for s in [last_move.get('from'), last_move.get('to')]:
                if s:
                    c = ord(s[0]) - ord('a')
                    r = 8 - int(s[1])
                    highlight_sqs.add((c, r))

        for r in range(8):
            for c in range(8):
                is_dark = (r + c) % 2 == 1
                color = (DARK_HL if is_dark else LIGHT_HL) if (c, r) in highlight_sqs else (DARK_SQ if is_dark else LIGHT_SQ)
                x1, y1 = c * SQ, r * SQ
                bdraw.rectangle([x1, y1, x1 + SQ, y1 + SQ], fill=color)

                if c == 0:
                    text_col = LIGHT_SQ if is_dark else DARK_SQ
                    bdraw.text((x1 + 6, y1 + 4), str(8 - r), fill=text_col, font=font_coord)
                if r == 7:
                    text_col = LIGHT_SQ if is_dark else DARK_SQ
                    bdraw.text((x1 + SQ - 16, y1 + SQ - 22), chr(ord('a') + c), fill=text_col, font=font_coord)

        img.paste(board_surface, (BOARD_X, BOARD_Y), board_surface)

        # 5. Bottom Player Bar: Biplob (1620)
        bbar_y = BOARD_Y + BOARD_SIZE + 15
        img.paste(assets['avatar_user_header'], (BOARD_X, bbar_y + 10), assets['avatar_user_header'])
        user_name = "Biplob"
        user_elo = "(1620)"
        draw.text((BOARD_X + 68, bbar_y + 14), user_name, fill=TEXT_WHITE, font=font_player_name)
        user_w = font_player_name.getbbox(user_name)[2] - font_player_name.getbbox(user_name)[0]
        draw.text((BOARD_X + 80 + user_w, bbar_y + 17), user_elo, fill=TEXT_MUTED, font=font_player_elo)
        for i, h in enumerate([6, 10, 14, 18]):
            draw.rectangle([BOARD_X + 245 + i*5, bbar_y + 36 - h, BOARD_X + 248 + i*5, bbar_y + 36], fill=(34, 197, 94))
        
        draw.rounded_rectangle([BOARD_X + BOARD_SIZE - clk_w, bbar_y + 12, BOARD_X + BOARD_SIZE, bbar_y + 12 + clk_h], radius=8, fill=(24, 23, 21), outline=(80, 80, 80), width=2)
        blitz_secs = max(165, int(180 - t))
        draw.text((BOARD_X + BOARD_SIZE - clk_w//2, bbar_y + 12 + clk_h//2), f"{blitz_secs//60}:{blitz_secs%60:02d}", fill=TEXT_WHITE, font=font_clock, anchor="mm")

        # 6. Stationary Pieces
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p != '.':
                    px = BOARD_X + c * SQ + p_offset
                    py = BOARD_Y + r * SQ + p_offset
                    p_sprite = pieces[p]
                    img.paste(p_sprite, (px, py), p_sprite)

        # Check Ring
        if active_check_ring:
            cc = ord(active_check_ring[0]) - ord('a')
            cr = 8 - int(active_check_ring[1])
            k_cx = BOARD_X + cc * SQ + SQ // 2
            k_cy = BOARD_Y + cr * SQ + SQ // 2
            ch_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
            ch_draw = ImageDraw.Draw(ch_img)
            ch_draw.ellipse([k_cx - 54, k_cy - 54, k_cx + 54, k_cy + 54], fill=(239, 68, 68, 140))
            img.paste(ch_img, (0, 0), ch_img)
            k_p = board[cr][cc]
            if k_p != '.':
                img.paste(pieces[k_p], (BOARD_X + cc * SQ + p_offset, BOARD_Y + cr * SQ + p_offset), pieces[k_p])

        # 7. Animating Piece (Flat 2D glide)
        if animating:
            c_x = int(BOARD_X + animating['c'] * SQ + p_offset)
            c_y = int(BOARD_Y + animating['r'] * SQ + p_offset)
            p_sprite = pieces[animating['piece']]
            img.paste(p_sprite, (c_x, c_y), p_sprite)

        # 8. Target Rings
        for tr in active_target_rings:
            tc = ord(tr[0]) - ord('a')
            tr_r = 8 - int(tr[1])
            t_cx = BOARD_X + tc * SQ + SQ // 2
            t_cy = BOARD_Y + tr_r * SQ + SQ // 2
            r_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
            rdraw = ImageDraw.Draw(r_img)
            rdraw.ellipse([t_cx - 48, t_cy - 48, t_cx + 48, t_cy + 48], outline=(239, 68, 68, 220), width=5)
            rdraw.line([t_cx - 16, t_cy, t_cx + 16, t_cy], fill=(239, 68, 68, 220), width=4)
            rdraw.line([t_cx, t_cy - 16, t_cx, t_cy + 16], fill=(239, 68, 68, 220), width=4)
            img.paste(r_img, (0, 0), r_img)

        # 9. Realistic Tactical Arrows (On top of pieces, Chess.com chevron style)
        if active_arrows:
            growth_p = min(1.0, (t - arrow_start_time) / 0.28) if arrow_start_time else 1.0
            for arr in active_arrows:
                col = arr.get('color', ALERT_RED)
                draw_realistic_chess_arrow(img, arr['from'], arr['to'], col, progress=growth_p)

        # 10. Brilliant Move Ripple
        if brilliant_active and t < 42.5:
            e4_x = BOARD_X + 4 * SQ
            e4_y = BOARD_Y + 4 * SQ
            time_since_land = t - brilliant_land_t
            if time_since_land < 0.6:
                sw_p = time_since_land / 0.6
                sw_r = int(50 + 70 * sw_p)
                sw_a = int(220 * (1.0 - sw_p))
                sw_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
                sw_draw = ImageDraw.Draw(sw_img)
                cx_e4 = e4_x + SQ // 2
                cy_e4 = e4_y + SQ // 2
                sw_draw.ellipse([cx_e4 - sw_r, cy_e4 - sw_r, cx_e4 + sw_r, cy_e4 + sw_r], outline=(20, 184, 166, sw_a), width=6)
                img.paste(sw_img, (0, 0), sw_img)

            b_x = e4_x + SQ - 44
            b_y = e4_y - 12
            if time_since_land < 0.25:
                p_b = time_since_land / 0.25
                scale_b = 0.3 + 0.7 * (1.0 - (1.0 - p_b) ** 2) + 0.3 * math.sin(p_b * math.pi)
                bw = int(56 * scale_b)
                bh = int(56 * scale_b)
                b_scaled = assets['brilliant_badge'].resize((bw, bh), Image.Resampling.LANCZOS)
                img.paste(b_scaled, (b_x + (56 - bw)//2, b_y + (56 - bh)//2), b_scaled)
            else:
                img.paste(assets['brilliant_badge'], (b_x, b_y), assets['brilliant_badge'])

        # 11. Tactical Card
        if active_badge:
            bx, by, bw, bh = BOARD_X, 1530, BOARD_SIZE, 195
            c_shadow = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
            csdraw = ImageDraw.Draw(c_shadow)
            csdraw.rounded_rectangle([0, 0, bw, bh], radius=20, fill=(0, 0, 0, 80))
            img.paste(c_shadow, (bx + 4, by + 6), c_shadow)

            is_brill = active_badge.get('cat') == 'BRILLIANT SACRIFICE'
            border_col = (20, 184, 166) if is_brill else (68, 65, 60)
            tag_col = (20, 184, 166) if is_brill else ACCENT_GOLD

            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=20, fill=(45, 42, 38), outline=border_col, width=3 if is_brill else 2)
            draw.text((bx + 36, by + 24), active_badge['cat'], fill=tag_col, font=font_badge_cat)
            draw.text((bx + 36, by + 60), active_badge['move'], fill=TEXT_WHITE, font=font_badge_move)
            draw.text((bx + 36, by + 138), active_badge['desc'], fill=(185, 185, 185), font=font_badge_desc)

        # 12. Overlays
        draw_intro_card(img, t, assets)
        draw_victory_modal(img, t, assets)

        proc.stdin.write(img.tobytes())

        if f % 150 == 0 or f == total_frames - 1:
            pct = (f + 1) / total_frames * 100
            print(f"Render progress: {f+1}/{total_frames} ({pct:.1f}%) [t={t:.1f}s]")

    proc.stdin.close()
    proc.wait()

    if proc.returncode != 0:
        print("FFmpeg error:", proc.stderr.read().decode())
        sys.exit(1)

    print(f"\n✅ Video successfully generated at: {output_mp4} ({os.path.getsize(output_mp4)/(1024*1024):.2f} MB)")
