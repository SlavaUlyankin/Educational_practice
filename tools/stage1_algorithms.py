"""Согласование разделов 9–10 с проверенным прототипом."""
from copy import deepcopy
from pathlib import Path
from docx import Document

target_path = Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
source_path = Path(r'C:\Учебная практика 5 сем Codex\Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
target, source = Document(target_path), Document(source_path)

def bounds(doc):
    nodes = list(doc.element.body)
    def text(n):
        return ''.join(t.text or '' for t in n.xpath('.//w:t'))
    a = next(i for i, n in enumerate(nodes) if text(n).startswith('9. АЛГОРИТМЫ РЕШЕНИЯ ЗАДАЧИ'))
    b = next(i for i in range(a+1, len(nodes)) if text(nodes[i]).startswith('11. ПЕРЕВОД ФРАГМЕНТА'))
    return nodes, a, b

dst, a, b = bounds(target)
src, x, y = bounds(source)
anchor = dst[b]
for node in dst[a+1:b]:
    target.element.body.remove(node)
for node in src[x+1:y]:
    anchor.addprevious(deepcopy(node))

for p in target.paragraphs:
    if p.text.startswith('Работоспособность реализации подтверждена двумя способами.'):
        p.clear()
        p.add_run('Работоспособность реализации проверена набором из 84 тест-кейсов (tests/cases.py и tests/stage1_cases.py): команда python run_cases.py показала 84 совпадения и отсутствие ошибок. Команда python -m unittest discover выполнила 8 тестов успешно, включая проверки сохранения истории. Примеры приведены в таблице 12.')
    if p.text.startswith('Глоссарий'):
        pass
    if p.text == '11.3. Глоссарий':
        continue
    if p.text.startswith('Таблица 13 — Глоссарий'):
        p.insert_paragraph_before('Основные термины переведённого фрагмента представлены в таблице 13.')
    if p.text.startswith('Программный код процедурной реализации алгоритмов (раздел 10) размещён'):
        for r in p.runs:
            if '76 тест-кейсам' in r.text:
                r.text = r.text.replace('76 тест-кейсам', '84 тест-кейсам')
target.save(target_path)
Document(target_path)
