"""Import the newly filled gallery slots from the second supplied Figma revision."""
from pathlib import Path
import json

# Reuse the reference parser and crop/mask conversion without reimporting older slots.
parser = Path('scripts/import-figma.py').read_text().split('# Layer order is preserved')[0]
parser = parser.replace(".design/context-0.txt", ".design/updated.txt").replace(".design/assets.json", ".design/updated-assets.json")
exec(parser)
fixed['mix-blend-multiply'] = ('mix-blend-mode', 'multiply')

updates = [
    ('alma', 793, 963, [453, 454]),
    ('wildfleur', 14, 2178.35, [493, 525]),
    ('ide8', 14, 1787.35, [547, 548]),
    ('ide8-escape', 403, 1787.35, [549, 550, 551, 552, 553, 557]),
    ('jap', 792, 1787.35, [554, 555, 556]),
    ('painting-red', 1570, 1787.35, [544]),
]
for slug, x, y, ids in updates:
    Path('content/artwork/'+slug+'.html').write_text(''.join(render(nodes['1:'+str(id)], x, y) for id in ids)+'\n')

projects = json.loads(Path('content/projects.json').read_text())
# Idempotent: keep any later user additions while replacing this revision's slots.
new_ids = {'ide8','ide8-escape','jap','painting-red'}
projects = [p for p in projects if p['id'] not in new_ids]
index = next(i for i,p in enumerate(projects) if p['id']=='conversas')
conversas = projects[index]
for key in ('caption','desktopColumn','desktopRow'): conversas.pop(key,None)
conversas['category'] = 'Events'
new = [
    {'id':'ide8','title':'IDE8','category':'Real State','artwork':'ide8.html'},
    {'id':'ide8-escape','title':'IDE8','category':'Real State','artwork':'ide8-escape.html'},
    {'id':'jap','title':'JAP','category':'Youth Organization','artwork':'jap.html'},
]
projects[index:index] = new
projects.insert(index+4, {'id':'painting-red','title':'Painting','category':'Oil patel on Papper','artwork':'painting-red.html'})
Path('content/projects.json').write_text(json.dumps(projects,ensure_ascii=False,indent=2)+'\n')
print('Updated six artwork compositions; gallery now has',len(projects),'projects.')
