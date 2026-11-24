"""Компактная ER-схема; полный перечень атрибутов приведён в таблицах отчёта."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

out = Path('docs/figures')
out.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(15, 10), dpi=220)
ax.set_xlim(0, 15)
ax.set_ylim(0, 10)
ax.axis('off')
nodes = {
    'client': (1.6, 8.8, 'Клиент'),
    'game': (5.3, 8.8, 'Игра'),
    'tariff': (9.1, 8.8, 'Тариф'),
    'arena': (13.1, 8.8, 'Площадка'),
    'booking': (5.3, 5.7, 'Бронирование'),
    'session': (9.1, 5.7, 'Сеанс'),
    'equipment_set': (13.1, 5.7, 'Комплект оборудования'),
    'booking_history': (1.6, 2.1, 'История брони'),
    'session_equipment': (9.1, 2.1, 'Выдача комплекта'),
    'equipment_status_log': (13.1, 2.1, 'История статусов'),
}
def link(points, label, position):
    x, y = zip(*points)
    ax.plot(x, y, color='#334155', linewidth=1.1, zorder=1)
    ax.annotate('', xy=points[-1], xytext=points[-2],
                arrowprops=dict(arrowstyle='-|>', color='#334155', lw=1.1,
                                mutation_scale=12), zorder=1)
    ax.text(*position, label, ha='center', va='center', fontsize=9,
            bbox=dict(facecolor='white', edgecolor='none', pad=1), zorder=3)

link([(1.6,8.25),(1.6,7.35),(4.0,7.35),(4.0,6.15)], '1 : N', (2.5,7.35))
link([(5.3,8.25),(5.3,6.15)], '1 : N', (5.3,7.15))
link([(9.1,8.25),(9.1,7.55),(6.5,7.55),(6.5,6.15)], '1 : N', (7.7,7.55))
link([(6.6,8.8),(7.8,8.8)], '1 : N', (7.2,8.8))
link([(13.1,8.25),(13.1,7.95),(3.2,7.95),(3.2,5.7),(4,5.7)], '1 : N', (11.6,7.95))
link([(13.1,8.25),(13.1,6.15)], '1 : N', (13.1,7.1))
link([(6.6,5.7),(7.8,5.7)], '1 : 0..1', (7.2,5.7))
link([(5.3,5.25),(5.3,3.55),(1.6,3.55),(1.6,2.55)], '1 : N', (3.4,3.55))
link([(9.1,5.25),(9.1,2.55)], '1 : N', (9.1,4))
link([(13.1,5.25),(13.1,4.45),(10.6,4.45),(10.6,2.1),(10.4,2.1)], '1 : N', (11.8,4.45))
link([(13.1,5.25),(13.1,2.55)], '1 : N', (13.1,3.75))
link([(12.0,8.25),(11.6,7.7),(11.6,0.8),(1.6,0.8),(1.6,1.65)], '1 : N (old/new)', (6.8,0.8))
for name, (x, y, title) in nodes.items():
    box = FancyBboxPatch((x-1.3, y-0.45), 2.6, 0.9, boxstyle='round,pad=0.04,rounding_size=0.12',
                         facecolor='#edf3f8', edgecolor='#1e293b', linewidth=1.3, zorder=2)
    ax.add_patch(box)
    ax.text(x, y+0.14, name, ha='center', va='center', fontsize=10, fontweight='bold', zorder=4)
    ax.text(x, y-0.17, title, ha='center', va='center', fontsize=9, zorder=4)
ax.text(7.5, 0.23, '1 : N — связь «один ко многим»; 0..1 — необязательная связь; old/new — прежняя и новая площадка',
        ha='center', va='center', fontsize=9)
fig.savefig(out / 'er_stage1.png', bbox_inches='tight', facecolor='white')
plt.close(fig)
