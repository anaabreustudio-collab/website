"""Sync the latest supplied reference, preserving original artwork layer order."""
from pathlib import Path
import json,re
parser = Path('scripts/import-figma.py').read_text().split('# Layer order is preserved')[0]
parser = parser.replace('.design/context-0.txt','.design/rev9.txt').replace('.design/assets.json','.design/rev9-assets.json').replace('4534 if axis', '4929 if axis')
exec(parser)
fixed['mix-blend-multiply']=('mix-blend-mode','multiply')
row_y=[139,552,963,1374,1788,2178.35,2602,3026,3472,3919,4364]
col_x=[15,404,793,1182,1571]
slugs=[
 'as-runas','dtx','interstellar','future-films','arnaldo-antunes',
 'gandum','nomade-records','o33','domenique-dumont','tzol-skin',
 'alquimia','obsolete','alma','aivados','wrkrm',
 'poster','hauto','magnameta','cityleaks','cisma',
 'ide8','swiss-escape','rocket-science','conversas','painting-red',
 'wildfleur','painting','capy','heeria','oliver-wyman',
 'james-flower','telma-goncalves','nomad-records','joren-ottens','outroom',
 'asian-marketplace','ana-viotti','future-print-club','stu-dere','mulheres-com-impacto',
 'apro','gilberto-gil','painting-digital-red','days-of-adventure','painting-mixed',
 'as-runas-illustration','dtx-artwork','illustration-pen','painting-framed','painting-digital-grid',
 'gandum-sign','everpress','joana-nobre','dtx-black','stuff'
]
layers={i:[] for i in range(len(slugs))}
captions={}
def words(n):
    return n if isinstance(n,str) else ' '.join(words(c) for c in n.children)
for node in p.root.children[0].children:
    if isinstance(node,str):continue
    style=styles(node.attrs.get('class',''))
    x,y=px(style.get('left','0')),px(style.get('top','0'),'top')
    if y<50 or y>4700:continue
    # Captions are offset by 262 px from the top of their artwork.
    target_y=y-262 if node.tag=='p' else y
    row=min(range(len(row_y)),key=lambda i:abs(row_y[i]-target_y))
    col=min(range(5),key=lambda i:abs(col_x[i]-x))
    slot=row*5+col
    if node.tag=='p':
        text=' '.join(words(node).split())
        if '•' in text:captions[slot]=[s.strip() for s in text.split('•',1)]
    else:layers[slot].append(node)
projects=[]
for slot,slug in enumerate(slugs):
    row,col=divmod(slot,5)
    assert slot in captions,(slot,'Missing caption')
    assert layers[slot],(slot,'Missing artwork')
    # The final three rows sit one pixel left in the source, except two moved tiles.
    offset_x=-1 if row>=4 else 0
    if row==3 and col==3:offset_x=-1
    if row==5 and col in (2,3):offset_x=0
    x=col_x[col]+offset_x
    y=row_y[row]
    offset_y=-.65 if row==4 and col!=3 else 0
    y+=offset_y
    Path('content/artwork/'+slug+'.html').write_text(''.join(render(n,x,y) for n in layers[slot])+'\n')
    title,category=captions[slot]
    corrections={'Wood Craftmanship':'Wood Craftsmanship','Mixmedia Poster':'Mixed-Media Poster','Real State':'Real Estate','Technic Designer':'Technical Designer','Oil patel on Papper':'Oil Pastel on Paper','Asiatic Marketplace':'Asian Marketplace'}
    category=corrections.get(category,category)
    projects.append({'id':slug,'title':title,'category':category,'artwork':slug+'.html','desktopOffsetX':offset_x,'desktopOffsetY':offset_y})
Path('content/projects.json').write_text(json.dumps(projects,ensure_ascii=False,indent=2)+'\n')
print('Synced',len(projects),'projects and captions from the latest reference.')
