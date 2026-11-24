from pathlib import Path
from docx import Document

source=Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_этап1.docx')
output=Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_готово.docx')
doc=Document(source)
caption=next(p for p in doc.paragraphs if p.text.startswith('Таблица 3 — Обмен сообщениями'))
caption.paragraph_format.page_break_before=True
caption.paragraph_format.keep_with_next=True
doc.save(output);Document(output)
