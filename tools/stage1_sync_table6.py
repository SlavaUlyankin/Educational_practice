from pathlib import Path
from docx import Document

path=Path('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4.docx')
doc=Document(path)
t=next(t for t in doc.tables if t.cell(0,0).text == 'Операция' and len(t.columns)==7)
edits={
    (1,3):'проверяет пересечение интервалов подтверждённых броней выбранной площадки и число её комплектов, не отмеченных неисправными; конфликтующая заявка отклоняется',
    (1,4):'помогает выявить конфликт расписания при последовательной работе одного оператора',
    (1,6):'booking, arena, equipment_set',
    (2,3):'проверяет возможность переноса; успешные перенос и отмена изменяют бронь и фиксируются в истории; при конфликте предлагаются альтернативы',
    (2,4):'изменения брони и освобождение прежнего интервала становятся прослеживаемыми',
    (2,6):'booking, arena, booking_history, equipment_set',
    (3,4):'администратор получает сведения об оставшемся времени и превышении',
    (5,4):'переходы статусов проверяются; при выдаче выбираются комплекты со статусом available',
}
for (row,col),text in edits.items():
    cell=t.cell(row,col);p=cell.paragraphs[0];p.clear();p.add_run(text)
    for extra in cell.paragraphs[1:]: extra._element.getparent().remove(extra._element)
doc.save(path);Document(path)
