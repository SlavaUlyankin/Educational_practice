from pathlib import Path
from docx import Document
from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root=Path('docs/report')
source=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_этап3_готово.docx'
output=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_ООП_итог.docx'
doc=Document(source)
anchor=next(p for p in doc.paragraphs if p.text.strip()=='СПИСОК ЛИТЕРАТУРЫ')

for p in doc.paragraphs:
    for r in p.runs:
        old='Сопоставление процедурного и объектно-ориентированного подходов выполняется на следующем этапе.'
        if old in r.text:r.text=r.text.replace(old,'Сопоставление подходов приведено в разделе 3.5.')

def paragraph(text,style=None):
    p=anchor.insert_paragraph_before(style=style);r=p.add_run(text)
    r.font.name='Times New Roman';r.font.size=Pt(14)
    fonts=r._element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ('ascii','hAnsi','cs','eastAsia'):fonts.set(qn('w:'+attr),'Times New Roman')
    if not style:
        p.paragraph_format.first_line_indent=Mm(12.5);p.paragraph_format.line_spacing=1.5;p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    return p

def table(caption,headers,rows):
    caption_p=paragraph(caption,'Подпись таблиц ГОСТ');caption_p.paragraph_format.keep_with_next=True
    t=doc.add_table(rows=1,cols=len(headers));t.style='Table Grid'
    for i,values in enumerate([headers]+rows):
        cells=t.rows[0].cells if i==0 else t.add_row().cells
        for cell,value in zip(cells,values):
            p=cell.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(0)
            r=p.add_run(value);r.bold=(i==0);r.font.name='Times New Roman';r.font.size=Pt(10)
        t.rows[-1]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    anchor._p.addprevious(t._tbl)
    return caption_p

paragraph('3.4. ДЕМОНСТРАЦИЯ РАБОТЫ JAVA-МОДУЛЯ','Heading 2')
paragraph('Консольный сценарий Demo воспроизводит рабочий цикл на вымышленных данных при фиксированных моментах времени. После создания броней выполняется проверка конфликта, попытка переноса на занятое время, отмена другой брони и повторный перенос. Далее регистрируются выдача и замена комплекта, превышение времени сеанса, возврат и неявка. Фактический вывод программы приведён в листинге 4 и сохранён в репозитории в файле docs/java_demo_этап3.txt.')
cap=paragraph('Листинг 4 — Фактический вывод Java-демонстрации','Подпись таблиц ГОСТ');cap.paragraph_format.keep_with_next=True
lines=Path('docs/java_demo_этап3.txt').read_text(encoding='utf-8').splitlines()
assert len(lines)>=10 and 'Конфликт 19:00: CONFLICT' in lines[1] and 'Неявка брони 3: NO_SHOW' in lines[9]
listing=anchor.insert_paragraph_before();listing.paragraph_format.first_line_indent=Pt(0);listing.paragraph_format.line_spacing=1;listing.paragraph_format.keep_together=True
run=listing.add_run('\n'.join(lines));run.font.name='Consolas';run.font.size=Pt(10)
rf=run._element.get_or_add_rPr().get_or_add_rFonts()
for attr in ('ascii','hAnsi','cs','eastAsia'):rf.set(qn('w:'+attr),'Consolas')
paragraph('Конфликтующий перенос не изменил бронь; после отмены другой брони повторная проверка позволила выполнить перенос. Состояние TIME_UP зафиксировано с превышением две минуты. После отметки неявки в демонстрационном сценарии журнал бронирований содержит шесть событий: три создания, отмену, перенос и неявку.')
paragraph('3.5. СОПОСТАВЛЕНИЕ ПРОЦЕДУРНОГО И ОБЪЕКТНО-ОРИЕНТИРОВАННОГО ПОДХОДОВ','Heading 2')
paragraph('Обе реализации решают одну задачу — проверку доступности слота и перенос брони с сохранением истории. Процедурный прототип написан на Python, объектная версия — на Java; поэтому при сопоставлении следует учитывать не только распределение ответственности, но и различия языков, используемых типов и инструментов. Результаты сравнения приведены в таблице 17.')
rows=[
('Данные и операции','Структуры dataclass определены в models.py; функции проверки и переноса расположены в a1_slots.py и a4_bookings.py.','Предметные классы хранят данные; BookingService объединяет проверку и операции, SessionService и EquipmentService — остальные обязанности.','В первом варианте связи между функциями видны через параметры; во втором общие зависимости задаются конструктору сервиса.'),
('Проверка и перенос','check_slot_availability принимает время, длительность, состав группы, брони, комплекты и идентификатор площадки; reschedule_booking вызывает проверку и запись истории.','checkSlot получает Game и Arena; reschedule вызывает проверку, изменяет бронь и записывает BookingHistory при успехе.','Обе версии исключают собственную бронь и сохраняют её при отказе. Java дополнительно проверяет активность и вместимость площадки.'),
('Время и проверка','Текущее время now явно передаётся в функции; сценарии задаются в tests/cases.py и tests/stage1_cases.py.','Сервисы получают java.time.Clock; в JUnit используется управляемый источник времени.','Оба способа позволяют воспроизводить пограничные условия; выбор механизма связан также с возможностями языка и библиотек.'),
('Новый статус комплекта','Добавить значение EquipmentStatus и допустимые пары в ALLOWED_TRANSITIONS; скорректировать функции и тесты для затронутых операций.','Добавить значение EquipmentStatus и ветви разрешённых переходов в EquipmentService.changeStatus; обновить затронутые операции и тесты.','Изменение затрагивает перечисление и правила переходов в обоих вариантах; единая функция смены статуса помогает искать место изменения.'),
('Вторая площадка','Добавить данные площадки, указать arena_id у броней и комплектов и передавать нужный prep_min при проверке.','Создать Arena с вместимостью и prepMin, присвоить arenaId броням и комплектам и передать Arena сервису.','Изоляция расписаний предусмотрена обеими реализациями. Java проверяет вместимость и активность; Python-прототип эти проверки не выполняет.'),
('Результаты и ограничения','Функции возвращают коды и структуры результата; списки передаются явно.','Проверка слота возвращает SlotResult, операции также используют исключения; сущности и сервисы разделены.','Обе версии работают в памяти и не обеспечивают конкурентную запись. Удобство сопровождения зависит от размера задачи и дисциплины изменения кода.')]
caption=table('Таблица 17 — Сопоставление реализаций на примере бронирования',['Аспект','Python','Java','Следствие'],rows)
caption.paragraph_format.page_break_before=True
conclusion=paragraph('Процедурное решение удобно для небольшого набора алгоритмов и явной передачи данных между функциями. Объектная версия группирует операции и зависимости по областям ответственности, что облегчает поиск места изменения при расширении модели, но добавляет классы и связи. Эти наблюдения относятся к конкретным реализациям; различия строгой типизации, стандартных библиотек и инструментария языков нельзя приписывать одному только способу организации кода.')
conclusion.paragraph_format.keep_together=True
doc.save(output);Document(output)
