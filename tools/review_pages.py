from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import sys

folder=Path('docs/report/rendered')
prefix=sys.argv[1] if len(sys.argv)>1 else 'page'
files=sorted(folder.glob(prefix+'-*.jpg'))
for start in range(0,len(files),12):
    canvas=Image.new('RGB',(4*400,3*590),'#c3c3c3')
    for n,path in enumerate(files[start:start+12]):
        page=Image.open(path).convert('RGB');page.thumbnail((385,555))
        x=(n%4)*400+(400-page.width)//2;y=(n//4)*590+25
        canvas.paste(page,(x,y));ImageDraw.Draw(canvas).text((x,y-20),path.stem,fill='black')
    canvas.save(folder/f'{prefix}-contact-{start//12+1}.jpg',quality=85)
