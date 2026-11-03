"""Печатает таблицу «ожидалось / получено» по всем тест-кейсам (для отчёта)."""
import sys
from tests.cases import ALL_GROUPS


def main() -> int:
    failed = total = 0
    for group, cases in ALL_GROUPS.items():
        print(f"\n=== {group} ===")
        for c in cases:
            actual = c.run()
            ok = actual == c.expected
            total += 1
            failed += 0 if ok else 1
            print(f"[{'OK ' if ok else 'ОШИБКА'}] {c.id:7} {c.desc}")
            print(f"         ожидалось: {c.expected}")
            print(f"         получено : {actual}")
    print(f"\nИтого: {total} кейсов, успешно {total - failed}, ошибок {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
