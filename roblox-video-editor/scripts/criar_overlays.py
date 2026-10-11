"""Create original transparent stickers from geometric shapes and system fonts; no third-party images."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, random

def font(size):
    # Heavy display faces read best on phones; fall back to whatever the system has.
    for name in ['ariblk.ttf', 'Arial Black.ttf', 'impact.ttf', 'DejaVuSans-Bold.ttf', 'arialbd.ttf']:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()

def burst_points(cx, cy, r_out, r_in, spikes, rng, jitter=.18):
    pts = []
    for n in range(spikes * 2):
        r = (r_out if n % 2 == 0 else r_in) * (1 + rng.uniform(-jitter, jitter))
        a = n * math.pi / spikes - math.pi / 2
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts

def fitted(d, text, size, max_width, stroke):
    # Shrink until the stroked word fits, so no sticker is clipped at its edges.
    while size > 12:
        f = font(size)
        box = d.textbbox((0, 0), text, font=f, stroke_width=stroke)
        if box[2] - box[0] <= max_width:
            return f
        size -= 4
    return font(size)

def text_center(d, xy, text, f, fill, stroke, width):
    d.text(xy, text, font=f, fill=fill, anchor='mm', stroke_width=width, stroke_fill=stroke)

def comic_word(word, fill, burst, seed, size=512, tilt=-8):
    rng = random.Random(seed)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    d.polygon(burst_points(c, c, size * .48, size * .30, 13, rng), fill='#202020')
    d.polygon(burst_points(c, c, size * .44, size * .27, 13, random.Random(seed)), fill=burst)
    layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    f = fitted(ld, word, int(size * .30), size * .70, max(6, size // 40))
    text_center(ld, (c, c), word, f, fill, '#202020', max(6, size // 40))
    img.alpha_composite(layer.rotate(tilt, resample=Image.BICUBIC, center=(c, c)))
    return img

def plain_word(word, fill, seed, size=512, tilt=6):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = fitted(d, word, int(size * .34), size * .80, max(8, size // 28))
    text_center(d, (size / 2, size / 2), word, f, fill, '#202020', max(8, size // 28))
    return img.rotate(tilt, resample=Image.BICUBIC)

def main():
    folder = Path(__file__).resolve().parents[1] / 'assets' / 'overlays'
    folder.mkdir(parents=True, exist_ok=True)
    def save(name, draw_fn):
        image = Image.new('RGBA', (512,512), (0,0,0,0))
        draw_fn(ImageDraw.Draw(image))
        image.save(folder / name)
    save('seta.png', lambda d: d.polygon([(40,205),(275,205),(275,115),(480,256),(275,397),(275,307),(40,307)], fill='#FFE83D', outline='#202020', width=14))
    save('check.png', lambda d: d.line([(70,265),(200,390),(440,120)], fill='#202020', width=82, joint='curve') or d.line([(70,265),(200,390),(440,120)], fill='#4EFF82', width=56, joint='curve'))
    def cross(d):
        for color, width in [('#202020',78),('#FF5470',52)]:
            d.line([(110,110),(402,402)], fill=color,width=width)
            d.line([(402,110),(110,402)], fill=color,width=width)
    save('erro.png', cross)
    def burst(d):
        points=[]
        for n in range(24):
            r=240 if n%2==0 else 125
            points.append((256+math.cos(n*math.pi/12)*r,256+math.sin(n*math.pi/12)*r))
        d.polygon(points,fill='#FFE83D',outline='#202020',width=9)
    save('explosao-cartoon.png',burst)
    def confetti(d):
        rng=random.Random(17)
        colors=['#FF5470','#FFE83D','#4EFF82','#47C8FF','#C687FF']
        for n in range(60):
            x,y=rng.randint(15,475),rng.randint(15,475)
            d.rectangle((x,y,x+12,y+22),fill=colors[n%len(colors)])
    save('confete.png',confetti)
    # Comic words: one per kind of moment (hit, explosion, laugh, surprise, fail).
    for name, word, fill, bg, seed, tilt in [
        ('pow.png', 'POW!', '#FFFFFF', '#FF3B3B', 3, -10), ('bam.png', 'BAM!', '#FFE83D', '#2E7BFF', 5, 8),
        ('boom.png', 'BOOM!', '#FFE83D', '#FF7A00', 7, -6), ('tum.png', 'TUM!', '#FFFFFF', '#9B4DFF', 11, 9),
        ('wow.png', 'UAU!', '#FFFFFF', '#18B85A', 13, -7), ('oops.png', 'OPS!', '#FFFFFF', '#FF4FA3', 17, 7)]:
        comic_word(word, fill, bg, seed, tilt=tilt).save(folder / name)
    plain_word('KKKK', '#FFE83D', 1, tilt=5).save(folder / 'kkkk.png')
    plain_word('?!', '#FF3B3B', 2, tilt=-8).save(folder / 'interrogacao.png')
    def dizzy(d):
        # Ring of stars for a dazed character.
        for n in range(5):
            a = n * 2 * math.pi / 5
            x, y = 256 + math.cos(a) * 170, 256 + math.sin(a) * 70
            pts = [(x + math.cos(k * math.pi / 5 - math.pi / 2) * (46 if k % 2 == 0 else 20),
                    y + math.sin(k * math.pi / 5 - math.pi / 2) * (46 if k % 2 == 0 else 20)) for k in range(10)]
            d.polygon(pts, fill='#FFE83D', outline='#202020', width=6)
        d.ellipse((86, 186, 426, 326), outline='#FFFFFF', width=6)
    save('estrelas-tontas.png', dizzy)
    def bolt(d):
        pts = [(300, 20), (130, 280), (245, 280), (190, 492), (390, 200), (270, 200), (340, 20)]
        d.polygon(pts, fill='#202020')
        d.polygon([(x + (256 - x) * .1, y + (256 - y) * .1) for x, y in pts], fill='#FFE83D')
    save('raio.png', bolt)
    def sweat(d):
        for (x, y, s) in [(150, 150, 1), (330, 230, .8), (220, 330, .65)]:
            r = 70 * s
            d.polygon([(x, y - 2.1 * r), (x - r, y), (x + r, y)], fill='#202020')
            d.ellipse((x - r, y - r, x + r, y + r), fill='#202020')
            r2 = r * .82
            d.polygon([(x, y - 2.0 * r), (x - r2, y), (x + r2, y)], fill='#6FD3FF')
            d.ellipse((x - r2, y - r2, x + r2, y + r2), fill='#6FD3FF')
    save('suor.png', sweat)
    def speed_lines(d):
        rng = random.Random(23)
        for _ in range(26):
            a = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(150, 200); r1 = rng.uniform(235, 256)
            d.line([(256 + math.cos(a) * r0, 256 + math.sin(a) * r0), (256 + math.cos(a) * r1, 256 + math.sin(a) * r1)], fill='#FFFFFF', width=rng.randint(4, 9))
    save('linhas-velocidade.png', speed_lines)
    print(folder)

if __name__ == '__main__':
    main()
