"""Замена трёх схем обмена сообщениями и связанных описаний."""
from pathlib import Path
from PIL import Image
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Mm

path=Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
doc=Document(path)
for number, image_path in [(1,'docs/figures/bpmn_overview.png'),(2,'docs/figures/bpmn_client.png'),(4,'docs/figures/bpmn_esp1_draft.png')]:
    p=next(p for p in doc.paragraphs if p.text.startswith(f'Рисунок {number} —'))
    node=p._p.getprevious()
    while node is not None and not node.xpath('.//a:blip'): node=node.getprevious()
    assert node is not None
    rid,_=doc.part.get_or_add_image(image_path)
    node.xpath('.//a:blip')[0].set(qn('r:embed'),rid)
    pw,ph=Image.open(image_path).size
    width=min(int(Mm(155)),int(Mm(190)*pw/ph));height=round(width*ph/pw)
    ext=node.xpath('.//wp:extent')[0];ext.set('cx',str(width));ext.set('cy',str(height))
    for inner in node.xpath('.//a:xfrm/a:ext'):
        inner.set('cx',str(width));inner.set('cy',str(height))

p=next(p for p in doc.paragraphs if p.text.startswith('Отмена и перенос брони оформлены как непрерывающий'))
p.clear();p.add_run('Отмена и перенос брони оформлены как непрерывающий подпроцесс-событие ESP1 (рисунок 4): сообщение клиента запускает отдельную обработку, не останавливая обработку остальных броней. Администратор находит активную бронь (X1.2, X1.3) и определяет вид запроса (X1.6). При отмене он изменяет статус брони и урегулирует предоплату по правилам точки (X1.7–X1.9); при переносе проверяет новый слот и площадку (X1.13, X1.14), после чего обновляет бронь (X1.15) или предлагает альтернативы, сохраняя прежнюю бронь (X1.18–X1.19).')

table=next(t for t in doc.tables if t.cell(0,0).text == 'Шлюз')
for row in table.rows:
    if row.cells[0].text.startswith('X1.8 / X1.14'):
        for cell,text in zip(row.cells,['X1.14','Новый слот свободен и комплектов достаточно?','да — изменить бронь и записать историю (X1.15); нет — сохранить прежнюю бронь и предложить варианты (X1.18, X1.19)']):
            p=cell.paragraphs[0];p.clear();p.add_run(text)
doc.save(path);Document(path)
