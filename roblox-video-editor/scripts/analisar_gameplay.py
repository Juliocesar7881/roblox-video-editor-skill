"""Create timestamped contact sheets, review proxy and audio; optionally transcribe locally."""
import argparse, json, math
from pathlib import Path
from media_utils import probe, run

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--interval', type=float, default=10)
    ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--end', type=float)
    ap.add_argument('--proxy', action='store_true')
    ap.add_argument('--transcribe', action='store_true')
    ap.add_argument('--model', default='small')
    args = ap.parse_args()
    if args.interval <= 0:
        ap.error('--interval deve ser positivo')
    src = args.video.resolve(); info = probe(src)
    end = min(args.end if args.end is not None else info['duration'], info['duration'])
    if not 0 <= args.start < end:
        ap.error('Intervalo de analise invalido')
    if (args.out / 'midia.json').exists():
        raise FileExistsError('Pasta ja contem analise; escolha outra --out para evitar frames antigos.')
    args.out.mkdir(parents=True, exist_ok=True)
    info.update(source=str(src), analysis_start=args.start, analysis_end=end)
    (args.out / 'midia.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype('arial.ttf', 18)
    except OSError:
        font = ImageFont.load_default()
    count = math.ceil((end - args.start) / args.interval)
    frame_dir = args.out / 'frames'; frame_dir.mkdir(exist_ok=True)
    # Sequential decode avoids seeking once per thumbnail on hour-long sources.
    run(['-ss', args.start, '-i', src, '-t', end - args.start,
         '-vf', f'fps=1/{args.interval}:start_time=0,scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2',
         '-frames:v', count, frame_dir / 'frame-%06d.jpg'], args.out / 'frames.log')
    files = sorted(frame_dir.glob('frame-*.jpg'))
    timestamps = []
    for page in range(math.ceil(len(files) / 24)):
        sheet = Image.new('RGB', (320 * 4, 208 * 6), '#151515')
        draw = ImageDraw.Draw(sheet)
        for slot, p in enumerate(files[page * 24:(page + 1) * 24]):
            idx = page * 24 + slot; t = args.start + idx * args.interval
            x, y = (slot % 4) * 320, (slot // 4) * 208
            with Image.open(p) as im:
                sheet.paste(im, (x, y))
            label = f'{int(t)//3600:02}:{int(t)//60%60:02}:{t%60:05.2f}'
            draw.text((x + 8, y + 182), label, font=font, fill='white')
            timestamps.append({'time': t, 'frame': p.relative_to(args.out).as_posix()})
        sheet.save(args.out / f'contato-{page+1:03d}.jpg', quality=90)
    (args.out / 'frames.json').write_text(json.dumps(timestamps, indent=2), encoding='utf-8')
    if info['has_audio']:
        audio = args.out / 'audio.wav'
        run(['-ss', args.start, '-i', src, '-t', end - args.start, '-vn', '-ar', '16000', '-ac', '1', audio])
        run(['-i', audio, '-af', 'silencedetect=noise=-35dB:d=0.7', '-f', 'null', '-'], args.out / 'silencios.log')
        if args.transcribe:
            from faster_whisper import WhisperModel
            model = WhisperModel(args.model, device='cpu', compute_type='int8')
            segments, _ = model.transcribe(str(audio), language='pt', vad_filter=True)
            rows = [{'start': s.start + args.start, 'end': s.end + args.start, 'text': s.text} for s in segments]
            (args.out / 'transcricao.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    if args.proxy:
        run(['-ss', args.start, '-i', src, '-t', end - args.start,
             '-vf', 'scale=960:-2', '-c:v', 'libx264', '-crf', '28', '-preset', 'fast',
             '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', args.out / 'proxy.mp4'])
    print(f'Analise criada em {args.out.resolve()}. Frames e silencio sao pistas; revise os trechos em movimento.')

if __name__ == '__main__':
    main()
