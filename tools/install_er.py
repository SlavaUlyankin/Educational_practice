from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from PIL import Image

path = Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
doc = Document(path)
caption = next(p for p in doc.paragraphs if p.text.startswith('Рисунок 10 — Логическая модель'))
node = caption._p.getprevious()
while node is not None and not node.xpath('.//a:blip'):
    node = node.getprevious()
assert node is not None
blips = node.xpath('.//a:blip')
assert len(blips) == 1
rid, _ = doc.part.get_or_add_image('docs/figures/er_stage1.png')
blips[0].set(qn('r:embed'), rid)
width_px, height_px = Image.open('docs/figures/er_stage1.png').size
extent = node.xpath('.//wp:extent')[0]
height = str(round(int(extent.get('cx')) * height_px / width_px))
extent.set('cy', height)
for inner in node.xpath('.//a:xfrm/a:ext'):
    inner.set('cy', height)
doc.save(path)
Document(path)
