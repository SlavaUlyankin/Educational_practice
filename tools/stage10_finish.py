from pathlib import Path
from shutil import copy2
import re
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

root=Path('docs/report')
src=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_образование.docx'
dst=root/'Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_итог.docx'
copy2(src,root/'backups/этап4_перед_этапом10.docx')
d=Document(src)
original_review=Document('docs/reviews/ЗиминЕА_рецензия_УльянкинВИ.docx')
def font(r,size=14):
    r.font.name='Times New Roman';r.font.size=Pt(size)
    for a in ('ascii','hAnsi','cs','eastAsia'):r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:'+a),'Times New Roman')
def replace(p,old,new):
    nodes=p.xpath('.//w:t');full=''.join(n.text or '' for n in nodes)
    for m in reversed(list(re.finditer(re.escape(old),full))):
        start,end=m.span();off=0;first=last=None
        for node in nodes:
            count=len(node.text or '')
            if first is None and start<off+count:first=node;lo=start-off
            if first is not None and end<=off+count:last=node;hi=end-off;break
            off+=count
        if first is last:first.text=(first.text or '')[:lo]+new+(first.text or '')[hi:]
        else:
            first.text=(first.text or '')[:lo]+new;active=False
            for node in nodes:
                if node is first:active=True;continue
                if active and node is last:node.text=(node.text or '')[hi:];break
                if active:node.text=''

mapping={i:('1.'+str(i) if i<=5 else '2.'+str(i-5)) for i in range(1,12)}
start=next(p for p in d.paragraphs if p.text.startswith('1. ИССЛЕДОВАНИЕ'))
second=next(p for p in d.paragraphs if p.text.startswith('6. МОДЕЛЬ ОСНОВНОГО'))
appendix_v=next(p for p in d.paragraphs if p.text.strip()=='Приложение В')
appendix_v.style='Heading 1';appendix_v.paragraph_format.page_break_before=False
next(p for p in d.paragraphs if p.text.strip()=='Пояснение принятых решений').style='Heading 3'

# Renumber references only in report content, excluding approved forms and source review.
active=False
pattern=re.compile(r'(?i)(раздел[а-я]*\s+)(\d+(?:\.\d+)?(?:\s*(?:и|,|–|-)\s*\d+(?:\.\d+)?)*)')
for p in d.element.body.xpath('.//w:p'):
    if p is start._p:active=True
    if p is appendix_v._p:break
    if not active:continue
    full=''.join(n.text or '' for n in p.xpath('.//w:t'))
    for m in reversed(list(pattern.finditer(full))):
        value=m.group(2)
        new=re.sub(r'(?<![\d.])\d+(?![\d.])',lambda x:mapping.get(int(x.group()),x.group()),value)
        if value!=new:replace(p,m.group(0),m.group(1)+new)

# Original 11 main sections become sections 1.1–1.5 and 2.1–2.6.
for p in list(d.paragraphs):
    if p is appendix_v:break
    if p.style.name=='Heading 1':
        m=re.match(r'^(\d{1,2})\.\s+(.+)$',p.text)
        if not m:continue
        number=int(m.group(1))
        if number not in mapping:continue
        replace(p._p,m.group(0),mapping[number]+'. '+m.group(2))
        p.style='Heading 2';p.paragraph_format.page_break_before=False;p.paragraph_format.keep_with_next=True
    elif p.style.name=='Heading 2' and re.match(r'^11\.[1-4]\.',p.text):
        replace(p._p,'11.','2.6.');p.style='Heading 3';p.paragraph_format.keep_with_next=True

def preceding_heading(anchor,text):
    p=d.add_paragraph(text,style='Heading 1');anchor._p.addprevious(p._p)
    p.paragraph_format.page_break_before=True;p.paragraph_format.keep_with_next=True
    for r in p.runs:font(r)
    return p
chapter1=preceding_heading(start,'ГЛАВА 1. ИССЛЕДОВАНИЕ ПРЕДМЕТНОЙ ОБЛАСТИ')
preceding_heading(second,'ГЛАВА 2. АНАЛИЗ И ПРОЕКТИРОВАНИЕ СИСТЕМЫ')

