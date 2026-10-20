# Gerçek Safari'de (safaridriver) vaziyet planını açar, başka pencereye geçip döner,
# gerçek ekranı (screencapture) ve WebGL durumunu kaydeder.
import subprocess, time, json, sys, os
from selenium import webdriver
URL = sys.argv[1]; OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
JS = """var c=document.querySelector('.pnlm-render-container canvas');if(!c)return {err:'canvas yok',world:!!document.querySelector('.pnlm-world')};
var g=c.getContext('webgl')||c.getContext('experimental-webgl');var q=g?Array.from(g.getParameter(g.VIEWPORT)):null;
return {cw:c.width,ch:c.height,kw:c.clientWidth,kh:c.clientHeight,dpr:devicePixelRatio,vp:q,bw:g&&g.drawingBufferWidth,bh:g&&g.drawingBufferHeight,lost:g&&g.isContextLost(),ua:navigator.userAgent,duz:window.__vpDuzeltme||0,iw:innerWidth,ih:innerHeight};"""
def shot(n):
    subprocess.run(['screencapture', '-x', f'{OUT}/safari-{n}.png'])
def osa(s): subprocess.run(['osascript', '-e', s])
d = webdriver.Safari()
d.set_window_rect(0, 0, 1280, 800)
d.get(URL); time.sleep(12)
try: d.execute_script("var r=document.querySelector('.cerez button.red');if(r)r.click();")
except Exception: pass
log = {}
log['1-acilis'] = d.execute_script(JS); shot('1-acilis')
d.execute_script("document.querySelector('.sc[data-k=\"5\"]').click()"); time.sleep(8)
log['2-sahne5'] = d.execute_script(JS); shot('2-sahne5')
for i in range(3):
    osa('tell application "Finder" to activate'); osa('tell application "Finder" to make new Finder window'); time.sleep(3); shot(f'3-finder{i}')
    osa('tell application "Safari" to activate'); time.sleep(4)
    log[f'4-donus{i}'] = d.execute_script(JS); shot(f'4-donus{i}')
d.execute_script("document.getElementById('tgl').click()"); time.sleep(7)
osa('tell application "TextEdit" to activate'); time.sleep(3); osa('tell application "Safari" to activate'); time.sleep(4)
log['5-gece-donus'] = d.execute_script(JS); shot('5-gece-donus')
d.execute_script("document.getElementById('tgl').click()"); time.sleep(7)
log['6-gunduz'] = d.execute_script(JS); shot('6-gunduz')
print(json.dumps(log, indent=1, ensure_ascii=False))
json.dump(log, open(f'{OUT}/safari-log.json', 'w'), indent=1, ensure_ascii=False)
d.quit()
