from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
files=sorted(Path('docs/report/rendered').glob('stage7-*.jpg'))
thumbs=[]
for f in files:
    im=Image.open(f).convert('RGB');im.thumbnail((320,450));canvas=Image.new('RGB',(340,480),'white');canvas.paste(im,((340-im.width)//2,20));ImageDraw.Draw(canvas).text((10,2),f.stem,fill='black');thumbs.append(canvas)
out=Image.new('RGB',(340*4,480*((len(thumbs)+3)//4)),'#aaa')
for i,im in enumerate(thumbs):out.paste(im,((i%4)*340,(i//4)*480))
out.save('docs/report/rendered/stage7-contact.jpg')
print('pages',len(files))
