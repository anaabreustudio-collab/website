"""One-time conversion of the supplied Figma reference into local artwork fragments.
The website itself uses only HTML, CSS, JavaScript and local assets.
"""
import re, json, html
from pathlib import Path
from html.parser import HTMLParser

source = Path('.design/context-0.txt').read_text()
assets = json.loads(Path('.design/assets.json').read_text())['assets']
markup = source.split('return (',1)[1].split('\n  );',1)[0].strip()
markup = re.sub(r'\{`([^`]*?)`\}', lambda m: html.escape(m[1]), markup)
markup = re.sub(r'src=\{(\w+)\}', lambda m: 'src="/images/'+assets[m[1]]+'"', markup)
markup = re.sub(r'style=\{\{ maskImage: `url\("\$\{(\w+)\}"\)` \}\}', lambda m: 'data-mask="/images/'+assets[m[1]]+'"', markup)
markup = markup.replace('className=', 'class=').replace('<br aria-hidden />','<br />')

class Node:
    def __init__(self,tag='root',attrs=()):self.tag,self.attrs,self.children=tag,dict(attrs),[]
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.root=Node();self.stack=[self.root]
    def handle_starttag(self,tag,attrs):
        n=Node(tag,attrs);self.stack[-1].children.append(n)
        if tag not in ('img','br'):self.stack.append(n)
    def handle_endtag(self,tag):self.stack.pop()
    def handle_startendtag(self,tag,attrs):self.stack[-1].children.append(Node(tag,attrs))
    def handle_data(self,data):
        if data.strip():self.stack[-1].children.append(data.strip())
p=Parser();p.feed(markup)
nodes={n.attrs['data-node-id']:n for n in p.root.children[0].children if isinstance(n,Node)}

fixed={'absolute':('position','absolute'),'relative':('position','relative'),'contents':('display','contents'),'block':('display','block'),'flex':('display','flex'),'flex-none':('flex','none'),'items-center':('align-items','center'),'justify-center':('justify-content','center'),'overflow-hidden':('overflow','hidden'),'overflow-clip':('overflow','clip'),'pointer-events-none':('pointer-events','none'),'object-cover':('object-fit','cover'),'max-w-none':('max-width','none'),'mix-blend-difference':('mix-blend-mode','difference'),'whitespace-nowrap':('white-space','nowrap'),'not-italic':('font-style','normal'),'text-center':('text-align','center'),'mb-0':('margin-bottom','0'),'opacity-80':('opacity','.8'),'leading-none':('line-height','1'),'whitespace-pre':('white-space','pre'),'whitespace-pre-wrap':('white-space','pre-wrap'),'text-right':('text-align','right'),'underline':('text-decoration','underline'),'border-solid':('border-style','solid'),'border-black':('border-color','#000'),'mask-alpha':('mask-mode','alpha'),'mask-intersect':('mask-composite','intersect'),'mask-no-clip':('mask-clip','no-clip'),'mask-no-repeat':('mask-repeat','no-repeat')}
props={'h':'height','w':'width','top':'top','left':'left','inset':'inset','bg':'background','leading':'line-height','tracking':'letter-spacing','mask-position':'mask-position','mask-size':'mask-size','border':'border-width'}
def styles(classes):
    d={}
    for c in classes.split():
        if c in fixed:k,v=fixed[c];d[k]=v
        elif c.startswith('font-') or c.startswith('decoration-'):continue
        elif c=='[word-break:break-word]':d['overflow-wrap']='break-word'
        elif c=='[text-underline-position:from-font]':d['text-underline-position']='from-font'
        elif 'rotate-' in c:d['transform']='rotate('+('-' if c.startswith('-') else '')+c.split('-')[-1]+'deg)'
        elif c in ('-translate-x-1/2','-translate-y-1/2'):
            d['transform']=d.get('transform','')+' translate'+('X' if '-x-' in c else 'Y')+'(-50%)'
        elif c=='-translate-x-full':d['transform']='translateX(-100%)'
        else:
            m=re.match(r'(.+?)-\[(.+)\]$',c)
            if m:key,value=m[1],m[2].replace('_',' ')
            else:
                key,_,value=c.rpartition('-');value={'full':'100%','0':'0','black':'#000','white':'#fff'}.get(value,value)
            if key=='size':d['width']=d['height']=value
            elif key=='text':d['color' if value.startswith('#') else 'font-size']=value
            elif key=='border' and value.startswith(('#','rgb')):d['border-color']=value
            elif key in props:d[props[key]]=value
            else:raise ValueError(c)
    return d
