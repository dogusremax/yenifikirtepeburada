"""Render kuyruğu: plans/*.json içinde "ready": true olan ve henüz yayımlanmamış planları sırayla
render eder, assets/kat3d/<id>/ altına webp + meta.json yazar, data.js'i yeniler, commit edip main'e iter.
Çalıştırma: setsid nohup python3 tools/kat3d/queue.py > tools/kat3d/queue.log 2>&1 &
Durdurmak için: touch tools/kat3d/STOP"""
import json, os, glob, subprocess, sys, time, shutil
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.path.join(REPO, 'assets', 'kat3d'); WORK = os.path.join(HERE, '_work')
ORDER = ['11', '2', '4', '12', '19', '3', '5']
N, RES, SAMPLES, EL = 36, 960, 30, 62
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def sh(*cmd, **kw): return subprocess.run(cmd, cwd=REPO, **kw)
def short(n): return n.replace('Ebeveyn Yatak Odası', 'Ebeveyn Y. Odası').replace('Ebeveyn Yatak Odasi', 'Ebeveyn Y. Odası')
def rebuild_data():
    data = {}
    for m in sorted(glob.glob(os.path.join(ASSETS, '*', 'meta.json'))):
        pid = os.path.basename(os.path.dirname(m)); data[pid] = json.load(open(m))
    open(os.path.join(ASSETS, 'data.js'), 'w').write('window.KAT3D=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
def pending():
    out = []
    for f in glob.glob(os.path.join(HERE, 'plans', '*.json')):
        p = json.load(open(f))
        if p.get('ready') and not os.path.exists(os.path.join(ASSETS, p['id'], 'meta.json')): out.append(p)
    key = lambda p: (ORDER.index(p['id'].split('-')[0]) if p['id'].split('-')[0] in ORDER else 99, p['id'])
    return sorted(out, key=key)
def render(p):
    pid = p['id']; wd = os.path.join(WORK, pid); os.makedirs(wd, exist_ok=True); b = os.path.join(HERE, 'build.py')
    top = os.path.join(wd, 'top.png')
    if not os.path.exists(top + '.json'):
        log(pid, 'kuş bakışı'); subprocess.run([sys.executable, b, pid, 'top', top, '1300', '40'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log(pid, 'döndürme %d kare' % N)
    subprocess.run([sys.executable, b, pid, 'spin', wd, str(N), str(RES), str(SAMPLES), str(EL)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    fr = [os.path.join(wd, 'f%02d.png' % i) for i in range(N)]
    if not all(os.path.exists(x) for x in fr) or not os.path.exists(top + '.json'): raise RuntimeError('eksik kare')
    od = os.path.join(ASSETS, pid); os.makedirs(od, exist_ok=True)
    for i, x in enumerate(fr): Image.open(x).save(os.path.join(od, 'f%02d.webp' % i), 'WEBP', quality=84, method=4)
    Image.open(top).save(os.path.join(od, 'top.webp'), 'WEBP', quality=86, method=4)
    lab = json.load(open(os.path.join(wd, 'labels_0.json')))
    meta = {'dir': 'assets/kat3d/%s/' % pid, 'n': N, 'labels': [lab[str(i)] for i in range(N)], 'top': json.load(open(top + '.json')),
            'rooms': [[r[0], short(r[1]), r[2]] for r in p['rooms']]}
    json.dump(meta, open(os.path.join(od, 'meta.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    rebuild_data()
def publish(pid):
    sh('git', 'add', '-A', 'assets/kat3d', 'tools/kat3d/plans')
    msg = 'Kat planları 3D: %s eklendi\n\nCo-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_015dAWQkN84MvRwkmuWSfWiy' % pid
    sh('git', 'commit', '-q', '-m', msg)
    for i in range(5):
        sh('git', 'fetch', '-q', 'origin', 'main'); sh('git', 'merge', '-q', '--no-edit', 'origin/main')
        if sh('git', 'push', '-q', 'origin', 'HEAD:main').returncode == 0: break
        time.sleep(2 ** (i + 1))
    sh('git', 'push', '-q', 'origin', 'HEAD:claude/kat-planlari-sayfasi-ig93y7')
    log(pid, 'yayımlandı')
if '--rebuild' in sys.argv: rebuild_data(); sys.exit()
while not os.path.exists(os.path.join(HERE, 'STOP')):
    q = pending()
    if not q: time.sleep(60); continue
    p = q[0]
    try:
        t0 = time.time(); render(p); publish(p['id']); log(p['id'], 'süre %.0f dk' % ((time.time() - t0) / 60))
        shutil.rmtree(os.path.join(WORK, p['id']), ignore_errors=True)
    except Exception as e:
        log(p['id'], 'HATA', e); time.sleep(30)
