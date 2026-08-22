import re, os, json, subprocess, glob
SKIP = {'index.html','privacy-policy.html','preview.html'}
GROUP = [('dnd-','地城迴響'),('zl-','殭屍防線'),('vr-','吸血鬼復仇')]

def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
def pick(pat, s):
    m = re.search(pat, s, re.S)
    return re.sub(r'\s+',' ', re.sub('<[^>]+>','', m.group(1))).strip() if m else ''

rows = []
for f in sorted(glob.glob('*.html')):
    if f in SKIP: continue
    s = open(f, encoding='utf-8').read()
    t = pick(r'<title>(.*?)</title>', s) or pick(r'<h1[^>]*>(.*?)</h1>', s)
    l = pick(r'class="lede"[^>]*>(.*?)</p>', s)
    c = sh(f'git log --diff-filter=A -1 --format=%ad --date=short -- {f}') or sh('date +%F')
    u = sh(f'git log -1 --format=%ad --date=short -- {f}') or c
    kb = os.path.getsize(f)//1024
    assets = []
    d = f[:-5]
    if os.path.isdir(d):
        assets.append(d)
        kb += sum(os.path.getsize(os.path.join(r,x)) for r,_,fs in os.walk(d) for x in fs)//1024
    g = next((n for p,n in GROUP if f.startswith(p)), '美術與特效')
    rows.append({"f":f,"t":t,"l":l,"c":c,"u":u,"kb":max(1,kb),"assets":assets,"g":g})

rows.sort(key=lambda r:(r['u'], r['f']), reverse=True)
p = open('preview.html', encoding='utf-8').read()
new = 'const DATA=' + json.dumps(rows, ensure_ascii=False) + ';'
p2, n = re.subn(r'const DATA=\[.*?\];', lambda m: new, p, count=1, flags=re.S)
assert n == 1, '找不到 DATA 陣列'
open('preview.html','w',encoding='utf-8').write(p2)
print(f'索引重建：{len(rows)} 頁')
for r in rows: print(' -', r['f'], '|', r['t'][:36], '|', r['g'])
