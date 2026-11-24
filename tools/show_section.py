import sys
from docx import Document

doc = Document(sys.argv[1])
active = False
for paragraph in doc.paragraphs:
    if paragraph.text.startswith(sys.argv[2]):
        active = True
    elif active and paragraph.text.startswith(sys.argv[3]):
        break
    if active and paragraph.text:
        print(paragraph.text)
