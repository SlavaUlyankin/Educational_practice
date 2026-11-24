from pathlib import Path
from docx import Document
from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

root=Path('docs/report')
source=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_этап2_готово.docx'
output=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_этап3_готово.docx'
doc=Document(source)
anchor=next(p for p in doc.paragraphs if p.text.strip()=='СПИСОК ЛИТЕРАТУРЫ')
def paragraph(text,style=None):
    p=anchor.insert_paragraph_before(style=style);r=p.add_run(text);r.font.name='Times New Roman';r.font.size=Pt(14)
    fonts=r._element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ('ascii','hAnsi','cs','eastAsia'):fonts.set(qn('w:'+attr),'Times New Roman')
    if not style:
        p.paragraph_format.first_line_indent=Mm(12.5);p.paragraph_format.line_spacing=1.5;p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    return p

paragraph('3.3. ПРОГРАММНАЯ РЕАЛИЗАЦИЯ JAVA-МОДУЛЯ','Heading 2')
paragraph('Объектная модель раздела 3.1 реализована в Maven-проекте java. Исходный код хранится в репозитории проекта: https://github.com/SlavaUlyankin/Educational_practice. Модуль содержит десять предметных классов, перечисления состояний, сервисы BookingService, SessionService и EquipmentService, демонстрационный класс Demo и тесты JUnit 5. Состояние и журналы хранятся в оперативной памяти; база данных и обработка платежей в модуле отсутствуют.')
paragraph('BookingService проверяет доступность слота, оформляет и переносит бронь, фиксирует отмену и неявку. При успешной операции создаётся запись BookingHistory, содержащая тип события, время, причину и прежнее и новое состояние при переносе. При недоступности выбранного времени бронирование не меняется; в случае конфликта предлагаются варианты в пределах четырёх часов с шагом 15 минут. Фрагмент создания записи журнала приведён в листинге 3.')
caption=paragraph('Листинг 3 — Создание записи истории брони (BookingService, фрагмент)','Подпись таблиц ГОСТ')
caption.paragraph_format.page_break_before=True;caption.paragraph_format.keep_with_next=True
code='''long next = history.stream().mapToLong(BookingHistory::id)
        .max().orElse(0) + 1;
history.add(new BookingHistory(next, b.id, event, at,
        oldStart, newStart, oldArena, newArena, reason));'''
for index,line in enumerate(code.splitlines()):
    p=anchor.insert_paragraph_before();p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1
    p.paragraph_format.keep_with_next=index<len(code.splitlines())-1
    r=p.add_run(line);r.font.name='Consolas';r.font.size=Pt(10)
    fonts=r._element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ('ascii','hAnsi','cs','eastAsia'):fonts.set(qn('w:'+attr),'Consolas')
paragraph('SessionService запускает и завершает сеанс, вычисляет состояние времени и превышение. EquipmentService проверяет разрешённые переходы статусов, выполняет выдачу, замену и возврат; перед возвратом проверяются условия для всех комплектов. Сервисы получают java.time.Clock, что позволяет воспроизводимо проверять границы времени. Состав предметных классов и названия сервисных методов соответствуют проектной модели на рисунке 16 и в таблицах 15–16.')
paragraph('Для сборки и проверки из каталога java выполняется команда mvn -q test; запуск демонстрации после компиляции — java -cp target/classes ru.mirea.vrarena.Demo. Проверка Maven выполнена с JetBrains Runtime 25 при целевой версии компиляции Java 17: девять тестов JUnit завершились без ошибок и пропусков. Демонстрация выполнила создание и отмену брони, обнаружение конфликта, перенос, контроль времени сеанса, замену и возврат оборудования и отметку неявки. Отдельный запуск на JDK 17 на момент проверки не выполнялся.')
paragraph('В отличие от исходного Python-прототипа Java-модуль дополнительно проверяет активность площадки и ограничение её вместимости. Обе реализации хранят состояние в памяти и не обеспечивают конкурентную запись. Сопоставление процедурного и объектно-ориентированного подходов выполняется на следующем этапе.')
doc.save(output);Document(output)
