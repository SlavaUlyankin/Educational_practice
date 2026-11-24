from pathlib import Path
from PIL import Image
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Mm

path = Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
doc = Document(path)
p = next(p for p in doc.paragraphs if p.text.startswith('Рисунок 15 —'))
node = p._p.getprevious()
while node is not None and not node.xpath('.//a:blip'):
    node = node.getprevious()
assert node is not None
rid, _ = doc.part.get_or_add_image('docs/figures/a5_stage1.png')
node.xpath('.//a:blip')[0].set(qn('r:embed'), rid)
pw, ph = Image.open('docs/figures/a5_stage1.png').size
width = min(int(Mm(155)), int(Mm(210) * pw / ph))
height = round(width * ph / pw)
extent = node.xpath('.//wp:extent')[0]
extent.set('cx', str(width)); extent.set('cy', str(height))
for inner in node.xpath('.//a:xfrm/a:ext'):
    inner.set('cx', str(width)); inner.set('cy', str(height))
doc.save(path)
Document(path)
