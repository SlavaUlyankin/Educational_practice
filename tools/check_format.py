"""Структурные проверки документа; визуальная проверка выполняется отдельно."""
import re
import sys
from collections import Counter
from pathlib import Path
from docx import Document

doc = Document(sys.argv[1])
paragraphs = [p.text.strip() for p in doc.paragraphs]
full = '\n'.join(paragraphs)
lines = ['# Проверка оформления', '', 'Автоматические структурные проверки; визуальная проверка обязательна.', '']
for label in ('Таблица', 'Рисунок', 'Листинг'):
    numbers = [int(m.group(1)) for p in paragraphs if (m := re.match(rf'^{label}\s+(\d+)\s*[—–-]', p))]
    counts = Counter(numbers)
    expected = set(range(1, max(numbers) + 1)) if numbers else set()
    duplicates = [n for n, count in counts.items() if count > 1]
    missing = sorted(expected - set(numbers))
    order = numbers == sorted(numbers)
    stem = {'Таблица': r'таблиц[а-я]*', 'Рисунок': r'рисун(?:ок|к[а-я]*)', 'Листинг': r'листинг[а-я]*'}[label]
    body = '\n'.join(p for p in paragraphs if not re.match(rf'^{label}\s+\d+\s*[—–-]', p))
    uncited = [n for n in numbers if not re.search(rf'(?i){stem}\s+{n}(?!\d)', body)]
    ok = not (duplicates or missing or uncited) and order
    lines.append(f'{"PASS" if ok else "FAIL"}: {label}: номера {numbers}; дубли {duplicates}; пропуски {missing}; не по порядку {not order}; без упоминания {uncited}.')
bad = [p for p in paragraphs if re.search(r'TODO|```|\*\*|\[ \]', p)]
lines.append(f'{"FAIL" if bad else "PASS"}: черновые маркеры: {len(bad)}.')
lines.append('Ссылки диапазоном (например, рисунки 11–15) не распознаются и требуют ручной проверки. НЕ ПРОВЕРЕНО автоматически: унаследованные стили, реальные ссылки и список источников, перекрёстные ссылки разделов, границы изображений, страницы, переносы и читаемость. Требуется ручная проверка.')
Path('docs/standards/format_report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
