from copy import deepcopy
from pathlib import Path
import re, shutil
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Pt, Mm, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image

root=Path('docs/report')
src=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_организация.docx'
out=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_рецензия.docx'
review_path=Path('C:/Users/Slava/Downloads/Telegram Desktop/ЗиминЕА_рецензия_УльянкинВИ.docx')
review_md=review_path.with_suffix('.md')
(root/'backups').mkdir(exist_ok=True)
shutil.copy2(src,root/'backups/этап4_перед_этапом7.docx')
Path('docs/reviews').mkdir(exist_ok=True)
shutil.copy2(review_path,Path('docs/reviews')/review_path.name)
shutil.copy2(review_md,Path('docs/reviews')/review_md.name)
d=Document(src); review=Document(review_path)

def replace(p,old,new):
    nodes=p.xpath('.//w:t'); full=''.join(n.text or '' for n in nodes)
    assert old in full, old
    for m in reversed(list(re.finditer(re.escape(old),full))):
        start,end=m.span(); offset=0; first=last=None
        for node in nodes:
            n=len(node.text or '')
            if first is None and start<offset+n: first=node;lo=start-offset
            if first is not None and end<=offset+n: last=node;hi=end-offset;break
            offset+=n
        if first is last: first.text=(first.text or '')[:lo]+new+(first.text or '')[hi:]
        else:
            first.text=(first.text or '')[:lo]+new; between=False
            for node in nodes:
                if node is first: between=True;continue
                if between and node is last: node.text=(node.text or '')[hi:];break
                if between: node.text=''

allp=d.element.body.xpath('.//w:p')
def sub(old,new):
    found=[p for p in allp if old in ''.join(x.text or '' for x in p.xpath('.//w:t'))]
    assert found,old
    for p in found: replace(p,old,new)
sub('со статусом, отличным от faulty','с текущим статусом available')
sub('не отмеченных неисправными','со статусом available на момент проверки')
sub('kit.status != EquipmentStatus.FAULTY','kit.is_available_for_issue()')
sub('Команда python -m unittest discover выполнила 8 тестов успешно','Команда python -m unittest discover выполнила 11 тестов успешно')
sub('девять тестов JUnit завершились','пятнадцать тестов JUnit завершились')
sub('Вызывается ПРОВЕРИТЬ_СЛОТ для new_start','Если время и площадка не изменились, возвращается OK без записи в историю. Иначе вызывается ПРОВЕРИТЬ_СЛОТ для new_start')
sessionrow=next(r for r in d.tables[20].rows if r.cells[0].text.strip()=='Session')
sessionrow.cells[2].text='id, bookingId, arenaId, playersCount, status, durationMin, startedAt, actualEndAt'
sessionrow.cells[3].text='Состояние сеанса и снимок площадки связанной брони'

for caption,path,maxwidth,maxheight in [('Рисунок 11','docs/figures/a1_stage1.png',155,210),('Рисунок 15','docs/figures/a5_stage1.png',155,210),('Рисунок 16','docs/figures/uml_stage2.png',150,190)]:
    p=next(p for p in d.paragraphs if p.text.startswith(caption)); el=p._p.getprevious()
    while el is not None and not el.xpath('.//a:blip'):el=el.getprevious()
    assert el is not None,caption
    rid,_=d.part.get_or_add_image(path)
    el.xpath('.//a:blip')[0].set(qn('r:embed'),rid)
    w,h=Image.open(path).size; width=min(maxwidth,maxheight*w/h); height=width*h/w
    for e in el.xpath('.//wp:extent | .//a:xfrm/a:ext'):
        e.set('cx',str(Mm(width).emu));e.set('cy',str(Mm(height).emu))

