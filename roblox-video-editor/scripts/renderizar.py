"""Render an agent-authored edit decision list with FFmpeg. No automatic semantic editing."""
import argparse, collections, hashlib, json, math, tempfile
from pathlib import Path
from media_utils import probe, run, filter_path

# ASS colours are &HAABBGGRR.
COLORS = {'branco': '&H00FFFFFF', 'amarelo': '&H0000E6FF', 'vermelho': '&H003C3CFF', 'verde': '&H005AE63C',
          'azul': '&H00FFAA3C', 'rosa': '&H00C85AFF', 'laranja': '&H00008CFF', 'roxo': '&H00FF5AA0', 'ouro': '&H004FE5FF', 'ciano': '&H00FFE960', 'coral': '&H007777FF'}
CAPTION_STYLES = ('fala', 'legenda', 'karaoke', 'grito', 'titulo')
FONTES = Path(__file__).resolve().parents[1] / 'assets' / 'fontes'
EFFECT_TYPES = ('punch', 'zoom', 'shake', 'flash')
FLASH_COLORS = {'branco': 'white', 'amarelo': 'yellow', 'vermelho': 'red', 'preto': 'black'}


def number(value, name, lo=0, hi=1e8):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not lo <= value <= hi:
        raise ValueError(f'{name}: numero esperado entre {lo} e {hi}')
    return float(value)

def path_at(root, name):
    p = Path(name)
    p = p if p.is_absolute() else root / p
    p = p.resolve()
    if not p.is_file():
        raise FileNotFoundError(p)
    return p

def ass_time(t):
    c = round(t * 100)
    return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'

def native_resolution(info, vertical):
    width,height=info['width'],info['height']
    if not width or not height or width%2 or height%2:
        raise ValueError('Fonte sem dimensoes pares: edicao H.264 exige adaptacao explicita.')
    wide,tall=max(width,height),min(width,height)
    # For ordinary 16:9 gameplay, preserve the exact dimensions; transpose for Shorts.
    if abs(wide/tall-16/9)<.002:
        return (tall,wide) if vertical else (wide,tall)
    # A non-16:9 source retains its longest edge; padding supplies the required aspect.
    other=round(wide*9/16/2)*2
    return (other,wide) if vertical else (wide,other)

def clean_text(value, highlight=None, base=None):
    # All text is supplied as data. Escape ASS syntax and strip control codes.
    text = str(value).replace('\\', '＼').replace('{', '(').replace('}', ')')
    text = ''.join(ch for ch in text if ord(ch) >= 32 or ch == '\n').replace('\n', r'\N')
    if not (highlight and base):
        return text.replace('*', '')
    # *palavra* marks the key word of a line, as in word-by-word Shorts captions.
    parts = text.split('*')
    return ''.join(p if i % 2 == 0 else '{\\c' + highlight + '&}' + p + '{\\c' + base + '&}' for i, p in enumerate(parts))

