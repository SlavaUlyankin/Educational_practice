"""Удаление неиспользованного источника и вставка таблицы потоков сообщений."""
import re
from copy import deepcopy
from pathlib import Path
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

path=Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
output=Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_этап1.docx')
d=Document(path)
source_start=next(i for i,p in enumerate(d.paragraphs) if p.text.strip()=='СПИСОК ЛИТЕРАТУРЫ')
source_end=next(i for i,p in enumerate(d.paragraphs) if i>source_start and p.text.strip()=='Приложение А')
source_paras=d.paragraphs[source_start+1:source_end]
unused=next(p for p in source_paras if p.text.startswith('5. Рынок устройств виртуальной'))
assert not any('[5]' in ''.join(t.text or '' for t in p.xpath('.//w:t')) for p in d.element.body.xpath('.//w:p'))
unused._p.getparent().remove(unused._p)

def replace_in_nodes(p, pattern, convert):
    nodes=p.xpath('.//w:t'); whole=''.join(n.text or '' for n in nodes)
    for match in reversed(list(re.finditer(pattern,whole,flags=re.IGNORECASE))):
        replacement=convert(match)
        start,end=match.span();offset=0; first=last=None; lo=hi=0
        for node in nodes:
            size=len(node.text or '')
            if first is None and start < offset+size: first=node;lo=start-offset
            if first is not None and end <= offset+size: last=node;hi=end-offset;break
            offset+=size
        assert first is not None and last is not None
        if first is last: first.text=(first.text or '')[:lo]+replacement+(first.text or '')[hi:]
        else:
            first.text=(first.text or '')[:lo]+replacement
            active=False
            for node in nodes:
                if node is first: active=True;continue
                if active and node is last: node.text=(node.text or '')[hi:];break
                if active: node.text=''
        whole=''.join(n.text or '' for n in nodes)

for p in d.element.body.xpath('.//w:p'):
    replace_in_nodes(p,r'\[(\d{1,2})\]',lambda m: f'[{int(m.group(1))-1}]' if 6<=int(m.group(1))<=16 else m.group(0))
    replace_in_nodes(p,r'(таблиц(?:а|е|ы|у|ей)?\s+)(\d+)',lambda m: m.group(1)+str(int(m.group(2))+1) if 3<=int(m.group(2))<=13 else m.group(0))

for p in source_paras:
    if p is unused: continue
    if re.match(r'^(?:[6-9]|1[0-6])\.\s',p.text):
        replace_in_nodes(p._p,r'^(\d+)\.(?=\s)',lambda m: str(int(m.group(1))-1)+'.')

figure=next(p for p in d.paragraphs if p.text.startswith('Рисунок 4 —'))
caption_template=next(p for p in d.paragraphs if p.text.startswith('Таблица 2 —'))
caption=deepcopy(caption_template._p)
for child in list(caption):
    if child.tag != qn('w:pPr'):caption.remove(child)
run=OxmlElement('w:r'); runtext=OxmlElement('w:t'); runtext.text='Таблица 3 — Обмен сообщениями при отмене и переносе брони'; run.append(runtext);caption.append(run)
figure._p.addnext(caption)
table=d.add_table(rows=1,cols=3)
table.style=next(t.style for t in d.tables if len(t.columns)==3 and t is not table)
data=[('Сообщение','Отправитель → получатель','Содержание и результат'),
('ML5.1','Клиент → администратор','Запрос отмены; запуск ESP1 и поиск активной брони в DS1.'),
('ML5.2','Клиент → администратор','Запрос переноса с указанием нового времени и при необходимости площадки.'),
('ML6.1','Администратор → клиент','Подтверждение отмены после изменения статуса и записи события.'),
('ML6.2','Администратор → клиент','Подтверждение переноса после проверки слота и записи старых и новых значений.'),
('ML6.3','Администратор → клиент','Отказ или альтернативы; при неудачном переносе бронь сохраняется.')]
for idx,rowdata in enumerate(data):
    cells=table.rows[0].cells if idx==0 else table.add_row().cells
    for cell,text in zip(cells,rowdata):
        p=cell.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.space_after=Pt(0)
        r=p.add_run(text);r.font.name='Times New Roman';r.font.size=Pt(10);r.bold=(idx==0)
head=table.rows[0]._tr.get_or_add_trPr();head.append(OxmlElement('w:tblHeader'))
for row in table.rows: row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
caption.addnext(table._tbl)
anchor=next(p for p in d.paragraphs if p.text.startswith('Для уточнения обмена сообщения ML5'))
anchor.add_run(' Состав сообщений приведён в таблице 3.')
for run in anchor.runs:
    run.font.name='Times New Roman';run.font.size=Pt(14)
    fonts=run._element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ('ascii','hAnsi','cs','eastAsia'):fonts.set(qn('w:'+attr),'Times New Roman')
d.save(output);Document(output)