def px(value, axis="left"):
    if value.startswith('calc('):
        m=re.match(r'calc\(([\d.]+)%([+-][\d.]+)px\)',value)
        return round(float(m[1])*18/100)/18*(4534 if axis=="top" else 1765)+float(m[2])
    return float(value.replace('px',''))
def render(n,x,y,global_coords=True):
    if isinstance(n,str):return html.escape(n)
    d=styles(n.attrs.get('class',''))
    if global_coords and d.get('display')!='contents':
        for key,offset in [('left',x),('top',y)]:
            if key in d:d[key]=f'{px(d[key],key)-offset:.3f}px'
    if 'data-mask' in n.attrs:d['mask-image']='url('+n.attrs['data-mask']+')'
    attrs={'style':';'.join(k+':'+v for k,v in d.items())}
    if 'data-node-id' in n.attrs:attrs['data-figma-node']=n.attrs['data-node-id']
    if n.tag=='img':
        attrs.update(src=n.attrs['src'],alt='',loading='lazy',decoding='async')
        # SVGs keep their original exported dimensions.
        if attrs['src'].endswith('.svg'):
            attrs['loading']='eager'
            d.pop('width',None);d.pop('height',None)
            attrs['style']=';'.join(k+':'+v for k,v in d.items())
    result='<'+n.tag+''.join(' '+k+'="'+html.escape(v,quote=True)+'"' for k,v in attrs.items())+'>'
    if n.tag in ('img','br'):return result
    next_global=global_coords and d.get('display')=='contents'
    return result+''.join(render(c,x,y,next_global) for c in n.children)+'</'+n.tag+'>'

# Layer order is preserved, including masks, image crops, and intentional empty tiles.
specs=[
 ('as-runas','As Runas','Boutique Hotel',15,139,[4]),
 ('dtx','DTX','Record Label',404,139,[83]),
 ('interstellar','Interstellar','Cover Single',793,139,[84]),
 ('future-films','Future Films','Streaming Plataform',1182,139,[30]),
 ('arnaldo-antunes','Arnaldo Antunes','Album Cover',1571,139,[88]),
 ('gandum','Gandum','Boutique Hotel',15,552,[17,52]),
 ('nomade-records','Nomade Records','Record Label',404,552,[16]),
 ('o33','O33','Wodd Craftmanship',793,552,[18]),
 ('domenique-dumont','Domenique Dumont','Cover Album',1182,552,[23,51]),
 ('tzol-skin','Tzol’Skin','Vegan Skincare',1571,552,[98]),
 ('alquimia','Alquimia do Montado','Gourmet Foods',15,963,[54,55]),
 ('obsolete','obsolete.studio','Cultural Organization',404,963,[14,34,35]),
 ('alma','Alma','Cover Single',793,963,[85,86]),
 ('aivados','AIVADOS','Boutique Surf Hotel',1182,963,[42]),
 ('wrkrm','WRKRM','Music Events',1571,963,[27]),
 ('poster','Poster','Mixmedia Poster',15,1374,[102,103]),
 ('hauto','HAUTO','Skincare',404,1374,[96]),
 ('magnameta','Magnameta','Interior Design',793,1374,[106,107]),
 ('cityleaks','CityLeaks','Urban Art Festival',1181,1374,[100]),
 ('cisma','CISMA','Youth Organization',1571,1374,[105]),
 ('conversas','Conversas Rotterdam','',1181,1788,[108,109]),
 ('wildfleur','Wildfleur','Skincare',14,2178.35,[126,150]),
 ('capy','Capy','AI Software Engineer',403,2178.35,[125,129,130,131,141]),
 ('heeria','Heeria','Jewelry',792,2178.35,[151,160]),
 ('painting','Painting','Oil patel on Papper',1180,2178.35,[116]),
 ('oliver-wyman','Oliver Wyman','Consulting',1570,2178.35,[154]),
]
projects=[]
for i,(slug,title,category,x,y,ids) in enumerate(specs):
    Path('content/artwork/'+slug+'.html').write_text(''.join(render(nodes['1:'+str(id)],x,y) for id in ids)+'\n')
    item={'id':slug,'title':title,'category':category,'artwork':slug+'.html'}
    if slug=='domenique-dumont':item['note']='(Personal Project)'
    if slug=='conversas':item.update(caption=False,desktopColumn=4,desktopRow=5)
    projects.append(item)
Path('content/projects.json').write_text(json.dumps(projects,ensure_ascii=False,indent=2)+'\n')
print('Imported',len(projects),'artwork compositions.')
