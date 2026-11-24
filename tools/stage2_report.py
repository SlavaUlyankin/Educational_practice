from pathlib import Path
from docx import Document
from docx.shared import Pt, Mm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

root=Path('docs/report')
source=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_готово.docx'
output=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_этап2_готово.docx'
doc=Document(source)
anchor=next(p for p in doc.paragraphs if p.text.strip()=='СПИСОК ЛИТЕРАТУРЫ')

def para(text,style=None):
    p=anchor.insert_paragraph_before(style=style)
    p.add_run(text)
    for r in p.runs:
        r.font.name='Times New Roman';r.font.size=Pt(14)
        rf=r._element.get_or_add_rPr().get_or_add_rFonts()
        for a in ('ascii','hAnsi','cs','eastAsia'):rf.set(qn('w:'+a),'Times New Roman')
    if not style:
        p.paragraph_format.first_line_indent=Mm(12.5)
        p.paragraph_format.line_spacing=1.5
        p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    return p

def table(caption,headers,rows):
    p=para(caption,'Подпись таблиц ГОСТ');p.paragraph_format.keep_with_next=True
    t=doc.add_table(rows=1,cols=len(headers));t.style='Table Grid'
    for n,data in enumerate([headers]+rows):
        cells=t.rows[0].cells if n==0 else t.add_row().cells
        for c,value in zip(cells,data):
            p=c.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.space_after=Pt(0)
            p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.line_spacing=1
            run=p.add_run(value);run.bold=n==0;run.font.name='Times New Roman';run.font.size=Pt(10)
        trpr=t.rows[-1]._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    anchor._p.addprevious(t._tbl)

p=para('ГЛАВА 3. ОБЪЕКТНО-ОРИЕНТИРОВАННОЕ ПРОЕКТИРОВАНИЕ И ПРОГРАММНАЯ РЕАЛИЗАЦИЯ','Heading 1')
p.paragraph_format.page_break_before=True
para('3.1. ОБЪЕКТНАЯ МОДЕЛЬ РЕШЕНИЯ','Heading 2')
para('Объектная модель развивает логическую модель данных раздела 8 и алгоритмы А1–А5 раздела 9. Для каждой из десяти сущностей выделен отдельный предметный класс; операции распределены между сервисами бронирования, сеансов и оборудования. Проектируемый состав классов показан на рисунке 16 в приложении Б; основные поля, методы и связи приведены в таблице 15. Реализация Java-модуля выполняется на следующем этапе.')
classes=[
('Client','Клиент','id, fullName, phone, email, createdAt','Данные клиента; связь с Booking по clientId'),
('Game','Игровой формат','id, title, minPlayers, maxPlayers, allowsGroupMerge','Ограничения группы; связи с Tariff и Booking'),
('Tariff','Тариф','id, gameId, name, durationMin, price, active','Параметры сеанса; связь с Game и Booking'),
('Arena','Площадка','id, name, capacity, prepMin, active','Параметры площадки; связи с Booking и EquipmentSet'),
('Booking','Бронь','id, clientId, gameId, tariffId, arenaId, start, durationMin, players, status, sessionId','Хранение текущего состояния и ссылок на предметные объекты'),
('BookingHistory','Событие брони','id, bookingId, eventType, old/new time, old/new arena, changedAt, reason','Неизменяемый снимок события; связь с Booking и Arena'),
('Session','Сеанс','id, status, durationMin, startedAt, actualEndAt','Состояние и временные параметры; связь с Booking'),
('EquipmentSet','Комплект оборудования','id, arenaId, inventoryCode, kind, status','Учёт статуса; связь с Arena и журналом переходов'),
('SessionEquipment','Выдача комплекта','sessionId, equipmentId, issuedAt, returnedAt, condition','Связывает Session и EquipmentSet, хранит возврат'),
('EquipmentStatusLog','Запись статуса','equipmentId, oldStatus, newStatus, changedAt, comment','Фиксирует переход состояния комплекта'),
('BookingService','Бронирования','Clock, коллекции броней, истории и комплектов','checkSlot, create, cancel, reschedule, markNoShow; А1 и А5'),
('SessionService','Жизненный цикл сеанса','Clock, сеансы и связанные брони','start, timeState, finish; А2'),
('EquipmentService','Оборудование','Clock, комплекты, выдачи и журнал','changeStatus, issue, returnEquipment, replace; А3 и А4'),
('Перечисления','Ограниченные состояния','BookingStatus, BookingEventType, SessionStatus, EquipmentStatus, EquipmentKind','Значения состояний и событий без произвольных строк'),
('Clock','Источник времени','java.time.Clock','instant; внедряется в сервисы для воспроизводимых тестов')]
table('Таблица 15 — Основные классы и распределение ответственности',['Класс','Назначение','Основные данные','Методы и связи'],classes)
para('Сервисы получают зависимости через конструктор и работают с переданными коллекциями в памяти. BookingService проверяет площадку и конфликт расписания, а успешные операции фиксирует в BookingHistory; отклонённый перенос не изменяет бронь. SessionService управляет состоянием и временем сеанса; EquipmentService проверяет переходы статусов и фиксирует выдачу и возврат. Для денежных значений предполагается BigDecimal, для моментов времени — java.time; правила часового пояса должны быть определены при реализации.')
para('Композиция используется для организации сервисов вокруг переданных зависимостей. Наследование между предметными классами не вводится: их обязанности различаются, а общая иерархия не добавляет полезного поведения. Вместо собственного интерфейса времени используется абстрактный класс java.time.Clock из JDK; дальнейшие интерфейсы хранилищ целесообразно вводить при появлении альтернативных реализаций хранения.')
para('3.2. СВЯЗЬ ОБЪЕКТНОЙ МОДЕЛИ С АЛГОРИТМАМИ И ПРОЦЕССОМ','Heading 2')
para('Трассировка проектируемых методов к алгоритмам, элементам BPMN и сущностям логической модели представлена в таблице 16. Методы и связи являются проектным решением: их соответствие исполняемому Java-коду проверяется после реализации.')
rows=[('А1 — доступность','BookingService.checkSlot, create','SP1, A1.3','Booking, Arena, EquipmentSet, Game, Tariff'),('А2 — время','SessionService.start, timeState, finish','SP4, D4.2–D4.6','Session, Booking, Tariff'),('А3 — статусы','EquipmentService.changeStatus, issue, replace','SP3, ESP2, SP6','EquipmentSet, EquipmentStatusLog, SessionEquipment'),('А4 — возврат','EquipmentService.returnEquipment','SP4, SP6','Session, SessionEquipment, EquipmentSet, EquipmentStatusLog'),('А5 — отмена и перенос','BookingService.cancel, reschedule, markNoShow','ESP1, X1.7, X1.14, X1.15; SP2','Booking, BookingHistory, Arena, EquipmentSet')]
table('Таблица 16 — Трассировка алгоритмов и классов',['Алгоритм','Классы и методы','Элементы BPMN','Сущности'],rows)
para('При изменении времени и площадки сервис сначала проверяет возможность переноса, затем обновляет бронь и добавляет запись истории. Для отмены и неявки сохраняются прежние значения. Физическая база данных, конкурентная запись и интеграция с платёжной системой в проектируемое ядро не входят.')

p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.page_break_before=True;p.paragraph_format.keep_with_next=True
p.add_run().add_picture('docs/figures/uml_stage2.png',width=Mm(150))
p=doc.add_paragraph(style='Подпись рисунка ГОСТ');r=p.add_run('Рисунок 16 — Проектируемая объектная модель Java-модуля');r.font.name='Times New Roman';r.font.size=Pt(14)
doc.save(output);Document(output)
