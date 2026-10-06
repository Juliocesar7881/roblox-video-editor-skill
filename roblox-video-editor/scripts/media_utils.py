from pathlib import Path
import json, os, re, shutil, subprocess

def ffmpeg():
    exe = os.environ.get('FFMPEG_BINARY') or shutil.which('ffmpeg')
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit('Instale FFmpeg ou: python -m pip install imageio-ffmpeg')

def run(args, log=None):
    result = subprocess.run([ffmpeg(), '-hide_banner', '-nostdin', '-y', *map(str, args)], capture_output=True)
    stderr = result.stderr.decode('utf-8', 'replace')
    if log:
        Path(log).write_text(stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(stderr[-6000:])
    return stderr

def probe(path):
    tool = shutil.which('ffprobe')
    if tool:
        p = subprocess.run([tool, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], capture_output=True, check=True)
        j = json.loads(p.stdout)
        video = next((s for s in j['streams'] if s['codec_type'] == 'video'), {})
        num, den = map(float, video.get('avg_frame_rate', '0/1').split('/'))
        return {'duration': float(j['format']['duration']), 'width': video.get('width'),
                'height': video.get('height'), 'fps': num / den if den else 0,
                'has_audio': any(s['codec_type'] == 'audio' for s in j['streams']), 'raw': j}
    p = subprocess.run([ffmpeg(), '-hide_banner', '-i', str(path)], capture_output=True)
    s = p.stderr.decode('utf-8', 'replace')
    duration = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', s)
    size = re.search(r'Video:.*?(\d{2,5})x(\d{2,5})', s)
    fps = re.search(r'(\d+(?:\.\d+)?) fps', s)
    if not duration:
        raise ValueError(f'Nao foi possivel ler: {path}\n{s[-2000:]}')
    h, m, sec = map(float, duration.groups())
    return {'duration': h * 3600 + m * 60 + sec, 'width': int(size[1]) if size else None,
            'height': int(size[2]) if size else None, 'fps': float(fps[1]) if fps else 0,
            'has_audio': 'Audio:' in s}

def filter_path(path):
    # FFmpeg filter quoting is independent of the subprocess argv quoting.
    # Special names are handled by staging filter files in a simple-name working directory.
    return str(Path(path).resolve()).replace('\\', '/').replace(':', '\\:').replace("'", "'\\''")