items=[
('H-1','Исправлено','Проверка слота и выдача учитывают только комплекты со статусом available на момент проверки. Прогноз будущего состояния и резервирование комплектов не реализованы.'),
('H-2','Частично исправлено','Java-сеанс связан с конкретной бронью и её площадкой; выдача и замена ограничены этой площадкой. В Python площадка учитывается, но связь с существующей бронью не гарантируется.'),
('H-3','Частично исправлено','Завершение Java-сеанса возвращает плановое и фактическое время и превышение. События начала и завершения в историю брони пока не добавлены.'),
('H-4','Исправлено','Результат замены явно показывает, зафиксирована ли неисправность, найден ли резерв и какова причина отказа.'),
('H-5','Частично исправлено','Отмена Java-брони возвращает записанную сумму предоплаты для ручного решения. Платежи, возвраты и обязательность предоплаты не реализованы.'),
('H-6','Отложено','Допустимый интервал запуска сеанса должен быть определён заказчиком; произвольное правило не вводилось.'),
('H-7','Частично принято','Поиск альтернатив вперёд сохранён согласно исходным параметрам алгоритма; выдача альтернатив при создании брони отложена.'),
('H-8','Отложено','Единый формат ошибок требует отдельного проектирования интерфейса сервисов.'),
('H-9','Частично исправлено','Java-сервис проверяет принадлежность брони коллекции и соответствие сеанса броне. Инкапсуляция коллекций и параллельная работа не реализованы.'),
('H-10','Исправлено','Перенос на прежние время и площадку возвращает OK без лишнего события истории в Python и Java.'),
('H-11','Отложено','Правила округления неполных минут и расчёта оплаты требуют согласования; автоматический расчёт оплаты не реализован.'),
('H-12','Частично исправлено','Основные числовые параметры поиска и ожидания в Java вынесены в именованные константы; типизацию условий возврата и расширение инвариантов истории можно улучшить отдельно.'),
('H-13','Отложено','Снимок интервала подготовки в брони требует изменения модели и согласования правил хранения.')]

anchor=next(p for p in d.paragraphs if p.text.strip()=='СПИСОК ЛИТЕРАТУРЫ')
def insert(text,style=None):
    p=d.add_paragraph(text,style=style);anchor._p.addprevious(p._p)
    p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(0)
    p.paragraph_format.line_spacing=1.5
    p.paragraph_format.first_line_indent=Cm(1.25) if style is None and not text.startswith('Таблица') else Cm(0)
    if style is None and not text.startswith('Таблица'):p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    if style or text.startswith('Таблица'):p.paragraph_format.keep_with_next=True
    for r in p.runs:
        r.font.name='Times New Roman';r.font.size=Pt(14)
        for a in ('ascii','hAnsi','cs','eastAsia'):r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:'+a),'Times New Roman')
    return p
insert('4.3 Анализ полученной рецензии', 'Heading 2')
insert('Получена рецензия Зимина Егора Алексеевича на версию проекта 92b087de5f2fe29dab54c7ccfa418fc02f4f616e. Полный текст рецензии приведён в приложении В. Проверки, указанные в рецензии, относятся к исходной проверенной версии. Решения по замечаниям приведены в таблице 20.')
insert('Таблица 20 — Результаты анализа замечаний рецензента')
t=d.add_table(rows=1,cols=3);t.style=d.tables[20].style;t.autofit=False
for col,width in zip(t.columns,(18,37,110)):col.width=Mm(width)
for c,txt in zip(t.rows[0].cells,('№','Решение','Результат и ограничения')):c.text=txt
for row in items:
    cells=t.add_row().cells
    for c,txt in zip(cells,row): c.text=txt
for row in t.rows:
    row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    for cell,width in zip(row.cells,(18,37,110)):
        cell.width=Mm(width)
        for p in cell.paragraphs:
            p.paragraph_format.space_after=Pt(0)
            p.paragraph_format.line_spacing=1.0;p.paragraph_format.first_line_indent=Cm(0);p.alignment=WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name='Times New Roman';run.font.size=Pt(12)
                for a in ('ascii','hAnsi','cs','eastAsia'):run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:'+a),'Times New Roman')