def make_ass(path, captions, w, h, total, preview):
    fs = round(w * .058) if h > w else round(h * .065)
    # Reaction text must read on a phone at a glance: much larger than dialogue.
    big, top = round(fs * (2.0 if h > w else 1.8)), round(fs * 1.5)
    header = f'''[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: fala,Arial,{fs},&H00FFFFFF,&H000000FF,&H00101010,&H60000000,-1,0,0,0,100,100,0,0,1,{max(3,round(fs*.06))},1,2,{int(w*.12)},{int(w*.16)},{int(h*.23)},1
Style: legenda,Arial Black,{round(fs*1.5)},&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{max(4,round(fs*.11))},{max(2,round(fs*.05))},2,{int(w*.07)},{int(w*.07)},{int(h*.3)},1
Style: karaoke,Lilita One,{round(w*.089 if h > w else h*.08)},&H00FFFFFF,&H000000FF,&H003E2810,&H003E2810,0,0,0,0,100,100,0,0,1,{max(4,round((w*.089 if h > w else h*.08)*.075))},0,2,0,0,0,1
Style: grito,Arial Black,{big},{COLORS['amarelo']},&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{max(5,round(big*.09))},{max(2,round(big*.05))},5,{int(w*.06)},{int(w*.06)},0,1
Style: titulo,Arial Black,{top},&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{max(4,round(top*.08))},{max(2,round(top*.04))},8,{int(w*.08)},{int(w*.08)},{int(h*.1)},1
Style: Preview,Arial,{int(fs*.5)},&H0060FFFF,&H000000FF,&H00101010,&H60000000,0,0,0,0,100,100,0,0,1,2,0,8,10,10,10,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
    lines = []
    for i, c in enumerate(captions):
        start = number(c['start'], 'caption.start', hi=total)
        # Small float drift from summed clip durations should not abort a long render.
        end = min(number(c['end'], 'caption.end', lo=start + .01, hi=total + .1), total)
        style = c.get('style', 'fala')
        if style not in CAPTION_STYLES:
            raise ValueError(f'caption.style deve ser um de {CAPTION_STYLES}')
        color = c.get('color')
        if color is not None and color not in COLORS:
            raise ValueError(f'caption.color deve ser um de {sorted(COLORS)}')
        tag = rf'\c{COLORS[color]}&' if color else ''
        base = COLORS[color] if color else (COLORS['amarelo'] if style == 'grito' else COLORS['branco'])
        highlight = c.get('highlight', 'verde' if style == 'grito' else 'amarelo')
        if highlight not in COLORS:
            raise ValueError(f'caption.highlight deve ser um de {sorted(COLORS)}')
        if style == 'karaoke':
            # Receita dos Shorts de referencia (roblox-shorts-generator): Lilita One branca, contorno e
            # sombra #10283E deslocada para baixo, palavra falada colorida, grupos de ate 2 palavras
            # ~10% maiores, entrada elastica 83% -> 104% -> 100% em 0,22 s subindo um pouco, fade de
            # 45 ms na entrada e 75 ms na saida do grupo.
            sombra = r'\xshad' + str(max(1, round(w * .002))) + r'\yshad' + str(max(2, round(w * .0065)))
            palavras = len(str(c['text']).replace('*', '').split())
            esc = 110 if palavras <= 2 else 100
            try:
                from PIL import ImageFont
                tam = round(w * .089 if h > w else h * .08)
                fonte = ImageFont.truetype(str(FONTES / 'LilitaOne-Regular.ttf'), tam)
                # 0.87: o libass desenha a fonte menor que o PIL no mesmo tamanho (medido).
                largura = 0.87 * fonte.getlength(str(c['text']).replace('*', '').upper()) * esc / 100
                if largura > .86 * w:
                    esc = round(esc * .86 * w / largura)
            except (ImportError, OSError):
                pass
            # Posicao fixa: eventos posicionados nunca sao empilhados pelo libass (sem linha duplicada).
            x, y = round(w / 2), round(h * .722 if h > w else h * .86)
            if c.get('entrada'):
                pos = rf'\move({x},{y + round(w * .011)},{x},{y},0,120)'
                entrada = (rf'\fscx{round(esc * .83)}\fscy{round(esc * .83)}'
                           rf'\t(0,60,\fscx{round(esc * 1.016)}\fscy{round(esc * 1.016)})'
                           rf'\t(60,105,\fscx{round(esc * 1.035)}\fscy{round(esc * 1.035)})'
                           rf'\t(105,160,\fscx{round(esc * 1.004)}\fscy{round(esc * 1.004)})'
                           rf'\t(160,220,\fscx{esc}\fscy{esc})')
            else:
                pos = rf'\pos({x},{y})'
                entrada = rf'\fscx{esc}\fscy{esc}'
            fade = ''
            if c.get('entrada') or c.get('saida'):
                fade = rf'\fad({45 if c.get("entrada") else 0},{75 if c.get("saida") else 0})'
            animation = '{' + pos + sombra + fade + entrada + tag + '}'
            highlight = c.get('highlight', 'ouro')
        elif style == 'legenda':
            # Word-by-word captions: quick pop and no fade, so consecutive words feel snappy.
            animation = r'{\fscx80\fscy80\t(0,80,\fscx106\fscy106)\t(80,140,\fscx100\fscy100)' + tag + '}'
        elif style == 'fala':
            animation = r'{\fad(60,80)\fscx90\fscy90\t(0,120,\fscx100\fscy100)' + tag + '}'
        else:
            # Cartoon pop: grows past full size, settles, with a slight alternating tilt.
            tilt = (3 if i % 2 else -3) if style == 'grito' else 0
            animation = (r'{\fad(0,120)\fscx15\fscy15\frz' + str(tilt) +
                         r'\t(0,110,\fscx128\fscy128)\t(110,210,\fscx100\fscy100)' + tag + '}')
        layer = 0 if style in ('fala', 'legenda', 'karaoke') else 1
        lines.append(f'Dialogue: {layer},{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{animation}{clean_text(c["text"], COLORS[highlight], base)}')
    if preview:
        lines.append(f'Dialogue: 2,0:00:00.00,{ass_time(total)},Preview,,0,0,0,,PREVIA - LICENCAS PENDENTES')
    path.write_text(header + '\n'.join(lines) + '\n', encoding='utf-8-sig')

def camera_filters(effects, w, h, fps, total):
    """Timeline-level punch/zoom/shake as one zoompan pass and flashes as drawbox layers."""
    z_terms, cx_terms, cy_terms, dx_terms, dy_terms, flashes = [], [], [], [], [], []
    for e in effects:
        kind = e.get('type')
        if kind not in EFFECT_TYPES:
            raise ValueError(f'effect.type deve ser um de {EFFECT_TYPES}')
        a = number(e['at'], 'effect.at', hi=total)
        default = {'punch': .35, 'zoom': 1.2, 'shake': .45, 'flash': .12}[kind]
        d = number(e.get('duration', default), 'effect.duration', lo=.04, hi=max(.04, total - a + .05))
        b = a + d
        win = f'between(it,{a:.3f},{b:.3f})'
        if kind == 'flash':
            color = e.get('color', 'branco')
            if color not in FLASH_COLORS:
                raise ValueError(f'effect.color deve ser um de {sorted(FLASH_COLORS)}')
            alpha = number(e.get('intensity', .75), 'flash.intensity', lo=.05, hi=1)
            mid = a + d / 2
            for lo, hi, al in [(a, mid, alpha), (mid, b, alpha * .45)]:
                flashes.append(f"drawbox=x=0:y=0:w=iw:h=ih:color={FLASH_COLORS[color]}@{al:.2f}:t=fill:enable='between(t,{lo:.3f},{hi:.3f})'")
            continue
        if kind == 'shake':
            amp = number(e.get('intensity', 1), 'shake.intensity', lo=.1, hi=3) * .018
            # Margin so the shaken window never leaves the frame.
            z_terms.append(f'{win}*{2.4*amp:.4f}')
            decay = f'(1-(it-{a:.3f})/{d:.3f})'
            dx_terms.append(f'{win}*{amp:.4f}*iw*{decay}*sin(107*(it-{a:.3f}))')
            dy_terms.append(f'{win}*{amp*.7:.4f}*ih*{decay}*cos(83*(it-{a:.3f}))')
            continue
        amount = number(e.get('intensity', .28 if kind == 'punch' else .2), f'{kind}.intensity', lo=.02, hi=1)
        cx, cy = (number(v, 'effect.center', hi=1) for v in e.get('center', [.5, .5]))
        if kind == 'punch':
            # Snap in on the hit, ease back out.
            z_terms.append(f'{win}*{amount:.4f}*pow(1-(it-{a:.3f})/{d:.3f},2)')
        else:
            ramp = min(.18, d / 3)
            z_terms.append(f'{win}*{amount:.4f}*min(1,min((it-{a:.3f})/{ramp:.3f},({b:.3f}-it)/{ramp:.3f}))')
        cx_terms.append(f'{win}*{cx-.5:.4f}')
        cy_terms.append(f'{win}*{cy-.5:.4f}')
    filters = []
    if z_terms:
        z = '1+' + '+'.join(z_terms)
        cx = '0.5' + ''.join('+' + t for t in cx_terms)
        cy = '0.5' + ''.join('+' + t for t in cy_terms)
        dx = ''.join('+' + t for t in dx_terms)
        dy = ''.join('+' + t for t in dy_terms)
        x = f"clip((iw-iw/zoom)*({cx}){dx},0,iw-iw/zoom)"
        y = f"clip((ih-ih/zoom)*({cy}){dy},0,ih-ih/zoom)"
        filters.append(f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={w}x{h}:fps={fps}")
    return filters + flashes

def atempo_chain(speed):
    parts, s = [], speed
    while s < .5:
        parts.append('atempo=0.5'); s /= .5
    while s > 2:
        parts.append('atempo=2'); s /= 2
    if abs(s - 1) > 1e-6:
        parts.append(f'atempo={s:.6g}')
    return parts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('timeline', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--library', type=Path)
    ap.add_argument('--preview', action='store_true', help='Allow unverified SFX; watermark and exclude commercial readiness')
    args = ap.parse_args()
    root = args.timeline.resolve().parent
    spec = json.loads(args.timeline.read_text(encoding='utf-8-sig'))
    skill=Path(__file__).resolve().parents[1]
    config=json.loads((skill/'config.json').read_text(encoding='utf-8'))
    if (skill/'config.local.json').exists():
        config.update(json.loads((skill/'config.local.json').read_text(encoding='utf-8')))
    explicit=args.library or spec.get('library')
    lib=Path(explicit or config['library_root'])
    lib=(lib if lib.is_absolute() else (root if explicit else skill)/lib).resolve()
    catalog = json.loads((lib / 'catalogo.json').read_text(encoding='utf-8'))['assets']
    allowed = {(lib / a['path']).resolve(): a for a in catalog}
    credits = []
    verified = {}
    def asset(name):
        p = path_at(lib, name)
        a = allowed.get(p)
        if not a:
            raise ValueError(f'Audio ausente no catalogo: {p}')
        if p not in verified:
            verified[p] = hashlib.sha256(p.read_bytes()).hexdigest() == a['sha256']
        if not verified[p]:
            raise ValueError(f'Audio mudou desde a verificacao: {p}')
        if not args.preview and not a.get('commercial_allowed'):
            raise ValueError(f'Licenca comercial nao comprovada: {p}. Use alternativa liberada ou gere --preview.')
        if a.get('attribution') and a['attribution'] not in credits:
            credits.append(a['attribution'])
        return p
    outputs = spec['outputs']
    kinds = [o['format'] for o in outputs]
    delivery = spec.get('entrega', 'gameplay')
    if delivery == 'gameplay':
        if kinds.count('long') < 1 or kinds.count('short') < 2:
            raise ValueError('A entrega deve ter um longo e pelo menos dois Shorts.')
    elif delivery == 'shorts':
        # Animated Shorts made in Roblox Studio: each output stands alone.
        if not outputs or any(k != 'short' for k in kinds):
            raise ValueError('entrega "shorts" aceita somente outputs com format "short"')
    else:
        raise ValueError('entrega deve ser "gameplay" ou "shorts"')
    reference=spec.get('primary_source') or next((o for o in outputs if o['format']=='long'), outputs[0])['clips'][0]['source']
    native=probe(path_at(root,reference))
    args.out.mkdir(parents=True, exist_ok=True)
    completed = []
    for oi, output in enumerate(outputs):
        credits.clear()
        if output['format'] not in {'long', 'short'}:
            raise ValueError('Formato deve ser long ou short')
        vertical = output['format'] == 'short'
        w,h=native_resolution(native,vertical)
        expected_resolution=(w,h)
        if 'resolution' in output:
            w, h = output['resolution']
            if not all(isinstance(v, int) and v > 0 and v % 2 == 0 for v in (w,h)):
                raise ValueError('Resolucao deve ter dimensoes pares positivas')
            if abs(w/h - (9/16 if vertical else 16/9)) > .002:
                raise ValueError('Proporcao incorreta')
            if not args.preview and (w,h)!=expected_resolution:
                raise ValueError(f'Preserve a resolucao da fonte: esperado {expected_resolution}, recebido {(w,h)}')
        fps = number(output.get('fps', native['fps']), 'fps', lo=1, hi=240)
        if not args.preview and abs(fps-native['fps'])>.02:
            raise ValueError(f'Preserve o FPS da fonte: {native["fps"]}')
        name = output['name']
        if Path(name).name != name or not name.endswith('.mp4'):
            raise ValueError('name deve ser nome simples terminado em .mp4')
        dest = args.out / name
        if dest.exists():
            raise FileExistsError(f'Exportacao ja existe; escolha outra pasta: {dest}')
        if not output.get('music'):
            raise ValueError('Toda exportacao precisa de musica de fundo')
        # Captions, effects and overlays may carry their own sound; they join the SFX list.
        sfx_rows = list(output.get('sfx', []))
        for group in ('captions', 'effects', 'overlays'):
            for row in output.get(group, []):
                if row.get('sfx'):
                    at = row['start'] if group == 'captions' else row['at']
                    sfx_rows.append({'file': row['sfx'], 'at': at, 'gain_db': row.get('sfx_gain_db', -8),
                                     **({'pitch': row['sfx_pitch']} if 'sfx_pitch' in row else {})})
        # Validate licensing before potentially expensive video encoding.
        for audio in [*output.get('music', []), *sfx_rows]:
            asset(audio['file'])
        with tempfile.TemporaryDirectory(prefix='roblox-edit-') as td:
            tmp = Path(td)
            parts = []; total = 0.0
            for ci, clip in enumerate(output['clips']):
                src = path_at(root, clip['source'])
                inf = probe(src)
                start = number(clip['in'], 'in', hi=inf['duration'])
                end = number(clip['out'], 'out', lo=start+.02, hi=inf['duration']+.01)
                src_duration = end - start
                speed = number(clip.get('speed', 1), 'speed', lo=.25, hi=4)
                freeze = number(clip.get('freeze', 0), 'freeze', hi=4)
                reverse = bool(clip.get('reverse', False))
                if reverse and src_duration > 3:
                    raise ValueError('reverse aceita no maximo 3 s de fonte (usa memoria para todos os quadros)')
                moving = src_duration / speed
                duration = moving + freeze
                total += duration
                zoom = clip.get('zoom', [1, 1]); center = clip.get('center', [.5,.5])
                z0, z1 = (number(z, 'zoom', lo=1, hi=2) for z in zoom)
                cx, cy = (number(c, 'center', hi=1) for c in center)
                filters = []
                if clip.get('framing', 'crop') == 'fit':
                    if zoom != [1, 1]:
                        raise ValueError('framing=fit nao aceita zoom; use crop')
                    filters += [f'scale={w}:{h}:force_original_aspect_ratio=decrease', f'pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x151515']
                elif clip.get('framing', 'crop') == 'crop':
                    # Static punch-in: dynamic zoom is applied afterward with a fixed crop window.
                    ratio = w / h
                    filters += [f"crop=w='trunc(min(iw,ih*{ratio})/2)*2':h='trunc(min(ih,iw/{ratio})/2)*2':x='(iw-ow)*{cx}':y='(ih-oh)*{cy}'",
                                f'scale={w}:{h}']
                    if z0 != 1 or z1 != 1:
                        frames = max(1, round(moving * fps))
                        filters += [f"zoompan=z='{z0}+({z1}-{z0})*min(on/{max(1,frames-1)},1)':x='(iw-iw/zoom)*{cx}':y='(ih-ih/zoom)*{cy}':d=1:s={w}x{h}:fps={fps}"]
                else:
                    raise ValueError('framing deve ser crop ou fit')
                # Reverse/speed first, then FPS so zoompan's one-frame-per-input behavior preserves duration.
                timing = (['reverse'] if reverse else []) + [f'setpts=(PTS-STARTPTS)/{speed}', f'fps={fps}']
                filters = timing + filters
                if freeze:
                    filters.append(f'tpad=stop_mode=clone:stop_duration={freeze}')
                filters += ['setsar=1', 'format=yuv420p']
                # Only real audio is reversed/retimed: the silent stand-in is generated at the final length.
                af = ((['areverse'] if reverse else []) + atempo_chain(speed)) if inf['has_audio'] else []
                af.append(f"volume={number(clip.get('audio_gain_db',0), 'audio_gain_db', lo=-60, hi=12)}dB")
                for mute in clip.get('mute', []):
                    # Mute pairs are seconds within the clip source; convert to output time.
                    a = number(mute[0], 'mute.start', hi=src_duration)
                    b = number(mute[1], 'mute.end', lo=a, hi=src_duration)
                    if reverse:
                        a, b = src_duration - b, src_duration - a
                    af.append(f"volume=0:enable='between(t,{a/speed},{b/speed})'")
                af += ['aresample=48000', 'aformat=channel_layouts=stereo', f'apad=whole_dur={duration}', f'atrim=duration={duration}', 'asetpts=PTS-STARTPTS']
                part = tmp / f'clip-{ci:04}.mkv'; parts.append(part)
                cmd = ['-ss', start, '-t', src_duration, '-i', src]
                if not inf['has_audio']:
                    # Finite silence: an endless source would never let areverse/apad finish.
                    cmd += ['-f', 'lavfi', '-t', duration, '-i', 'anullsrc=r=48000:cl=stereo']
                cmd += ['-t', duration, '-map', '0:v:0', '-map', '0:a:0' if inf['has_audio'] else '1:a:0',
                        '-vf', ','.join(filters), '-af', ','.join(af), '-c:v', 'libx264', '-preset', 'fast', '-crf', '0',
                        '-r', fps, '-c:a', 'pcm_s16le', part]
                run(cmd, args.out / f'{Path(name).stem}-clip-{ci:03}.log')
            if not parts:
                raise ValueError('Timeline vazia')
            concat = tmp / 'concat.txt'
            concat.write_text('\n'.join(f"file '{p.as_posix()}'" for p in parts), encoding='utf-8')
            assembled = tmp / 'assembled.mkv'
            run(['-f','concat','-safe','0','-i',concat,'-c','copy',assembled])
            ass = tmp / 'captions.ass'
            make_ass(ass, output.get('captions', []), w, h, total, args.preview)
            # One input per distinct audio file; asplit feeds every use. Keeps argv short with many SFX.
            inputs = ['-i', assembled]
            # Dialogue (e.g. TTS lines) joins the gameplay sound before the split, so music ducks under it.
            voices = output.get('voice', [])
            graph = []
            for n, row in enumerate(voices, start=1):
                vat = number(row.get('at', 0), 'voice.at', hi=total)
                vgain = number(row.get('gain_db', 0), 'voice.gain_db', lo=-60, hi=12)
                inputs += ['-i', path_at(root, row['file'])]
                graph.append(f'[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vgain}dB,adelay={round(vat*1000)}:all=1[v{n}]')
            if voices:
                graph.append('[0:a]aresample=48000' + f'[g0];[g0]' + ''.join(f'[v{n}]' for n in range(1, len(voices) + 1))
                             + f'amix=inputs={len(voices)+1}:normalize=0:duration=first,asplit=2[base][side]')
            else:
                graph.append('[0:a]aresample=48000,asplit=2[base][side]')
            first = len(voices) + 1
            uses = []
            for kind, rows in [('music', output.get('music', [])), ('sfx', sfx_rows)]:
                for row in rows:
                    file = asset(row['file'])
                    at = number(row.get('at', 0), 'at', hi=total)
                    offset = number(row.get('offset', 0), 'offset', hi=probe(file)['duration']-.02) if kind == 'music' else 0
                    if kind == 'music':
                        length = number(row.get('duration', total-at), 'duration', lo=.02, hi=total-at+.01)
                    elif 'duration' in row:
                        # A sound near the end is simply cut at the end of the video.
                        length = max(.02, min(number(row['duration'], 'duration', lo=.02, hi=60), total - at))
                    else:
                        length = None
                    gain = number(row.get('gain_db', -23 if kind=='music' else -8), 'gain_db', lo=-60, hi=6)
                    if kind == 'sfx':
                        # SFX gain is the desired peak level: quiet and loud library files land alike.
                        gain -= allowed[file].get('peak_db', 0)
                    pitch = number(row.get('pitch', 1), 'pitch', lo=.5, hi=2)
                    uses.append(dict(kind=kind, key=(kind, str(file), offset), file=file, at=at, offset=offset, length=length, gain=gain, pitch=pitch))
            keys = list(dict.fromkeys(u['key'] for u in uses))
            counts = collections.Counter(u['key'] for u in uses)
            for idx, key in enumerate(keys, start=first):
                kind, file, offset = key
                if kind == 'music':
                    inputs += ['-stream_loop', '-1']
                inputs += (['-ss', offset] if offset else []) + ['-i', file]
                label = f'in{idx}'
                if counts[key] > 1:
                    graph.append(f'[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,asplit={counts[key]}' + ''.join(f'[{label}_{n}]' for n in range(counts[key])))
                else:
                    graph.append(f'[{idx}:a]aresample=48000,aformat=channel_layouts=stereo[{label}_0]')
            served = collections.Counter(); music_labels = []; sfx_labels = []
            for n, u in enumerate(uses):
                idx = keys.index(u['key']) + first
                src_label = f'in{idx}_{served[u["key"]]}'; served[u['key']] += 1
                chain = []
                if u['pitch'] != 1:
                    # Varispeed: higher pitch is also shorter, like a cartoon sound.
                    chain += [f'asetrate={round(48000*u["pitch"])}', 'aresample=48000']
                if u['length'] is not None:
                    chain += [f'atrim=duration={u["length"]}', 'asetpts=PTS-STARTPTS', f'volume={u["gain"]}dB',
                              'afade=t=in:d=0.02', f'afade=t=out:st={max(0,u["length"]-.15)}:d=0.15']
                else:
                    chain += ['asetpts=PTS-STARTPTS', f'volume={u["gain"]}dB', 'afade=t=in:d=0.005']
                chain.append(f'adelay={round(u["at"]*1000)}:all=1')
                label = f'u{n}'
                graph.append(f'[{src_label}]' + ','.join(chain) + f'[{label}]')
                (music_labels if u['kind']=='music' else sfx_labels).append(label)
            graph += [''.join(f'[{s}]' for s in music_labels) + f'amix=inputs={len(music_labels)}:normalize=0,apad=whole_dur={total},atrim=duration={total}[music]',
                      '[music][side]sidechaincompress=threshold=0.025:ratio=8:attack=20:release=250[ducked]']
            all_audio = ['base', 'ducked', *sfx_labels]
            graph += [''.join(f'[{s}]' for s in all_audio) + f'amix=inputs={len(all_audio)}:normalize=0:duration=first,atrim=duration={total}[mix]']
            graph_file = tmp / 'graph.txt'; graph_file.write_text(';\n'.join(graph), encoding='utf-8')
            mixed = tmp / 'mixed.wav'
            run([*inputs, '-filter_complex', graph_file.read_text(encoding='utf-8'), '-map', '[mix]', '-vn', '-c:a','pcm_s16le', '-t', total, mixed], args.out / f'{Path(name).stem}-mix.log')
            # Two-pass loudness normalization measures the real mix, rather than guessing from file gain.
            target_i, target_tp = config.get('target_loudness_lufs', -14), config.get('target_true_peak_dbtp', -1.5)
            measured = run(['-i', mixed, '-af', f'loudnorm=I={target_i}:TP={target_tp}:LRA=9:print_format=json', '-f','null','-'])
            stats = json.loads(measured[measured.rfind('{'):measured.rfind('}')+1])
            if all(math.isfinite(float(stats[k])) for k in ['input_i','input_tp','input_lra','input_thresh','target_offset']):
                # AAC encoding adds overshoot; aim the linear pass 0.5 dB below the true-peak target.
                norm = f"loudnorm=I={target_i}:TP={target_tp-.5}:LRA=9:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true"
            else:
                norm = 'alimiter=limit=0.84:level=false'
            final_inputs = ['-i', assembled, '-i', mixed]
            camera = camera_filters(output.get('effects', []), w, h, fps, total)
            video_graph = [f"[0:v]{','.join(camera) if camera else 'null'}[v0]"]
            overlays = output.get('overlays', [])
            for k, overlay in enumerate(overlays):
                file = path_at(root, overlay['file'])
                if file.suffix.lower() != '.png':
                    raise ValueError('Overlay deve ser PNG transparente')
                at = number(overlay['at'], 'overlay.at', hi=total)
                length = number(overlay['duration'], 'overlay.duration', lo=.05, hi=total-at+.05)
                size = round(w * number(overlay.get('width',.2), 'overlay.width', lo=.01, hi=1))
                x = round(w * number(overlay.get('x', .4), 'overlay.x', hi=1))
                y = round(h * number(overlay.get('y', .3), 'overlay.y', hi=1))
                final_inputs += ['-loop','1','-i',file]
                video_graph += [f'[{k+2}:v]scale={size}:-1,format=rgba,trim=duration={length},fade=t=in:d=0.08:alpha=1,fade=t=out:st={max(0,length-.12)}:d=0.12:alpha=1,setpts=PTS-STARTPTS+{at}/TB[o{k}]']
                yexpr = f'{y}+12*sin(6*(t-{at}))' if overlay.get('bob',True) else str(y)
                video_graph += [f"[v{k}][o{k}]overlay=x={x}:y='{yexpr}':enable='between(t,{at},{at+length})':eof_action=pass[v{k+1}]"]
            # Captions go last so stickers and camera moves never cover or shake the text.
            video_graph += [f"[v{len(overlays)}]ass=filename='{filter_path(ass)}':fontsdir='{filter_path(FONTES)}'[vout]"]
            final_graph = tmp / 'video-graph.txt'; final_graph.write_text(';\n'.join(video_graph), encoding='utf-8')
            run([*final_inputs, '-filter_complex', final_graph.read_text(encoding='utf-8'),'-map','[vout]','-map','1:a:0',
                 '-af', norm,
                 '-c:v','libx264','-crf',str(output.get('crf',16)),'-preset','medium',
                 '-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-b:a','320k',
                 '-t',total,'-movflags','+faststart',dest], args.out / f'{Path(name).stem}-export.log')
        actual = probe(dest)
        if abs(actual['duration'] - total) > .25:
            raise ValueError(f'Duracao exportada inesperada: {dest}')
        if (actual['width'], actual['height']) != (w, h) or not actual['has_audio'] or abs(actual['fps']-fps) > .1:
            raise ValueError(f'Formato exportado inesperado: {actual}')
        # Decode the complete output; a header-only check does not catch broken frames.
        run(['-v','error','-i',dest,'-f','null','-'], args.out / f'{Path(name).stem}-decode.log')
        (args.out / f'{Path(name).stem}-creditos.txt').write_text('\n'.join(credits), encoding='utf-8')
        sfx_files = collections.Counter(Path(r['file']).name for r in sfx_rows)
        completed.append({'file':name,'format':output['format'],'duration':actual['duration'],
                          'width':actual['width'],'height':actual['height'],
                          'source_resolution':[native['width'],native['height']],
                          'resolution_policy':'source-native-tier','fps':actual['fps'],
                          'sfx_total':len(sfx_rows),'sfx_por_minuto':round(len(sfx_rows)/max(total,1)*60,1),
                          'sfx_distintos':len(sfx_files),'sfx_mais_repetido':sfx_files.most_common(1),
                          'efeitos_visuais':len(output.get('effects', [])),
                          'legendas':len(output.get('captions', [])),'stickers':len(output.get('overlays', [])),
                          'preview':args.preview,'audio_licenses_checked':not args.preview,
                          'visual_review':'pending','source_video_rights':'user_to_verify'})
        print(f'Exportado: {dest}', flush=True)
        if not args.preview:
            history_file=lib/'historico-musicas.json'
            history=json.loads(history_file.read_text(encoding='utf-8')) if history_file.exists() else []
            titles=list(dict.fromkeys(allowed[path_at(lib,row['file'])]['title'] for row in output['music']))
            history.append({'output':name,'titles':titles})
            history_file.write_text(json.dumps(history[-200:],ensure_ascii=False,indent=2),encoding='utf-8')
    (args.out / 'relatorio-render.json').write_text(json.dumps(completed, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
