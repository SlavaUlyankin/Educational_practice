"""Точечные исправления фраз, разделённых на несколько run в Word."""
from pathlib import Path
from docx import Document

path = Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
doc = Document(path)
changes = {
    'warn_min = 0 — любой активный сеанс сразу переходит в ENDING_SOON': 'warn_min = 0 — предупреждение ENDING_SOON не возникает до завершения сеанса',
    'Сложность O(k), где k — число выданных в сеансе комплектов (как правило, равно числу игроков); обращение к conditions по идентификатору — за константное время.': 'Сложность O(r + k), где r — число проверяемых строк выдачи, k — число комплектов; обращение к словарям по идентификатору занимает в среднем константное время.',
}
for old, new in changes.items():
    found = [p for p in doc.paragraphs if old in p.text]
    if found:
        assert len(found) == 1
        p = found[0]
        text = p.text.replace(old, new)
        p.clear(); p.add_run(text)
doc.save(path)
Document(path)
