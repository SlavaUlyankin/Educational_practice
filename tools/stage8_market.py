from pathlib import Path
from shutil import copy2
from docx import Document
from docx.shared import Pt, Cm, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root=Path('docs/report')
src=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_рецензия.docx'
dst=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_рынок.docx'
copy2(src,root/'backups/этап4_перед_этапом8.docx')
d=Document(src)
anchor=next(p for p in d.paragraphs if p.text.strip()=='СПИСОК ЛИТЕРАТУРЫ')
def font(r,size=14):
    r.font.name='Times New Roman';r.font.size=Pt(size)
    rf=r._element.get_or_add_rPr().get_or_add_rFonts()
    for a in ('ascii','hAnsi','cs','eastAsia'):rf.set(qn('w:'+a),'Times New Roman')
def insert(text,style=None,caption=False):
    p=d.add_paragraph(text,style=style);anchor._p.addprevious(p._p)
    p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(0)
    p.paragraph_format.line_spacing=1.5;p.paragraph_format.first_line_indent=Cm(0 if style or caption else 1.25)
    p.alignment=WD_ALIGN_PARAGRAPH.LEFT if style or caption else WD_ALIGN_PARAGRAPH.JUSTIFY
    if style or caption:p.paragraph_format.keep_with_next=True
    for r in p.runs:font(r)
    return p
insert('4.4 Анализ требований рынка труда',style='Heading 2')
insert('Для профессионального развития выбрано направление серверной Java-разработки: Java-модуль проекта реализует предметную логику бронирования и сеансов VR-арены, а физическая модель данных на следующем этапе продолжает развитие этого решения. Целевая роль — junior Java backend developer с последующим ростом до middle.')
insert('Для сравнения изучены пять публикаций вакансий: две начального уровня и три уровня middle. Публикация БФТ-Холдинга размещена на площадке работодателем; остальные изучены по материалам сайтов вакансий, включая перепечатки. Сведения зафиксированы на 24.11.2026; актуальность вакансий и оригинальность перепечаток при последующем использовании следует проверять. Выборка небольшая и не является статистическим исследованием рынка. Результаты сведены в таблицу 21 [16][17][18][19][20].')
insert('Таблица 21 — Сравнение вакансий Java backend-разработчика',caption=True)
rows=[
('Ontory [16]','Junior','Доработка серверного кода, исправление ошибок и интеграции.','Java, ООП, коллекции, исключения, основы SQL и Spring, понимание REST; учебный проект указан как преимущество.'),
('X5 Tech [17]','Intern / junior','Разработка по заданиям, модульные тесты, сопровождение и устранение дефектов.','Java и Spring либо другой язык с готовностью развиваться в Java/Kotlin; Git, основы SQL и сервисной архитектуры.'),
('БФТ-Холдинг [18]','Middle','Разработка и поддержка сервисов, интеграции, оптимизация кода и анализ сбоев.','От трёх лет коммерческого опыта; Java 11+, Spring, Maven, Git, PostgreSQL/Cassandra, Kafka/RabbitMQ, основы CI/CD.'),
('ИЦ АЙ-ТЕКО [19]','Middle','Разработка серверных и интеграционных сервисов, проектирование схем PostgreSQL.','Java 8+, Spring Boot, Hibernate, PostgreSQL, Kafka, Docker, Kubernetes/OpenShift; заявлен опыт 3–6 лет.'),
('Ренью [20]','Middle','Развитие серверного функционала, интеграции, тесты и участие в выпусках.','От трёх лет Java и Spring Boot; PostgreSQL, оптимизация SQL, Docker, Kubernetes, GitLab CI, Kafka.')]
t=d.add_table(rows=1,cols=4);t.style=d.tables[20].style;t.autofit=False
widths=(30,25,52,63)
for c,w in zip(t.columns,widths):c.width=Mm(w)
for c,s in zip(t.rows[0].cells,('Работодатель','Уровень','Задачи','Требования и стек')):c.text=s
for data in rows:
    for c,s in zip(t.add_row().cells,data):c.text=s
