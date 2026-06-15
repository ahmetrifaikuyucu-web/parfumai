#!/usr/bin/env python3
"""Parfüm görsellerini WebP formatına dönüştürür."""
import os, glob
from PIL import Image

IMG_DIR = os.path.join(os.path.dirname(__file__), 'static', 'perfume_images')

def main():
    if not os.path.exists(IMG_DIR):
        print('Gorsel dizini bulunamadi. Once python app.py calistirarak gor sellerin olusmasini bekleyin.')
        return
    
    jpegs = glob.glob(os.path.join(IMG_DIR, '*.jpg')) + glob.glob(os.path.join(IMG_DIR, '*.jpeg'))
    total = len(jpegs)
    print(f'{total} JPEG bulundu, WebP\'ye donusturuluyor...')
    
    for i, path in enumerate(jpegs):
        webp_path = os.path.splitext(path)[0] + '.webp'
        if os.path.exists(webp_path):
            continue
        try:
            img = Image.open(path)
            img.save(webp_path, 'WEBP', quality=80)
        except Exception as e:
            print(f'HATA [{i+1}/{total}]: {os.path.basename(path)} -> {e}')
        
        if (i+1) % 100 == 0:
            print(f'  [{i+1}/{total}]...')
    
    webps = len(glob.glob(os.path.join(IMG_DIR, '*.webp')))
    print(f'Tamam! {webps}/{total} WebP olusturuldu.')

if __name__ == '__main__':
    main()
