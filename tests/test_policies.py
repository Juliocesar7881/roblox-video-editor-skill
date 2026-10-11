import hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'roblox-video-editor'
sys.path.insert(0,str(SKILL/'scripts'))
from renderizar import native_resolution, camera_filters, make_ass, atempo_chain

class Policies(unittest.TestCase):
 def test_native_dimensions(self):
  for w,h in [(1280,720),(1920,1080),(2560,1440),(3840,2160)]:
   self.assertEqual(native_resolution({'width':w,'height':h},False),(w,h))
   self.assertEqual(native_resolution({'width':w,'height':h},True),(h,w))

 def test_unsupported_odd_dimensions(self):
  with self.assertRaises(ValueError):native_resolution({'width':1919,'height':1080},False)

 def test_public_manifest(self):
  rows=json.loads((SKILL/'assets/audio-manifest.json').read_text(encoding='utf-8'))['assets']
  self.assertEqual(len(rows),82)
  self.assertTrue(all(r['commercial_allowed'] and r['distribution_allowed'] for r in rows))
  full=[r for r in rows if r.get('version')=='full']
  self.assertEqual(len(full),36)
  self.assertTrue(all(r['license']=='CC BY 4.0' and r['attribution_required'] for r in full))
  self.assertTrue(all(r['download_url'].startswith('https://incompetech.com/') for r in full))
  self.assertFalse(any('fornecidas' in r['path'] or 'fornecidos' in r['path'] for r in rows))

 def test_complete_bundled_library(self):
  library=SKILL/'assets/biblioteca-audio'
  rows=json.loads((library/'catalogo.json').read_text(encoding='utf-8'))['assets']
  self.assertEqual(len(rows),197)
  self.assertEqual(sum(r['license_status']=='unverified' for r in rows),38)
  self.assertEqual(sum(r.get('commercial_allowed',False) for r in rows),159)
  for row in rows:
   with self.subTest(file=row['path']):
    file=library/row['path']
    self.assertTrue(file.is_file())
    self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),row['sha256'])

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

 def test_capcut_sfx_cleared_and_categorized(self):
  rows=json.loads((SKILL/'assets/biblioteca-audio/catalogo.json').read_text(encoding='utf-8'))['assets']
  capcut=[r for r in rows if 'capcut-convertidos' in r['path']]
  self.assertEqual(len(capcut),77)
  self.assertTrue(all(r['commercial_allowed'] and r['license_status']=='user-declared-royalty-free' for r in capcut))
  self.assertTrue(all(r.get('category') and 'peak_db' in r for r in capcut))
  self.assertFalse(any(r.get('commercial_allowed') for r in rows if 'fornecid' in r['path']))
  self.assertGreaterEqual(sum(r['category']=='soco' for r in capcut),5)

 def test_camera_effects_build_filters(self):
  f=camera_filters([{'type':'punch','at':1,'center':[.3,.6]},{'type':'shake','at':2},{'type':'flash','at':3,'color':'amarelo'}],1920,1080,60,10)
  self.assertTrue(f[0].startswith('zoompan='))
  self.assertIn('between(it,1.000,1.350)',f[0])
  self.assertIn('sin(',f[0])
  self.assertEqual(sum('drawbox' in x and 'yellow' in x for x in f),2)
  self.assertEqual(camera_filters([],1920,1080,60,10),[])
  with self.assertRaises(ValueError):camera_filters([{'type':'explodir','at':1}],1920,1080,60,10)

 def test_caption_styles_and_escaping(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'c.ass'
   make_ass(p,[{'start':0,'end':1,'text':'POW {\\b1}','style':'grito','color':'vermelho'},
               {'start':1,'end':2.00001,'text':'JOGO 2','style':'titulo'}],1080,1920,2.0,False)
   t=p.read_text(encoding='utf-8-sig')
   self.assertIn(',grito,,',t); self.assertIn(',titulo,,',t); self.assertIn('&H003C3CFF',t)
   self.assertNotIn('{\\b1}',t)
   with self.assertRaises(ValueError):make_ass(p,[{'start':0,'end':1,'text':'x','style':'neon'}],1080,1920,2,False)

 def test_atempo_chain_limits(self):
  self.assertEqual(atempo_chain(1),[])
  self.assertEqual(atempo_chain(.25),['atempo=0.5','atempo=0.5'])
  self.assertEqual(atempo_chain(4),['atempo=2','atempo=2'])

 def test_sfx_selector_prefers_unused(self):
  lib=SKILL/'assets/biblioteca-audio'
  cmd=[sys.executable,str(SKILL/'scripts/selecionar_sfx.py'),'--library',str(lib),'--categoria','soco','--count','1']
  first=json.loads(subprocess.check_output(cmd))[0]['file']
  with tempfile.TemporaryDirectory() as td:
   tl=Path(td)/'timeline.json'
   tl.write_text(json.dumps({'outputs':[{'sfx':[{'file':first,'at':0}]}]}),encoding='utf-8')
   again=json.loads(subprocess.check_output(cmd+['--timeline',str(tl)]))[0]['file']
  self.assertNotEqual(first,again)

if __name__=='__main__':unittest.main()
