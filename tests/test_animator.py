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
        grupos = [c['text'].replace('*', '') for c in caps if c.get('entrada')]
        self.assertEqual(grupos, ['MANO,', 'OLHA O TAMANHO', 'DESSE OVO!'])
        self.assertEqual(caps[2]['text'], 'OLHA *O* TAMANHO')
        self.assertTrue(all(c['style'] == 'karaoke' for c in caps))
        self.assertTrue(all(a['end'] <= b['start'] + 1e-6 for a, b in zip(caps, caps[1:])))

    def test_karaoke_style_uses_bundled_font(self):
        from renderizar import make_ass, FONTES
        self.assertTrue((FONTES / 'LilitaOne-Regular.ttf').is_file())
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'k.ass'
            make_ass(p, [{'start': 0, 'end': 1, 'text': 'TAMANHO *DESSE* OVO!', 'style': 'karaoke', 'entrada': True}], 1080, 1920, 2, False)
            t = p.read_text(encoding='utf-8-sig')
            self.assertIn('Style: karaoke,Lilita One', t)
            self.assertIn('&H004FE5FF&}DESSE', t)
            self.assertIn(r'\yshad', t)

    def test_animkit_audits_and_hides_cursor(self):
        kit = (ANIM / 'luau' / 'AnimKit.lua').read_text(encoding='utf-8')
        for api in ('function AnimKit.auditar', 'GetPartsInPart', 'MouseIconEnabled = false',
                    'model.PrimaryPart = model.HumanoidRootPart', 'function AnimKit.preCarregar', 'function AnimKit.sentarEm'):
            self.assertIn(api, kit)

    def test_karaoke_one_idea_at_a_time(self):
        ws = 'O vermelho, o azul... ou o amarelo gigante?'.split()
        f = [{'id': '1', 'palavras': [{'w': w, 'start': i * .3, 'end': i * .3 + .25} for i, w in enumerate(ws)]}]
        grupos = [c['text'].replace('*', '') for c in legendas_karaoke(f, {'1': 0}) if c.get('entrada')]
        self.assertEqual(grupos, ['O VERMELHO,', 'O AZUL...', 'OU O AMARELO GIGANTE?'])
        numeros = legendas_karaoke([{'id': '2', 'palavras': [{'w': '5,', 'start': 0, 'end': .3}, {'w': 'não!', 'start': .5, 'end': .8}]}], {'2': 0})
        self.assertEqual([c['highlight'] for c in numeros if '*' in c['text']], ['ciano', 'coral'])

    @unittest.skipIf(ffmpeg_or_none() is None, 'FFmpeg indisponivel')
    def test_mouth_envelope_follows_voice(self):
        from envelope_boca import envelope
        ff = ffmpeg_or_none()
        with tempfile.TemporaryDirectory() as td:
            wav = Path(td) / 'v.wav'
            # 0,5 s de silencio, 0,5 s de "voz", 0,5 s de silencio.
            subprocess.run([ff, '-v', 'error', '-y', '-f', 'lavfi', '-i',
                            "aevalsrc='if(between(t,0.5,1),0.5*sin(2*PI*220*t),0)':d=1.5:s=16000", str(wav)], check=True)
            env = envelope(wav, 30)
            self.assertAlmostEqual(len(env), 45, delta=1)
            self.assertTrue(all(c in '0123456789' for c in env))
            self.assertLessEqual(max(map(int, env[:12])), 1)
            self.assertGreaterEqual(min(map(int, env[18:27])), 7)
            self.assertLessEqual(max(map(int, env[-10:])), 1)

    def test_karaoke_never_overlaps_or_flickers(self):
        # Tempos reais do piloto: "o" e "mais" duram menos de 0,1 s (o destaque piscava) e o grupo seguinte
        # comecava antes do anterior sumir (duas linhas na tela).
        ws = [('Qual', .0, .26), ('escorregador', .26, .94), ('é', .94, 1.0), ('o', 1.0, 1.06), ('mais', 1.12, 1.3),
              ('rápido?', 1.3, 1.64), ('O', 2.39, 2.61), ('vermelho,', 2.61, 3.57)]
        f = [{'id': '1', 'palavras': [{'w': w, 'start': a, 'end': b} for w, a, b in ws]}]
        caps = legendas_karaoke(f, {'1': 0.3})
        self.assertTrue(all(a['end'] <= b['start'] + 1e-6 for a, b in zip(caps, caps[1:])))
        self.assertTrue(all(c['end'] - c['start'] >= .16 for c in caps if '*' in c['text']))
        textos = [c['text'] for c in caps]
        self.assertIn('*É O MAIS* RÁPIDO?', textos)  # "é o" (0,12 s) acende junto com "mais", sem piscar
        self.assertNotIn('É *O* MAIS RÁPIDO?', textos)
        for g in [c for c in caps if c.get('entrada')]:
            self.assertEqual(g['text'].count('*'), 2)

    @unittest.skipIf(ffmpeg_or_none() is None, 'FFmpeg indisponivel')
    def test_caption_review_finds_overlap_flicker_and_stacking(self):
        from revisar_legendas import revisar
        with tempfile.TemporaryDirectory() as td:
            spec = Path(td) / 't.json'

            def checar(caps, overlays=()):
                out = {'name': 'x.mp4', 'format': 'short', 'resolution': [540, 960], 'clips': [],
                       'captions': caps, 'overlays': list(overlays)}
                spec.write_text(json.dumps({'outputs': [out]}), encoding='utf-8')
                return revisar(spec, fps=10)

            boas = legendas_karaoke([{'id': '1', 'palavras': [{'w': w, 'start': i * .4, 'end': i * .4 + .35}
                                                               for i, w in enumerate('Agora vai, eu acho!'.split())]}], {'1': 0})
            self.assertEqual(checar(boas), [])
            ruins = [{'start': 0, 'end': 1.2, 'text': 'UÉ...', 'style': 'karaoke'},
                     {'start': 1.0, 'end': 2.0, 'text': 'TRAVEI?', 'style': 'karaoke'},
                     {'start': 2.0, 'end': 2.06, 'text': '*TÁ* BOM', 'style': 'karaoke'},
                     # texto longo demais quebra em duas linhas
                     {'start': 3.0, 'end': 3.6, 'text': 'ESSE TEXTO E LONGO DEMAIS PARA UMA LINHA SO', 'style': 'legenda'}]
            problemas = ' | '.join(checar(ruins, [{'file': 'contagem-5.png', 'at': 1.5, 'duration': 1, 'y': .6}]))
            for trecho in ('sobrepostas', 'pisca', 'linhas de legenda ao mesmo tempo', 'na faixa da legenda'):
                self.assertIn(trecho, problemas)

    @unittest.skipIf(ffmpeg_or_none() is None, 'FFmpeg indisponivel')
    def test_slide_squeak_lands_on_the_stop(self):
        import numpy as np
        ff = ffmpeg_or_none()
        sons = ROOT / 'roblox-video-editor' / 'assets' / 'audio-original'

        def nivel(arquivo, a, b):
            raw = subprocess.run([ff, '-v', 'error', '-i', str(arquivo), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'],
                                 capture_output=True, check=True).stdout
            x = np.frombuffer(raw, np.float32)
            return 20 * np.log10(np.sqrt(np.mean(x[int(a * 16000):int(b * 16000)] ** 2)) + 1e-9)

        trava = sons / 'escorregar-trava.mp3'
        # Atrito durante 2 s, rangido no fim e silencio depois: o mesmo tempo do K.deslizar de 2,0 s.
        self.assertGreater(nivel(trava, .3, 1.7), -30)
        self.assertGreater(nivel(trava, 1.86, 1.99), -25)
        self.assertLess(nivel(trava, 2.06, 2.2), nivel(trava, .3, 1.7) - 30)
        rapido = sons / 'escorregar-rapido.mp3'
        self.assertGreater(nivel(rapido, 1.8, 2.1), nivel(rapido, .1, .4))  # acelera ate o lancamento
        self.assertGreater(nivel(rapido, 2.25, 2.45), -30)  # lufada de ar logo depois dos 2,2 s

    @unittest.skipIf(ffmpeg_or_none() is None, 'FFmpeg indisponivel')
    def test_camera_audit_maps_viewport_like_the_capture(self):
        # A auditoria de camera (AnimKit.noVideo) tem de achar no video final o mesmo lugar que
        # captura_janela.processar produz: corte da faixa de cima, transpose=2 e corte 9:16 central.
        import numpy as np
        from captura_janela import processar
        kit = (ANIM / 'luau' / 'AnimKit.lua').read_text(encoding='utf-8')
        for trecho in ('x, y, largo, alto = p.Y - corte, vp.X - p.X, vp.Y - corte, vp.X',
                       'if alto * 9 >= largo * 16 then th = largo * 16 / 9 else tw = alto * 9 / 16 end',
                       'AnimKit.MARGEM_TOPO = 0.075', '"rosto na faixa da legenda"', '"rosto cortado na borda"',
                       'BindToRenderStep(NOME, Enum.RenderPriority.Camera.Value + 2'):
            self.assertIn(trecho, kit)

        def no_video(px, py, vx, vy, margem=.075):
            corte = vy * margem
            x, y, largo, alto = py - corte, vx - px, vy - corte, vx
            tw, th = largo, alto
            if alto * 9 >= largo * 16:
                th = largo * 16 / 9
            else:
                tw = alto * 9 / 16
            return (x - (largo - tw) / 2) / tw, (y - (alto - th) / 2) / th

        ff = ffmpeg_or_none()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            subprocess.run([ff, '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1578x864:r=30:d=1.5',
                            '-vf', 'drawbox=x=1090:y=290:w=20:h=20:color=white:t=fill', '-pix_fmt', 'yuv420p',
                            str(td / 'viewport.mp4')], check=True)
            processar(td / 'viewport.mp4', td / 'cena.mp4', 0.2, 1.0, fps=30)
            raw = subprocess.run([ff, '-v', 'error', '-i', str(td / 'cena.mp4'), '-frames:v', '1', '-f', 'rawvideo',
                                  '-pix_fmt', 'gray', '-'], capture_output=True, check=True).stdout
            q = np.frombuffer(raw, np.uint8).reshape(1920, 1080)
            ys, xs = np.nonzero(q > 128)
            fx, fy = no_video(1100, 300, 1578, 864)
            self.assertAlmostEqual(xs.mean() / 1080, fx, delta=.01)
            self.assertAlmostEqual(ys.mean() / 1920, fy, delta=.01)

    def test_animkit_r15_pack_and_lipsync(self):
        kit = (ANIM / 'luau' / 'AnimKit.lua').read_text(encoding='utf-8')
        for trecho in ('HumanoidRigType.R15', 'idle = 742637544', 'correr = 742638842', 'function AnimKit.falar',
                       'function AnimKit.auditarCamera', 'function AnimKit.inserto', 'AnimationConstraint',
                       'sentadoReto', 'HeadScale'):
            self.assertIn(trecho, kit)
        self.assertNotIn('__mode', kit)  # tabelas fracas perdiam animacoes e poses no Roblox


if __name__ == '__main__':
    unittest.main()
