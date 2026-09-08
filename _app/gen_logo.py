import os
from PIL import Image

SRC = 'assets/logo-src.png'
OUT_DIR = 'assets'
SIZES = [16, 32, 64, 128, 256, 512]

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    img = Image.open(SRC).convert('RGBA')
    # 去透明背景留白：按内容裁切
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    # 统一按最大边正方形化（保持比例）
    w, h = img.size
    size = max(w, h)
    square = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    square.paste(img, ((size - w) // 2, (size - h) // 2), img)
    # 生成各尺寸 PNG
    for s in SIZES:
        out = square.resize((s, s), Image.LANCZOS)
        out.save(os.path.join(OUT_DIR, f'logo-{s}.png'))
    # 生成 favicon.ico（16,32,48）
    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    ico_imgs = [square.resize(s, Image.LANCZOS).convert('RGBA') for s in ico_sizes]
    # PIL 保存 ico 多尺寸时，需要把每个尺寸作为独立帧
    ico = ico_imgs[0].copy()
    ico.save(os.path.join(OUT_DIR, 'favicon.ico'), format='ICO', sizes=ico_sizes)
    # 再输出一个默认 logo.png（128px）供 README 使用
    square.resize((128, 128), Image.LANCZOS).save(os.path.join(OUT_DIR, 'logo.png'))
    print('Generated:', [f'logo-{s}.png' for s in SIZES] + ['favicon.ico', 'logo.png'])

if __name__ == '__main__':
    main()
