"""Инвентаризация структуры и прямых параметров DOCX, без изменения файла."""
import sys
from collections import Counter
from docx import Document
from docx.oxml.ns import qn

doc = Document(sys.argv[1])
print('# Фактические параметры документа\n')
for i, s in enumerate(doc.sections, 1):
    mm = lambda x: round(x.mm, 1) if x is not None else None
    print(f'Раздел {i}: страница {mm(s.page_width)} × {mm(s.page_height)} мм; поля Л/П/В/Н: {mm(s.left_margin)}/{mm(s.right_margin)}/{mm(s.top_margin)}/{mm(s.bottom_margin)} мм; первая страница отдельно: {s.different_first_page_header_footer}')
    for name, part in [('верхний', s.header), ('нижний', s.footer)]:
        print(f'  {name} колонтитул: {repr(" | ".join(p.text for p in part.paragraphs))}; поля: {part._element.xml.count("PAGE")}')
print('\n## Стили')
for style in doc.styles:
    if style.type == 1 and (style.name in ('Normal', 'Heading 1', 'Heading 2', 'Heading 3') or any(x in style.name.lower() for x in ('caption', 'подпис'))):
        f, p = style.font, style.paragraph_format
        rf = style.element.rPr.rFonts if style.element.rPr is not None else None
        fonts = {a: rf.get(qn('w:' + a)) for a in ('ascii', 'hAnsi', 'cs', 'eastAsia')} if rf is not None else None
        print(f'{style.name}: шрифт={f.name}, rFonts={fonts}, размер={f.size.pt if f.size else None}, интервал={p.line_spacing}, первая строка={p.first_line_indent}, выравнивание={p.alignment}, до/после={p.space_before}/{p.space_after}')
print('\n## Подписи и заголовки')
for p in doc.paragraphs:
    if p.style.name.startswith('Heading') or p.text.startswith(('Таблица ', 'Рисунок ', 'Листинг ')):
        print(f'{p.style.name}: {p.text}')
print('\n## Таблицы')
for i, table in enumerate(doc.tables, 1):
    h = table.rows[0]._tr.trPr if table.rows else None
    print(f'{i}: стиль={table.style.name}, строк={len(table.rows)}, повтор шапки={h is not None and h.find(qn("w:tblHeader")) is not None}, границы={"tblBorders" in table._tbl.xml}')
print('\nЧисло встроенных изображений:', len(doc.inline_shapes))
print('None означает отсутствие прямого значения: возможно наследование или прямое форматирование текста. Визуальную пагинацию и ссылки необходимо проверить отдельно.')
