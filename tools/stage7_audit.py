from docx import Document
from pathlib import Path
d=Document('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_организация.docx')
terms=('faulty','неисправн','JUnit','unittest','Session','Перенос на то же','СПИСОК ЛИТЕРАТУРЫ','Рисунок 11','Рисунок 15','Рисунок 16')
for i,p in enumerate(d.paragraphs):
    if any(t.lower() in p.text.lower() for t in terms): print('P',i,p.text[:1000])
for i,t in enumerate(d.tables):
    for n,row in enumerate(t.rows):
        text=' | '.join(c.text for c in row.cells)
        if any(x.lower() in text.lower() for x in ('faulty','неисправн','Session','JUnit')): print('T',i,n,text[:800])
