#!/usr/bin/env python3
"""Analyse les PNG locaux référencés par data.geojson; n'altère aucun fichier source."""
import argparse, json, csv, colorsys
from collections import Counter
from pathlib import Path
from PIL import Image

FAMILIES = ['rouge','orange','jaune','vert','cyan','bleu','violet','rose']

def family(rgb):
    r,g,b = [v/255 for v in rgb]
    h,s,v = colorsys.rgb_to_hsv(r,g,b)
    if v < .20: return 'noir'
    if s < .13: return 'blanc' if v > .88 else 'gris'
    if s < .22 and v < .42: return 'gris'
    deg = h*360
    if deg < 15 or deg >= 345: return 'rouge'
    if deg < 45: return 'orange'
    if deg < 70: return 'jaune'
    if deg < 165: return 'vert'
    if deg < 195: return 'cyan'
    if deg < 255: return 'bleu'
    if deg < 295: return 'violet'
    return 'rose'

def analyse(path):
    with Image.open(path) as src:
        img = src.convert('RGBA')
        img.thumbnail((350,350),Image.Resampling.LANCZOS)
        px = list(img.getdata())
    # Ignore pixels transparents et bordures d'antialiasing, pondère par alpha.
    opaque = [(r,g,b,a) for r,g,b,a in px if a >= 160]
    if not opaque: return {'status':'transparent_or_empty'}
    # Bins RGB de 16 unités, robustes aux légères variations des PNG.
    bins=Counter(); fam=Counter(); total=0
    for r,g,b,a in opaque:
        weight=a/255
        q=(min(255,(r//16)*16+8),min(255,(g//16)*16+8),min(255,(b//16)*16+8))
        bins[q]+=weight; fam[family((r,g,b))]+=weight; total+=weight
    main=bins.most_common(5)
    colors=[{'hex':'#%02X%02X%02X'%rgb,'share':round(w/total,4),'family':family(rgb)} for rgb,w in main]
    families={k:round(v/total,4) for k,v in fam.most_common()}
    return {'status':'ok','dominant_hex':colors[0]['hex'],'dominant_family':max(fam,key=fam.get),
            'colors':colors,'families':families,'opaque_fraction':round(len(opaque)/max(1,len(px)),4),
            'estimated_color_count':sum(w/total>=.07 for _,w in bins.items())}

def main():
    p=argparse.ArgumentParser(description='Extraction des couleurs des emblèmes PNG')
    p.add_argument('--site',default='.',help='Dossier contenant data.geojson et images/')
    p.add_argument('--output',default='emblem_colors.json')
    args=p.parse_args()
    root=Path(args.site).resolve()
    with (root/'data.geojson').open(encoding='utf-8') as f: data=json.load(f)
    result={}; counts=Counter()
    for feat in data['features']:
        prop=feat.get('properties',{})
        key=str(prop.get('code5') or prop.get('qid') or '')
        image=prop.get('image')
        if not key: continue
        if not image:
            result[key]={'status':'no_image'};counts['no_image']+=1;continue
        # N'accepte que les chemins locaux, jamais de téléchargement réseau.
        if '://' in image or image.startswith('//'):
            result[key]={'status':'remote_image'};counts['remote_image']+=1;continue
        path=(root/image.split('?',1)[0]).resolve()
        if not path.is_relative_to(root):
            result[key]={'status':'invalid_path'};counts['invalid_path']+=1;continue
        if not path.is_file():
            result[key]={'status':'file_missing'};counts['file_missing']+=1;continue
        try: record=analyse(path)
        except Exception as exc: record={'status':'error','detail':str(exc)}
        result[key]=record;counts[record['status']]+=1
    out=root/args.output
    with out.open('w',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2)
    csvpath=out.with_suffix('.csv')
    with csvpath.open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f);writer.writerow(['code5','status','dominant_hex','dominant_family','opaque_fraction','estimated_color_count'])
        for key,r in result.items():writer.writerow([key,r['status'],r.get('dominant_hex',''),r.get('dominant_family',''),r.get('opaque_fraction',''),r.get('estimated_color_count','')])
    print('Terminé:',dict(counts),'\nJSON:',out,'\nCSV:',csvpath)

if __name__=='__main__': main()
