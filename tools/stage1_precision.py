from pathlib import Path
from docx import Document

path = Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
doc = Document(path)
changes = {
    'warn_min = 0 — любой активный сеанс сразу переходит в ENDING_SOON': 'warn_min = 0 — состояние ENDING_SOON не возникает до окончания сеанса',
    'Сложность O(k), где k — число выданных в сеансе комплектов (как правило, равно числу игроков); обращение к conditions по идентификатору — за константное время.': 'Сложность O(r + k), где r — число просматриваемых строк выдачи, k — число комплектов в списке; поиск по построенному словарю и обращение к conditions выполняются в среднем за константное время.',
    'в history добавляется событие rescheduled со старыми и новыми временем и ареной': 'в историю брони добавляется событие rescheduled со старыми и новыми временем и ареной; при передаче общего журнала оно также добавляется в него',
}
for p in doc.paragraphs:
    if p.text.startswith('Соответствие алгоритмов схемам проверено покомандно:'):
        p.clear()
        p.add_run('Программная реализация алгоритмов описана в разделе 10.')
    for r in p.runs:
        updated = r.text
        for old, new in changes.items():
            updated = updated.replace(old, new)
        if updated != r.text:
            r.text = updated
doc.save(path)
Document(path)
