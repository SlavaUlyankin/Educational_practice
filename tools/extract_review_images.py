from pathlib import Path
import sys
from docx import Document
from docx.oxml.ns import qn

doc = Document(sys.argv[1])
out = Path('docs/standards/diagram_check')
out.mkdir(exist_ok=True)
for i, shape in enumerate(doc.inline_shapes, 1):
    blips = shape._inline.xpath('.//a:blip')
    if blips:
        part = doc.part.related_parts[blips[0].get(qn('r:embed'))]
        (out / f'{i}.{part.content_type.split("/")[-1]}').write_bytes(part.blob)
        print(i, part.content_type, len(part.blob))
