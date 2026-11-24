from docx import Document
d=Document('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_образование.docx')
for i,p in enumerate(d.paragraphs):
    if p.style.name.startswith('Heading') or p.text.strip() in ('СОДЕРЖАНИЕ','Приложение А','Приложение Б','Приложение В','СПИСОК ЛИТЕРАТУРЫ'):
        print(i,p.style.name,repr(p.text[:180]))
print('TOC',len([x for x in d.element.body.xpath('.//w:instrText') if 'TOC' in (x.text or '')]))
print('FIRST PARAGRAPHS')
for i,p in enumerate(d.paragraphs[:85]): print(i,repr(p.text[:130]))
