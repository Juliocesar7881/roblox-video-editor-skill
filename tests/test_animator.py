"""Animator helpers: window-capture post-processing, Studio pipeline, captions and TTS timing."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANIM = ROOT / 'roblox-shorts-animator'
sys.path.insert(0, str(ANIM / 'scripts'))
sys.path.insert(0, str(ROOT / 'roblox-video-editor' / 'scripts'))
from legendas import legendas_falas, legendas_karaoke
from tts_elevenlabs import words_from_alignment
import studio_runscript


def ffmpeg_or_none():
    try:
        from media_utils import ffmpeg
        return ffmpeg()
    except (SystemExit, ImportError):
        return None


class Animator(unittest.TestCase):
    def test_words_from_alignment(self):
        text = 'Ué, travei?'
        al = {'characters': list(text), 'character_start_times_seconds': [i * .1 for i in range(len(text))],
              'character_end_times_seconds': [i * .1 + .1 for i in range(len(text))]}
        w = words_from_alignment(al)
        self.assertEqual([x['w'] for x in w], ['Ué,', 'travei?'])
        self.assertAlmostEqual(w[1]['start'], .4)

    def test_caption_groups_and_highlight(self):
        f = [{'id': '01', 'palavras': [{'w': w, 'start': i * .3, 'end': i * .3 + .25}
                                       for i, w in enumerate('O vermelho, o azul ou o amarelo?'.split())]}]
        caps = legendas_falas(f, {'01': 10.0}, ['vermelho', 'amarelo'])
        self.assertTrue(all(c['style'] == 'legenda' for c in caps))
        self.assertEqual(caps[0]['text'], 'O *VERMELHO,*')
        self.assertAlmostEqual(caps[0]['start'], 10.0)
        self.assertTrue(all(a['end'] <= b['start'] + 1e-6 for a, b in zip(caps, caps[1:])))

    def test_pipeline_script_installs_kit_scene_and_play(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / 'cena.lua').write_text('print("]]") -- texto com ]] e ]=] para testar o literal\n', encoding='utf-8')
            (td / 'cenario.lua').write_text('print("cenario")\n', encoding='utf-8')
            saida = td / 'pipeline.lua'
            ns = type('A', (), {'kit': True, 'cenario': td / 'cenario.lua', 'cena': td / 'cena.lua',
                                'play': True, 'timeout': 60, 'saida': saida})
            studio_runscript.montar(ns)
            src = saida.read_text(encoding='utf-8')
            self.assertIn('ModuleScript', src)
            self.assertIn('ExecutePlayModeAsync', src)
            self.assertIn('AnimKitFim', src)
            self.assertIn('task.wait(4)', src)  # Play logo apos abrir o place encerra sozinho
            # The scene source must survive inside a long-bracket literal untouched.
            self.assertIn('print("]]") -- texto com ]] e ]=] para testar o literal', src)
            self.assertIn('[==[', src)

    def test_animkit_keeps_feet_on_marked_floors(self):
        kit = (ANIM / 'luau' / 'AnimKit.lua').read_text(encoding='utf-8')
        for api in ('function AnimKit.chao', 'function AnimKit.emPe', 'function AnimKit.deitado', 'function AnimKit.piso',
                    'RaycastFilterType.Include', 'ALTURA_SENTADO', 'function cam.rosto', 'function AnimKit.poeira'):
            self.assertIn(api, kit)

    @unittest.skipIf(ffmpeg_or_none() is None, 'FFmpeg indisponivel')
    def test_viewport_capture_becomes_vertical_clip(self):
        ff = ffmpeg_or_none()
        from captura_janela import processar
        from media_utils import probe
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            # Landscape viewport (the AnimKit films with the camera rolled 90 degrees).
            subprocess.run([ff, '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=s=1280x720:r=60:d=3',
                            '-pix_fmt', 'yuv420p', str(td / 'viewport.mp4')], check=True)
            processar(td / 'viewport.mp4', td / 'cena.mp4', 0.8, 1.5)
            info = probe(td / 'cena.mp4')
            self.assertEqual((info['width'], info['height']), (1080, 1920))
            self.assertAlmostEqual(info['duration'], 1.5, delta=.1)
            self.assertAlmostEqual(info['fps'], 60, delta=.5)

    def test_karaoke_groups_like_reference(self):
        f = [{'id': '01', 'palavras': [{'w': w, 'start': i * .35, 'end': i * .35 + .3}
                                       for i, w in enumerate('Mano, olha o tamanho desse ovo!'.split())]}]
        caps = legendas_karaoke(f, {'01': 1.0})
        self.assertEqual([c['text'] for c in caps[:4]],
                         ['*MANO,* OLHA O', 'MANO, *OLHA* O', 'MANO, OLHA *O*', '*TAMANHO* DESSE OVO!'])
        self.assertEqual([bool(c.get('entrada')) for c in caps], [True, False, False, True, False, False])
        self.assertTrue(all(c['style'] == 'karaoke' for c in caps))
        self.assertTrue(all(a['end'] <= b['start'] + 1e-6 for a, b in zip(caps, caps[1:])))

    def test_karaoke_style_uses_bundled_font(self):
        from renderizar import make_ass, FONTES
        self.assertTrue((FONTES / 'FredokaOne-Regular.ttf').is_file())
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'k.ass'
            make_ass(p, [{'start': 0, 'end': 1, 'text': 'TAMANHO *DESSE* OVO!', 'style': 'karaoke', 'entrada': True}], 1080, 1920, 2, False)
            t = p.read_text(encoding='utf-8-sig')
            self.assertIn('Style: karaoke,Fredoka One', t)
            self.assertIn('&H0050E2FF&}DESSE', t)
            self.assertIn('\fad(90,0)', t)

    def test_animkit_audits_and_hides_cursor(self):
        kit = (ANIM / 'luau' / 'AnimKit.lua').read_text(encoding='utf-8')
        for api in ('function AnimKit.auditar', 'GetPartsInPart', 'MouseIconEnabled = false',
                    'model.PrimaryPart = model.HumanoidRootPart', 'function AnimKit.preCarregar', 'function AnimKit.sentarEm'):
            self.assertIn(api, kit)


if __name__ == '__main__':
    unittest.main()
