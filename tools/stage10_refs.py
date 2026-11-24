from docx import Document
import re
d=Document('docs/report/Ульянкин_ВИ_ИКБО-30-24_Учебная_практика_этап4_образование.docx')
for p in d.element.body.xpath('.//w:p'):
 t=''.join(x.text or '' for x in p.xpath('.//w:t'))
 if t.startswith('Приложение В'):break
 matches=re.findall(r'(?i)раздел[а-я]*\s+\d+(?:[.\-–]\d+)*(?:\s*(?:и|,|–|-)\s*\d+(?:\.\d+)*)*',t)
 if matches: print(' | '.join(matches),'::',t[:160])
