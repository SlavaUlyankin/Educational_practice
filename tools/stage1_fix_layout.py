from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

path=Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
doc=Document(path)
prefixes=('Отмена и перенос брони оформлены как непрерывающий', 'Для уточнения обмена сообщения ML5',
          'При отмене администратор получает ML5', 'При переносе администратор получает ML5',
          'Работоспособность реализации проверена набором', 'Основные термины переведённого фрагмента',
          'Программная реализация алгоритмов описана в разделе 10.')
for p in doc.paragraphs:
    if p.text.startswith(prefixes) or ('warn_min = 0 — предупреждение' in p.text) or ('Сложность O(r + k)' in p.text):
        for r in p.runs:
            r.font.name='Times New Roman';r.font.size=Pt(14)
            rf=r._element.get_or_add_rPr().get_or_add_rFonts()
            for attr in ('ascii','hAnsi','cs','eastAsia'):rf.set(qn('w:'+attr),'Times New Roman')

t=next(t for t in doc.tables if t.cell(0,0).text=='Операция' and len(t.columns)==7)
for row in t.rows:
    for cell in row.cells:
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.name='Times New Roman';r.font.size=Pt(10)
    trpr=row._tr.get_or_add_trPr()
    if trpr.find(qn('w:cantSplit')) is None:trpr.append(OxmlElement('w:cantSplit'))
trpr=t.rows[0]._tr.get_or_add_trPr()
if trpr.find(qn('w:tblHeader')) is None:trpr.append(OxmlElement('w:tblHeader'))
doc.save(path);Document(path)