t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
anchor._p.addprevious(t._tbl)
insert('После исправлений проверены 84 сценария Python, 11 тестов unittest и 15 тестов JUnit. Проверка Java выполнена с JetBrains Runtime 25 при целевой версии компиляции Java 17; отдельный запуск на JDK 17 не выполнялся. Рецензирование проекта напарника не проводилось: на момент работы его исходный код не был предоставлен.')
insert('Проверка доступности комплектов использует текущее состояние оборудования и не предсказывает его состояние на будущий слот. Хранение данных остаётся в памяти, обработка платежей и многопользовательская синхронизация не реализованы.')

d.add_page_break();p=d.add_paragraph('Приложение В');p.alignment=1
for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(14)
p=d.add_paragraph('Рецензия Зимина Е. А. на программный код');p.alignment=1
for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(14)
# Copy source list definitions, then remap numbering and external hyperlinks.
sn=review.part.numbering_part.element;dn=d.part.numbering_part.element
def maxid(tag,attr):
    vals=[int(x.get(qn('w:'+attr))) for x in dn.findall(qn('w:'+tag))]
    return max(vals,default=0)
num_map={};abs_map={}; nextnum=maxid('num','numId')+1; nextabs=maxid('abstractNum','abstractNumId')+1
for el in review.element.body.xpath('.//w:numId'):
    old=el.get(qn('w:val'))
    if old in num_map or old=='0':continue
    original=next(x for x in sn.findall(qn('w:num')) if x.get(qn('w:numId'))==old)
    absid=original.find(qn('w:abstractNumId')).get(qn('w:val'))
    if absid not in abs_map:
        abstract=deepcopy(next(x for x in sn.findall(qn('w:abstractNum')) if x.get(qn('w:abstractNumId'))==absid))
        abstract.set(qn('w:abstractNumId'),str(nextabs));dn.append(abstract);abs_map[absid]=str(nextabs);nextabs+=1
    item=deepcopy(original);item.set(qn('w:numId'),str(nextnum));item.find(qn('w:abstractNumId')).set(qn('w:val'),abs_map[absid]);dn.append(item);num_map[old]=str(nextnum);nextnum+=1
body=d.element.body;end=body.sectPr
for child in review.element.body:
    if child.tag not in (qn('w:p'),qn('w:tbl')):continue
    cp=deepcopy(child)
    for x in cp.xpath('.//w:numId'):
        old=x.get(qn('w:val'))
        if old in num_map:x.set(qn('w:val'),num_map[old])
    for x in cp.xpath('.//w:hyperlink[@r:id]'):
        rel=review.part.rels[x.get(qn('r:id'))]
        if rel.is_external:x.set(qn('r:id'),d.part.relate_to(rel.target_ref,RT.HYPERLINK,is_external=True))
    for x in cp.xpath('.//w:bookmarkStart | .//w:bookmarkEnd'):x.getparent().remove(x)
    for x in cp.xpath('.//w:pStyle'):
        x.set(qn('w:val'),'Normal')
    for x in cp.xpath('.//w:r'):
        rpr=x.find(qn('w:rPr'))
        if rpr is None:rpr=OxmlElement('w:rPr');x.insert(0,rpr)
        fonts=rpr.find(qn('w:rFonts'))
        if fonts is None:fonts=OxmlElement('w:rFonts');rpr.insert(0,fonts)
        for attr in ('ascii','hAnsi','cs','eastAsia'):fonts.set(qn('w:'+attr),'Times New Roman')
        for name in ('sz','szCs'):
            size=rpr.find(qn('w:'+name))
            if size is None:size=OxmlElement('w:'+name);rpr.append(size)
            size.set(qn('w:val'),'24' if child.tag==qn('w:tbl') else '28')
    end.addprevious(cp)
d.save(out)
check=Document(out)
orig=[''.join(x.text or '' for x in p.xpath('.//w:t')) for p in review.element.body.xpath('./w:p | ./w:tbl//w:p')]
app=[''.join(x.text or '' for x in p.xpath('.//w:t')) for p in check.element.body.xpath('./w:p | ./w:tbl//w:p')]
assert app[-len(orig):]==orig,'Review text differs from original'
print('Saved',out,'review paragraphs checked',len(orig))
