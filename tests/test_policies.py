import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'roblox-video-editor'
sys.path.insert(0,str(SKILL/'scripts'))
from renderizar import native_resolution

class Policies(unittest.TestCase):
 def test_native_dimensions(self):
  for w,h in [(1280,720),(1920,1080),(2560,1440),(3840,2160)]:
   self.assertEqual(native_resolution({'width':w,'height':h},False),(w,h))
   self.assertEqual(native_resolution({'width':w,'height':h},True),(h,w))

 def test_unsupported_odd_dimensions(self):
  with self.assertRaises(ValueError):native_resolution({'width':1919,'height':1080},False)

 def test_public_manifest(self):
  rows=json.loads((SKILL/'assets/audio-manifest.json').read_text(encoding='utf-8'))['assets']
  self.assertEqual(len(rows),78)
  self.assertTrue(all(r['commercial_allowed'] and r['distribution_allowed'] for r in rows))
  full=[r for r in rows if r.get('version')=='full']
  self.assertEqual(len(full),36)
  self.assertTrue(all(r['license']=='CC BY 4.0' and r['attribution_required'] for r in full))
  self.assertTrue(all(r['download_url'].startswith('https://incompetech.com/') for r in full))
  self.assertFalse(any('fornecidas' in r['path'] or 'fornecidos' in r['path'] for r in rows))

 def test_rotation_counts_same_title_across_formats(self):
  with tempfile.TemporaryDirectory() as td:
   lib=Path(td)
   rows=[{'type':'music','commercial_allowed':True,'version':'full','title':title,'path':title+'.mp3','mood':'comedia'} for title in ['A','B','C']]
   (lib/'catalogo.json').write_text(json.dumps({'assets':rows}),encoding='utf-8')
   (lib/'historico-musicas.json').write_text(json.dumps([{'output':'short.mp4','titles':['A']}]),encoding='utf-8')
   result=subprocess.check_output([sys.executable,str(SKILL/'scripts/selecionar_musicas.py'),'--library',str(lib),'--count','3'])
   order=json.loads(result)
   self.assertEqual(order[-1]['title'],'A')
   self.assertEqual(order[-1]['prior_uses'],1)

if __name__=='__main__':unittest.main()