# Insert native Word TOC field before chapter 1. Word will populate it during the update step.
title=d.add_paragraph('СОДЕРЖАНИЕ');chapter1._p.addprevious(title._p)
title.alignment=WD_ALIGN_PARAGRAPH.CENTER;title.paragraph_format.page_break_before=True;title.paragraph_format.keep_with_next=True
for r in title.runs:font(r);r.bold=True
toc=d.add_paragraph();chapter1._p.addprevious(toc._p)
r=toc.add_run();begin=OxmlElement('w:fldChar');begin.set(qn('w:fldCharType'),'begin');r._r.append(begin)
instr=OxmlElement('w:instrText');instr.set(qn('xml:space'),'preserve');instr.text=' TOC \\o "1-3" \\h \\z \\u ';r._r.append(instr)
sep=OxmlElement('w:fldChar');sep.set(qn('w:fldCharType'),'separate');r._r.append(sep)
text=OxmlElement('w:t');text.text='Оглавление обновляется в Microsoft Word.';r._r.append(text)
end=OxmlElement('w:fldChar');end.set(qn('w:fldCharType'),'end');r._r.append(end)

def before(anchor,text):
    p=d.add_paragraph(text);anchor._p.addprevious(p._p)
    p.paragraph_format.line_spacing=1.5;p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(0)
    p.paragraph_format.first_line_indent=Cm(1.25);p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p.runs:font(r)
    return p
literature=next(p for p in d.paragraphs if p.text.strip()=='СПИСОК ЛИТЕРАТУРЫ')
before(literature,'Применение инструментов искусственного интеллекта при подготовке работы зафиксировано в журнале, приведённом в приложении Г. Приведённые материалы и результаты проверены в объёме, указанном в соответствующих разделах.')
table20=next(p for p in d.paragraphs if p.text.startswith('Таблица 20 —'))
table20.paragraph_format.page_break_before=True
appendix_b=next(p for p in d.paragraphs if p.text.strip()=='Приложение Б')
before(appendix_b,'Java-модуль находится в каталоге java. В IntelliJ IDEA следует открыть этот каталог как Maven-проект, выбрать JDK 17 или совместимый JDK, дождаться загрузки зависимостей и запустить тесты Maven test или класс ArenaServicesTest. Демонстрация запускается методом main класса Demo. Подробная инструкция находится в java/README.md.')
before(appendix_b,'Для проверки Java из каталога java выполняется команда mvn -q test; после сборки демонстрация запускается командой java -cp target/classes ru.mirea.vrarena.Demo. Последние локальные изменения должны быть опубликованы в удалённом репозитории отдельно; при проверке репозитория необходимо учитывать его фактическую версию.')

# Appendix G with a textual record, not Markdown syntax.
d.add_page_break();p=d.add_paragraph('Приложение Г',style='Heading 1');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
for r in p.runs:font(r)
p=d.add_paragraph('Журнал применения искусственного интеллекта');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
for r in p.runs:font(r);r.bold=True
for line in Path('docs/ai_journal.md').read_text(encoding='utf-8').splitlines():
    line=line.strip()
    if not line or line=='# Журнал применения ИИ':continue
    heading=line.startswith('## ');line=line.removeprefix('## ').replace('`','')
    p=d.add_paragraph(line);p.paragraph_format.line_spacing=1.5;p.paragraph_format.space_after=Pt(0)
    p.paragraph_format.first_line_indent=Cm(0 if heading else 1.25)
    p.alignment=WD_ALIGN_PARAGRAPH.LEFT if heading else WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.keep_with_next=heading
    for r in p.runs:font(r);r.bold=heading

# Enable field recalculation in Word.
settings=d.settings.element
upd=settings.find(qn('w:updateFields'))
if upd is None:upd=OxmlElement('w:updateFields');settings.append(upd)
upd.set(qn('w:val'),'true')
d.save(dst)
check=Document(dst)
source=[''.join(x.text or '' for x in p.xpath('.//w:t')) for p in original_review.element.body.xpath('./w:p | ./w:tbl//w:p')]
alltext=[''.join(x.text or '' for x in p.xpath('.//w:t')) for p in check.element.body.xpath('./w:p | ./w:tbl//w:p')]
index=next(i for i,s in enumerate(alltext) if s=='Рецензия Зимина Е. А. на программный код')+1
assert alltext[index:index+len(source)]==source,'Review text changed'
print('Saved',dst,'review paragraphs intact',len(source))
