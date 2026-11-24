"""Сверка ссылок на источники и размеров встроенных изображений."""
import re
import sys
from docx import Document

doc=Document(sys.argv[1])
texts=[p.text for p in doc.paragraphs]
source_start=next(i for i,t in enumerate(texts) if t.strip()=='СПИСОК ЛИТЕРАТУРЫ')
source_end=next(i for i in range(source_start+1,len(texts)) if texts[i].strip()=='Приложение А')
sources={int(m.group(1)) for t in texts[source_start+1:source_end] if (m:=re.match(r'^\s*(\d+)\.\s',t))}
refs={int(x) for t in texts[:source_start] for x in re.findall(r'\[(\d+)\]',t)}
print('Источники:',sorted(sources),'ссылки:',sorted(refs),'нет в списке:',sorted(refs-sources),'не упомянуты:',sorted(sources-refs))
print('Количество таблиц:',len(doc.tables),'встроенных изображений:',len(doc.inline_shapes))
for i,shape in enumerate(doc.inline_shapes,1):
    if shape.width.mm > 165.2:
        print('ПРОВЕРИТЬ ширину рисунка',i,round(shape.width.mm,1),'мм; учитывать поля соответствующего раздела.')
print('Фактическая пагинация, поля и читаемость требуют просмотра в Word.')
