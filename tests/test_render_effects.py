"""End-to-end render of a tiny synthetic gameplay using every exaggerated-editing feature."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'roblox-video-editor'
sys.path.insert(0,str(SKILL/'scripts'))

def ffmpeg_or_none():
 try:
  from media_utils import ffmpeg
  return ffmpeg()
 except (SystemExit, ImportError):
  return None

@unittest.skipIf(ffmpeg_or_none() is None,'FFmpeg indisponivel')
class RenderEffects(unittest.TestCase):
 def test_exaggerated_timeline_renders(self):
  ff=ffmpeg_or_none(); lib=SKILL/'assets/biblioteca-audio'; ov=SKILL/'assets/overlays'
  with tempfile.TemporaryDirectory() as td:
   td=Path(td); src=td/'g.mp4'
   subprocess.run([ff,'-v','error','-y','-f','lavfi','-i','testsrc2=s=320x180:r=30:d=6','-pix_fmt','yuv420p',str(src)],check=True)
   soco='efeitos/capcut-convertidos/em mp3-3.mp3'; imp='efeitos/capcut-convertidos/em mp3-7.mp3'
   def out(name,fmt):
    return {'name':name,'format':fmt,
     'clips':[{'source':'g.mp4','in':0,'out':2},{'source':'g.mp4','in':2,'out':3,'freeze':.5},
              {'source':'g.mp4','in':2,'out':3,'speed':.5,'zoom':[1,1.2]},{'source':'g.mp4','in':3,'out':4,'reverse':True}],
     'music':[{'file':'musicas/curtos/hyperfun-short.mp3','gain_db':-18}],
     'sfx':[{'file':soco,'at':.5,'gain_db':-5,'pitch':1.2},{'file':soco,'at':1.0,'gain_db':-5}],
     'effects':[{'type':'punch','at':.5},{'type':'shake','at':1.0},{'type':'flash','at':2.4},{'type':'zoom','at':3,'duration':1,'sfx':imp}],
     'captions':[{'start':0,'end':1,'text':'POW!','style':'grito','sfx':'efeitos/capcut-convertidos/eem mp3-18.mp3'},
                 {'start':2.5,'end':4.4,'text':'REPLAY','style':'titulo','color':'amarelo'}],
     'overlays':[{'file':str(ov/'pow.png'),'at':.5,'duration':.6,'x':.5,'y':.1,'width':.3,'sfx':imp}]}
   spec={'library':str(lib),'outputs':[out('l.mp4','long'),out('s1.mp4','short'),out('s2.mp4','short')]}
   (td/'t.json').write_text(json.dumps(spec),encoding='utf-8')
   r=subprocess.run([sys.executable,str(SKILL/'scripts/renderizar.py'),str(td/'t.json'),'--out',str(td/'o')],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr[-3000:])
   rep=json.loads((td/'o'/'relatorio-render.json').read_text(encoding='utf-8'))
   self.assertEqual([x['file'] for x in rep],['l.mp4','s1.mp4','s2.mp4'])
   # 2 + 0.5 freeze + 1 + 2 (half speed) + 1 = 6.5 s
   self.assertAlmostEqual(rep[0]['duration'],6.5,delta=.25)
   self.assertEqual((rep[1]['width'],rep[1]['height']),(180,320))
   self.assertEqual(rep[0]['sfx_total'],5)
   self.assertEqual(rep[0]['efeitos_visuais'],4)

 def test_animated_short_with_voice_and_highlight(self):
  ff=ffmpeg_or_none(); lib=SKILL/'assets/biblioteca-audio'
  with tempfile.TemporaryDirectory() as td:
   td=Path(td)
   subprocess.run([ff,'-v','error','-y','-f','lavfi','-i','testsrc2=s=320x180:r=30:d=4','-pix_fmt','yuv420p',str(td/'cena.mp4')],check=True)
   subprocess.run([ff,'-v','error','-y','-f','lavfi','-i','sine=f=300:d=1.2',str(td/'fala-01.wav')],check=True)
   spec={'library':str(lib),'entrega':'shorts','outputs':[{'name':'anim.mp4','format':'short',
     'clips':[{'source':'cena.mp4','in':0,'out':4}],
     'music':[{'file':'musicas/curtos/hyperfun-short.mp3','gain_db':-18}],
     'voice':[{'file':'fala-01.wav','at':0.5}],
     'captions':[{'start':0.5,'end':1.7,'text':'QUAL É O *MAIS RÁPIDO*?','style':'legenda'}]}]}
   (td/'t.json').write_text(json.dumps(spec),encoding='utf-8')
   r=subprocess.run([sys.executable,str(SKILL/'scripts/renderizar.py'),str(td/'t.json'),'--out',str(td/'o')],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr[-3000:])
   rep=json.loads((td/'o'/'relatorio-render.json').read_text(encoding='utf-8'))
   self.assertEqual([x['file'] for x in rep],['anim.mp4'])
   self.assertAlmostEqual(rep[0]['duration'],4,delta=.25)
   # A long output is rejected in shorts mode.
   spec['outputs'][0]['format']='long'
   (td/'t.json').write_text(json.dumps(spec),encoding='utf-8')
   r=subprocess.run([sys.executable,str(SKILL/'scripts/renderizar.py'),str(td/'t.json'),'--out',str(td/'o2')],capture_output=True,text=True)
   self.assertNotEqual(r.returncode,0)

if __name__=='__main__':unittest.main()