for ri,row in enumerate(t.rows):
    row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    for cell,w in zip(row.cells,widths):
        cell.width=Mm(w)
        for p in cell.paragraphs:
            p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.line_spacing=1.0;p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.space_after=Pt(0)
            for r in p.runs:font(r,11);r.bold=(ri==0)
t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
anchor._p.addprevious(t._tbl)
insert('Во всех пяти рассмотренных публикациях встречаются Java и Spring; базы данных или SQL также присутствуют во всех пяти. Git прямо указан в публикациях X5 Tech и БФТ-Холдинга, а Kafka — в трёх рассмотренных вакансиях middle. Эти наблюдения относятся только к выбранным объявлениям и не позволяют оценить частоту требований на рынке в целом [16]–[20].')
insert('На начальном уровне в выбранной паре вакансий внимание уделяется основам языка, работе с существующим кодом, SQL, тестам и готовности учиться. В трёх вакансиях middle дополнительно заявлен многолетний коммерческий опыт и практическая работа с интеграциями и инфраструктурой: брокерами сообщений, контейнерами или средствами развёртывания. Разница не абсолютна: стек и границы ответственности определяет конкретная команда [16]–[20].')
insert('В учебной работе уже применены объектное проектирование и Java: классы и сервисы показаны в разделе 3.1 и на рисунке 16, реализация — в разделе 3.3. Практика тестирования подтверждается 84 сценариями Python, 11 тестами unittest и 15 тестами JUnit; моделирование данных и алгоритмов — ER-моделью на рисунке 10 и разделом 9. Работа с Git отражена в структуре репозитория. Эти результаты подтверждают учебную практику, но не заменяют коммерческий опыт или опыт эксплуатации распределённых сервисов.')
insert('Для перехода к целевой роли следует прежде всего освоить Spring Boot и разработку REST API, практический SQL и PostgreSQL, затем закрепить интеграционное тестирование, Docker и основы CI/CD. Работа с Kafka и масштабированием относится к последующему углублению. Следующая контрольная точка практики — физическая модель данных — позволяет связать логическую ER-модель с PostgreSQL; подключение Spring Data JPA рассматривается как дальнейшее развитие, а не как уже реализованная часть проекта.')

appendix=next(p for p in d.paragraphs if p.text.strip()=='Приложение А')
refs=[
'16. Ontory. Junior Java Developer [Электронный ресурс] // Jabka. URL: https://jabka.work/jobs/junior-java-developer-ontory-20261119-j8lo (дата обращения: 24.11.2026).',
'17. X5 Tech. Intern Junior разработчик [Электронный ресурс] // Hack Offer, перепечатка объявления. URL: https://hack-offer.tech/vacancy/31377-intern-junior-razrabotchik (дата обращения: 24.11.2026).',
'18. БФТ-Холдинг. Java-разработчик [Электронный ресурс] // Хабр Карьера. URL: https://career.habr.com/vacancies/1000165768 (дата обращения: 24.11.2026).',
'19. ИЦ АЙ-ТЕКО. JAVA Middle-разработчик [Электронный ресурс] // Young&Junior, перепечатка объявления. URL: https://youngjunior.ru/backend/jobs/99424 (дата обращения: 24.11.2026).',
'20. Ренью. Backend разработчик Java (Middle) [Электронный ресурс] // Вакандия. URL: https://vakandia.ru/vacancy/backend-razrabotchik-java-middle-23421-563304 (дата обращения: 24.11.2026).']
for text in refs:
    p=d.add_paragraph(text);appendix._p.addprevious(p._p)
    p.paragraph_format.line_spacing=1.5;p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(0)
    p.paragraph_format.first_line_indent=Cm(1.25);p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p.runs:font(r)
d.save(dst)
check=Document(dst)
assert any(p.text.startswith('4.4 Анализ требований') for p in check.paragraphs)
assert all(any(p.text.startswith(str(n)+'. ') for p in check.paragraphs) for n in range(16,21))
print('Saved',dst)
