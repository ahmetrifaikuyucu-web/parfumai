#!/usr/bin/env python3
"""ParfumAI kurulum scripti — görselleri oluşturur."""
import os, sys, re, glob
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw, ImageFont
from random import randint
from perfume_engine import _init_database, save_database

IMG_DIR = os.path.join(os.path.dirname(__file__), 'static', 'perfume_images')
W, H = 400, 300
BG_DARK = (10, 10, 15)
BG_LIGHT = (18, 18, 26)

SEASON_NEON = {
    'yaz':      (0xff, 0x66, 0x00),
    'kis':      (0x00, 0xf5, 0xff),
    'dort_mevsim': (0x00, 0xff, 0x88),
    'ilkbahar': (0xff, 0x00, 0xe5),
}

def _make_img(w, h, nr, ng, nb):
    img = Image.new('RGBA', (w, h))
    for y in range(h):
        for x in range(w):
            t = y / h
            n = randint(-8, 8)
            r = min(255, max(0, int(BG_DARK[0] + (BG_LIGHT[0]-BG_DARK[0])*t) + n))
            g = min(255, max(0, int(BG_DARK[1] + (BG_LIGHT[1]-BG_DARK[1])*t) + n))
            b = min(255, max(0, int(BG_DARK[2] + (BG_LIGHT[2]-BG_DARK[2])*t) + n))
            img.putpixel((x, y), (r, g, b, 255))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        a = int(180 - 80*abs(y-h/2)/(h/2))
        for x in range(4):
            px0 = img.getpixel((x, y))
            img.putpixel((x, y), (min(255, px0[0]*0.3+nr*0.7), min(255, px0[1]*0.3+ng*0.7), min(255, px0[2]*0.3+nb*0.7), 255))
    cx, cy = w//2, h//2-10
    for dy in range(-100, 101):
        for dx in range(-100, 101):
            d = (dx*dx+dy*dy)**0.5
            if d > 110: continue
            px, py = cx+dx, cy+dy
            if 0 <= px < w and 0 <= py < h:
                ag = max(0, int(25*(1-d/110)))
                if ag > 0:
                    p0 = img.getpixel((px, py))
                    img.putpixel((px, py), (min(255, p0[0]+int(nr*ag/255)), min(255, p0[1]+int(ng*ag/255)), min(255, p0[2]+int(nb*ag/255)), 255))
    return img, draw

def _txt(draw, txt, font, y, color, w):
    bb = draw.textbbox((0, 0), txt, font=font)
    draw.text(((w-(bb[2]-bb[0]))//2, y), txt, fill=color, font=font)

def generate(brand, name, season):
    nr, ng, nb = SEASON_NEON.get(season, SEASON_NEON['dort_mevsim'])
    img, draw = _make_img(W, H, nr, ng, nb)
    fb = fn = None
    for p in ['C:/Windows/Fonts/arialbd.ttf','C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/segoeuib.ttf']:
        try:
            if fb is None: fb = ImageFont.truetype(p, 90)
            if fn is None: fn = ImageFont.truetype(p, 20)
        except Exception: pass
    if fb is None: fb = ImageFont.load_default()
    if fn is None: fn = ImageFont.load_default()
    init = brand[0].upper() if brand else '?'
    _txt(draw, init, fb, H//2-55, (220, 220, 230, 200), W)
    _txt(draw, brand.upper(), fn, H-70, (120, 120, 140, 200), W)
    dn = name if len(name)<=22 else name[:19]+'...'
    _txt(draw, dn, fn, H-45, (180, 180, 200, 180), W)
    for x in range(W):
        al = int(60*(1-abs(x-W/2)/(W/2)))
        for y in range(H-3, H):
            p = img.getpixel((x, y))
            img.putpixel((x, y), (min(255,p[0]+int(nr*al/255)), min(255,p[1]+int(ng*al/255)), min(255,p[2]+int(nb*al/255)), 255))
    rgb = Image.new('RGB', img.size, (0,0,0))
    rgb.paste(img, (0,0), img)
    return rgb

def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    old = glob.glob(os.path.join(IMG_DIR, '*'))
    if old:
        for f in old: os.remove(f)
        print(f'{len(old)} eski gorsel silindi')
    db = _init_database()
    total = len(db)
    print(f'{total} gorsel olusturuluyor...')
    for i, p in enumerate(db):
        season = p.get('season', 'dort_mevsim')
        if season not in SEASON_NEON: season = 'dort_mevsim'
        safe = re.sub(r'[\\/*?:"<>|]', '_', f'{p["brand"]}_{p["name"]}')[:80]
        safe = safe.replace('/', '_').replace(':', '_')
        jpg_path = os.path.join(IMG_DIR, f'{safe}.jpg')
        webp_path = os.path.join(IMG_DIR, f'{safe}.webp')
        try:
            img = generate(p['brand'], p['name'], season)
            img.save(jpg_path, 'JPEG', quality=88)
            img.save(webp_path, 'WEBP', quality=80)
            p['image_url'] = f'/static/perfume_images/{safe}.jpg'
        except Exception as e:
            print(f'HATA [{i+1}/{total}]: {p["brand"]} {p["name"]} -> {e}')
            p['image_url'] = ''
        if (i+1) % 50 == 0:
            print(f'  [{i+1}/{total}]...')
            save_database()
    save_database()
    done = sum(1 for p in db if p.get('image_url'))
    print(f'Tamam! {done}/{total}')

if __name__ == '__main__':
    main()
