"""Create original transparent stickers from geometric shapes; no third-party images."""
from pathlib import Path
from PIL import Image, ImageDraw
import math, random

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
    print(folder)

if __name__ == '__main__':
    main()
