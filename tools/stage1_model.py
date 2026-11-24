"""Перенос раздела логической модели в рабочую копию отчёта."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn

target_path = Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
source_path = Path(r'C:\Учебная практика 5 сем Codex\Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
target = Document(target_path)
source = Document(source_path)

def section(doc):
    body = doc.element.body
    children = list(body)
    def text(node):
        return ''.join(node.xpath('.//w:t')) if False else ''.join(t.text or '' for t in node.xpath('.//w:t'))
    start = next(i for i, node in enumerate(children) if text(node).startswith('8. ЛОГИЧЕСКАЯ МОДЕЛЬ ДАННЫХ'))
    end = next(i for i in range(start + 1, len(children)) if text(children[i]).startswith('9. АЛГОРИТМЫ РЕШЕНИЯ ЗАДАЧИ'))
    return body, children, start, end

dst_body, dst, ds, de = section(target)
_, src, ss, se = section(source)
reference = dst[de]
for node in dst[ds + 1:de]:
    dst_body.remove(node)
for node in src[ss + 1:se]:
    new = deepcopy(node)
    for blip in new.xpath('.//a:blip'):
        old_id = blip.get(qn('r:embed'))
        if old_id:
            image_part = source.part.related_parts[old_id]
            new_id, _ = target.part.get_or_add_image(BytesIO(image_part.blob))
            blip.set(qn('r:embed'), new_id)
    reference.addprevious(new)

for p in target.paragraphs:
    for run in p.runs:
        updated = run.text.replace('Таблица 10 — Глоссарий', 'Таблица 13 — Глоссарий')
        updated = updated.replace('таблице 10 приведён глоссарий', 'таблице 13 приведён глоссарий')
        updated = updated.replace('кто и когда вывел комплект из эксплуатации и почему', 'когда комплект был выведен из эксплуатации и почему')
        if updated != run.text:
            run.text = updated
target.save(target_path)
Document(target_path)
