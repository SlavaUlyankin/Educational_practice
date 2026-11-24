from docx import Document
import re
d=Document('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_итог.docx')
review=Document('docs/reviews/ЗиминЕА_рецензия_УльянкинВИ.docx')
body=[]
for p in d.element.body.xpath('.//w:p'):
    t=''.join(x.text or '' for x in p.xpath('.//w:t'))
    if t.strip()=='Приложение В':break
    body.append(t)
text='\n'.join(body)
titles={m.group(1) for p in d.paragraphs if p.style.name.startswith('Heading') and (m:=re.match(r'^(\d+\.\d+(?:\.\d+)?)(?:\.|\s)',p.text))}
refs=[]
for m in re.finditer(r'(?i)раздел[а-я]*\s+(\d+(?:\.\d+)?)',text):
    value=m.group(1)
    if '.' in value and value not in titles:refs.append(value)
old=list(re.finditer(r'(?i)раздел[а-я]*\s+(?:[5-9]|10|11)(?![\d.])',text))
print('Headings',sorted(titles),'bad section references',refs,'unmapped old references',len(old))
source=[''.join(x.text or '' for x in p.xpath('.//w:t')) for p in review.element.body.xpath('./w:p | ./w:tbl//w:p')]
alltext=[''.join(x.text or '' for x in p.xpath('.//w:t')) for p in d.element.body.xpath('./w:p | ./w:tbl//w:p')]
index=next(i for i,s in enumerate(alltext) if s=='Рецензия Зимина Е. А. на программный код')+1
print('Review unchanged:',alltext[index:index+len(source)]==source)
ps=[p.text.strip() for p in d.paragraphs]
start=ps.index('СПИСОК ЛИТЕРАТУРЫ');end=ps.index('Приложение А',start)
sources={int(m.group(1)) for s in ps[start+1:end] if (m:=re.match(r'^(\d+)\.\s',s))}
citations={int(x) for s in body[:next(i for i,v in enumerate(body) if v=='СПИСОК ЛИТЕРАТУРЫ')] for x in re.findall(r'\[(\d+)\]',s)}
print('Sources',sorted(sources),'missing cited',sorted(citations-sources),'unreferenced',sorted(sources-citations))
print('Appendices',[(x,any(p.text.strip()==x for p in d.paragraphs)) for x in ('Приложение А','Приложение Б','Приложение В','Приложение Г')])
assert not refs and not old and alltext[index:index+len(source)]==source and not(citations-sources) and not(sources-citations)
