"""Render an agent-authored edit decision list with FFmpeg. No automatic semantic editing."""
import argparse, hashlib, json, math, shutil, tempfile
from pathlib import Path
from media_utils import probe, run, filter_path

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

def make_ass(path, captions, w, h, total, preview):
    fs = round(w * .058) if h > w else round(h * .065)
    # All text is supplied as data. Escape ASS syntax and strip control codes.
    header = f'''[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,Arial,{fs},&H00FFFFFF,&H000000FF,&H00101010,&H60000000,-1,0,0,0,100,100,0,0,1,3,1,2,{int(w*.12)},{int(w*.16)},{int(h*.23)},1
Style: Preview,Arial,{int(fs*.5)},&H0060FFFF,&H000000FF,&H00101010,&H60000000,0,0,0,0,100,100,0,0,1,2,0,8,10,10,10,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
    lines = []
    for c in captions:
        start = number(c['start'], 'caption.start', hi=total)
        end = number(c['end'], 'caption.end', lo=start+.01, hi=total)
        text = str(c['text']).replace('\\', '＼').replace('{', '(').replace('}', ')')
        text = ''.join(ch for ch in text if ord(ch) >= 32 or ch == '\n').replace('\n', r'\N')
        animation = r'{\fad(60,80)\fscx90\fscy90\t(0,120,\fscx100\fscy100)}'
        lines.append(f'Dialogue: 0,{ass_time(start)},{ass_time(end)},Main,,0,0,0,,{animation}{text}')
    if preview:
        lines.append(f'Dialogue: 1,0:00:00.00,{ass_time(total)},Preview,,0,0,0,,PREVIA - LICENCAS PENDENTES')
    path.write_text(header + '\n'.join(lines) + '\n', encoding='utf-8-sig')

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
    def asset(name):
        p = path_at(lib, name)
        a = allowed.get(p)
        if not a:
            raise ValueError(f'Audio ausente no catalogo: {p}')
        if hashlib.sha256(p.read_bytes()).hexdigest() != a['sha256']:
            raise ValueError(f'Audio mudou desde a verificacao: {p}')
        if not args.preview and not a.get('commercial_allowed'):
            raise ValueError(f'Licenca comercial nao comprovada: {p}. Use alternativa original ou gere --preview.')
        if a.get('attribution') and a['attribution'] not in credits:
            credits.append(a['attribution'])
        return p
    outputs = spec['outputs']
    kinds = [o['format'] for o in outputs]
    if kinds.count('long') < 1 or kinds.count('short') < 2:
        raise ValueError('A entrega deve ter um longo e pelo menos dois Shorts.')
    reference=spec.get('primary_source') or next(o for o in outputs if o['format']=='long')['clips'][0]['source']
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
        # Validate licensing before potentially expensive video encoding.
        for audio in [*output.get('music', []), *output.get('sfx', [])]:
            asset(audio['file'])
        with tempfile.TemporaryDirectory(prefix='roblox-edit-') as td:
            tmp = Path(td)
            parts = []; total = 0.0
            for ci, clip in enumerate(output['clips']):
                src = path_at(root, clip['source'])
                inf = probe(src)
                start = number(clip['in'], 'in', hi=inf['duration'])
                end = number(clip['out'], 'out', lo=start+.02, hi=inf['duration']+.01)
                duration = end - start
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
                        frames = max(1, round(duration * fps))
                        filters += [f"zoompan=z='{z0}+({z1}-{z0})*min(on/{max(1,frames-1)},1)':x='(iw-iw/zoom)*{cx}':y='(ih-ih/zoom)*{cy}':d=1:s={w}x{h}:fps={fps}"]
                else:
                    raise ValueError('framing deve ser crop ou fit')
                # FPS before zoompan ensures its one-frame-per-input behavior preserves duration.
                filters.insert(0, f'fps={fps}')
                filters += ['setsar=1', 'format=yuv420p']
                af = [f"volume={number(clip.get('audio_gain_db',0), 'audio_gain_db', lo=-60, hi=12)}dB"]
                for mute in clip.get('mute', []):
                    a = number(mute[0], 'mute.start', hi=duration)
                    b = number(mute[1], 'mute.end', lo=a, hi=duration)
                    af.append(f"volume=0:enable='between(t,{a},{b})'")
                af += ['aresample=48000', 'aformat=channel_layouts=stereo', f'apad=whole_dur={duration}', f'atrim=duration={duration}', 'asetpts=PTS-STARTPTS']
                part = tmp / f'clip-{ci:04}.mkv'; parts.append(part)
                cmd = ['-ss', start, '-i', src]
                if not inf['has_audio']:
                    cmd += ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
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
            inputs = ['-i', assembled]
            graph = ['[0:a]aresample=48000,asplit=2[base][side]']
            index = 1; music_labels = []; sfx_labels = []
            for kind in ['music', 'sfx']:
                for row in output.get(kind, []):
                    file = asset(row['file'])
                    at = number(row.get('at', 0), 'at', hi=total)
                    offset = number(row.get('offset', 0), 'offset', hi=probe(file)['duration']-.02)
                    length = number(row.get('duration', total-at), 'duration', lo=.02, hi=total-at+.01)
                    gain = number(row.get('gain_db', -23 if kind=='music' else -12), 'gain_db', lo=-60, hi=6)
                    if kind == 'music':
                        inputs += ['-stream_loop', '-1']
                    inputs += ['-ss', offset, '-i', file]
                    label = f'{kind}{index}'
                    graph.append(f'[{index}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={length},asetpts=PTS-STARTPTS,volume={gain}dB,afade=t=in:d=0.02,afade=t=out:st={max(0,length-.15)}:d=0.15,adelay={round(at*1000)}:all=1[{label}]')
                    (music_labels if kind=='music' else sfx_labels).append(label)
                    index += 1
            graph += [''.join(f'[{s}]' for s in music_labels) + f'amix=inputs={len(music_labels)}:normalize=0,apad=whole_dur={total},atrim=duration={total}[music]',
                      '[music][side]sidechaincompress=threshold=0.025:ratio=8:attack=20:release=250[ducked]']
            all_audio = ['base', 'ducked', *sfx_labels]
            graph += [''.join(f'[{s}]' for s in all_audio) + f'amix=inputs={len(all_audio)}:normalize=0:duration=first,atrim=duration={total}[mix]']
            graph_file = tmp / 'graph.txt'; graph_file.write_text(';\n'.join(graph), encoding='utf-8')
            mixed = tmp / 'mixed.wav'
            run([*inputs, '-filter_complex_script', graph_file, '-map', '[mix]', '-vn', '-c:a','pcm_s16le', '-t', total, mixed], args.out / f'{Path(name).stem}-mix.log')
            # Two-pass loudness normalization measures the real mix, rather than guessing from file gain.
            measured = run(['-i', mixed, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json', '-f','null','-'])
            stats = json.loads(measured[measured.rfind('{'):measured.rfind('}')+1])
            if all(math.isfinite(float(stats[k])) for k in ['input_i','input_tp','input_lra','input_thresh','target_offset']):
                norm = f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true"
            else:
                norm = 'alimiter=limit=0.84:level=false'
            final_inputs = ['-i', assembled, '-i', mixed]
            video_graph = [f"[0:v]ass=filename='{filter_path(ass)}'[v0]"]
            overlays = output.get('overlays', [])
            for k, overlay in enumerate(overlays):
                file = path_at(root, overlay['file'])
                if file.suffix.lower() != '.png':
                    raise ValueError('Overlay deve ser PNG transparente')
                at = number(overlay['at'], 'overlay.at', hi=total)
                length = number(overlay['duration'], 'overlay.duration', lo=.05, hi=total-at)
                size = round(w * number(overlay.get('width',.2), 'overlay.width', lo=.01, hi=1))
                x = round(w * number(overlay.get('x', .4), 'overlay.x', hi=1))
                y = round(h * number(overlay.get('y', .3), 'overlay.y', hi=1))
                final_inputs += ['-loop','1','-i',file]
                video_graph += [f'[{k+2}:v]scale={size}:-1,format=rgba,trim=duration={length},fade=t=in:d=0.08:alpha=1,fade=t=out:st={max(0,length-.12)}:d=0.12:alpha=1,setpts=PTS-STARTPTS+{at}/TB[o{k}]']
                yexpr = f'{y}+12*sin(6*(t-{at}))' if overlay.get('bob',True) else str(y)
                video_graph += [f"[v{k}][o{k}]overlay=x={x}:y='{yexpr}':enable='between(t,{at},{at+length})':eof_action=pass[v{k+1}]"]
            final_graph = tmp / 'video-graph.txt'; final_graph.write_text(';\n'.join(video_graph), encoding='utf-8')
            run([*final_inputs, '-filter_complex_script',final_graph,'-map',f'[v{len(overlays)}]','-map','1:a:0',
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
        completed.append({'file':name,'format':output['format'],'duration':actual['duration'],
                          'width':actual['width'],'height':actual['height'],
                          'source_resolution':[native['width'],native['height']],
                          'resolution_policy':'source-native-tier','fps':actual['fps'],
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
