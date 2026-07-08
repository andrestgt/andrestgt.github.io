# -*- coding: utf-8 -*-
import os, shutil
DL='../Downloads'
FILES={}
FILES['food/singapore/restaurants/mouth-restaurant-di-mao-guan/index.md']='---\nlayout: default\nsection: food\nreview: true\ntitle: Mouth Restaurant - 地茂馆 (Di Mao Guan)\nsubtitle: Maxwell / Chinatown · Dim Sum, Cantonese\n---\n\n<figure>\n  <img src="/photos/singapore/mouth-restaurant-di-mao-guan-1.jpg" alt="Mouth Restaurant - 地茂馆 (Di Mao Guan)">\n  <figcaption>Mouth Restaurant - 地茂馆 (Di Mao Guan)</figcaption>\n</figure>\n\nVery good choice for upscale dim sum in Chinatown with a particularly impressive variety of steamed dumplings. Prices are definitely on the high side, but the quality justifies them. The siomai are especially excellent.\n\n<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">\n<figure>\n  <img src="/photos/singapore/mouth-restaurant-di-mao-guan-2.jpg" alt="Mouth Restaurant - 地茂馆 (Di Mao Guan)">\n  <figcaption>Mouth Restaurant - 地茂馆 (Di Mao Guan)</figcaption>\n</figure>\n<figure>\n  <img src="/photos/singapore/mouth-restaurant-di-mao-guan-3.jpg" alt="Mouth Restaurant - 地茂馆 (Di Mao Guan)">\n  <figcaption>Mouth Restaurant - 地茂馆 (Di Mao Guan)</figcaption>\n</figure>\n<figure>\n  <img src="/photos/singapore/mouth-restaurant-di-mao-guan-4.jpg" alt="Mouth Restaurant - 地茂馆 (Di Mao Guan)">\n  <figcaption>Mouth Restaurant - 地茂馆 (Di Mao Guan)</figcaption>\n</figure>\n</div>\n\n## Ratings\n\n| Category        | Score  |\n| --------------- | ------ |\n| Food            | 8.5/10 |\n| Service         | 7.5/10 |\n| Value for money | 7/10 |\n| Atmosphere      | 7.5/10 |\n| Overall         | 8/10 |\n\n### Practical\n\n🗺️ **Google Maps:** [Open in Google Maps](https://www.google.com/maps/search/?api=1&query=Mouth+Restaurant+Di+Mao+Guan+38+Maxwell+Rd+Singapore)\n📍 38 Maxwell Rd, #01-01/02 Airview Building, Singapore 069116\n🍽️ **Type:** Dim Sum, Cantonese\n💰 **Price level:** S$20–40\n'
FILES['food/singapore/restaurants/singapore-zam-zam-restaurant/index.md']='---\nlayout: default\nsection: food\nreview: true\ntitle: Singapore Zam Zam Restaurant\nsubtitle: Kampong Glam · Indian-Muslim\n---\n\n<figure>\n  <img src="/photos/singapore/singapore-zam-zam-restaurant-1.jpg" alt="Singapore Zam Zam Restaurant">\n  <figcaption>Singapore Zam Zam Restaurant</figcaption>\n</figure>\n\nOld-school Muslim restaurant serving huge portions at very reasonable prices by Singapore standards. The biryani comes with a generous piece of tender mutton and even a small murtabak is large enough to satisfy two hungry people.\n\n<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">\n<figure>\n  <img src="/photos/singapore/singapore-zam-zam-restaurant-2.jpg" alt="Singapore Zam Zam Restaurant">\n  <figcaption>Singapore Zam Zam Restaurant</figcaption>\n</figure>\n<figure>\n  <img src="/photos/singapore/singapore-zam-zam-restaurant-3.jpg" alt="Singapore Zam Zam Restaurant">\n  <figcaption>Singapore Zam Zam Restaurant</figcaption>\n</figure>\n</div>\n\n## Ratings\n\n| Category        | Score  |\n| --------------- | ------ |\n| Food            | 8/10 |\n| Service         | 7/10 |\n| Value for money | 9/10 |\n| Atmosphere      | 7/10 |\n| Overall         | 8/10 |\n\n### Practical\n\n🗺️ **Google Maps:** [Open in Google Maps](https://www.google.com/maps/search/?api=1&query=Singapore+Zam+Zam+Restaurant+697+North+Bridge+Rd)\n📍 697-699 North Bridge Rd, Singapore 198675\n🍽️ **Type:** Indian-Muslim\n💰 **Price level:** S$5–15\n'
PHOTOS=[('SG14-0009.jpg', 'photos/singapore/mouth-restaurant-di-mao-guan-1.jpg'), ('SG14-0011.jpg', 'photos/singapore/mouth-restaurant-di-mao-guan-2.jpg'), ('SG14-0012.jpg', 'photos/singapore/mouth-restaurant-di-mao-guan-3.jpg'), ('SG14-0013.jpg', 'photos/singapore/mouth-restaurant-di-mao-guan-4.jpg'), ('SG15-0041.jpg', 'photos/singapore/singapore-zam-zam-restaurant-1.jpg'), ('SG15-0042.jpg', 'photos/singapore/singapore-zam-zam-restaurant-2.jpg'), ('SG15-0043.jpg', 'photos/singapore/singapore-zam-zam-restaurant-3.jpg'), ('singaporehero.jpg', 'photos/background/singaporehero.jpg'), ('restaurantshero.jpg', 'photos/background/singapore-restaurants.jpg')]

for src,dest in PHOTOS:
    s=os.path.join(DL,src)
    if not os.path.exists(s): print("!! missing",s); continue
    os.makedirs(os.path.dirname(dest),exist_ok=True); shutil.copyfile(s,dest); print("photo",dest)
for rel,content in FILES.items():
    os.makedirs(os.path.dirname(rel),exist_ok=True)
    open(rel,'w',encoding='utf-8',newline='\n').write(content); print("page",rel)
# add hero front matter to country + restaurants landing
def add_hero(path, heroline):
    t=open(path,encoding='utf-8').read()
    if 'hero:' in t.split('---')[1]:
        print("hero already",path); return
    lines=t.split('\n'); outl=[]; done=False
    for ln in lines:
        outl.append(ln)
        if not done and ln.startswith('subtitle:'):
            outl.append(heroline); done=True
    open(path,'w',encoding='utf-8',newline='\n').write('\n'.join(outl)); print("hero+",path)
add_hero('food/singapore/index.md','hero: /photos/background/singaporehero.jpg')
add_hero('food/singapore/restaurants/index.md','hero: /photos/background/singapore-restaurants.jpg')
rp="reviews-without-photos.txt"
if os.path.exists(rp):
    L=[x.strip() for x in open(rp,encoding='utf-8') if x.strip()]
    rm=set(['food/singapore/index.md','food/singapore/restaurants/index.md',
        'food/singapore/restaurants/mouth-restaurant-di-mao-guan/index.md',
        'food/singapore/restaurants/singapore-zam-zam-restaurant/index.md'])
    L=[x for x in L if x not in rm]
    open(rp,'w',encoding='utf-8',newline='\n').write('\n'.join(sorted(set(L)))+'\n'); print('without-photos ->',len(L))
print("DONE")
