"""Блок-схема переноса брони по текущему алгоритму A5."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

fig, ax = plt.subplots(figsize=(12, 15), dpi=220)
ax.set(xlim=(0,12),ylim=(0,15)); ax.axis('off')
def box(x,y,w,h,t,kind='rect'):
    patch = FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.03,rounding_size=.17' if kind=='round' else 'square,pad=.02',facecolor='white',edgecolor='#1e293b',lw=1.3)
    ax.add_patch(patch); ax.text(x+w/2,y+h/2,t,fontsize=9,ha='center',va='center')
def diamond(x,y,t):
    ax.add_patch(Polygon([(x,y+.52),(x+.8,y),(x,y-.52),(x-.8,y)],closed=True,facecolor='white',edgecolor='#1e293b',lw=1.3))
    ax.text(x,y,t,fontsize=8,ha='center',va='center')
def line(points,label=None,xy=None):
    xs,ys=zip(*points);ax.plot(xs,ys,color='#1e293b',lw=1.2)
    ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=12,lw=1.2,color='#1e293b'))
    if label: ax.text(*xy,label,fontsize=8,bbox=dict(facecolor='white',edgecolor='none',pad=1),ha='center')

box(4.9,14.25,2.2,.48,'Начало','round')
box(3.5,13.25,5,.64,'Вход: id брони, новое время и площадка,\nрасписание, комплекты, текущее время')
box(4.0,12.25,4,.56,'Найти бронь по id')
diamond(6,11.28,'Бронь\nнайдена?')
box(.3,10.95,2.2,.55,'NOT_FOUND')
diamond(6,9.9,'Подтверждена,\nсеанс не начат?')
box(.3,9.63,2.2,.55,'INVALID_STATE')
diamond(6,8.55,'now < время\nтекущей брони?')
box(.3,8.27,2.2,.55,'TOO_LATE')
box(3.5,7.15,5,.72,'Определить целевую площадку; проверить слот\nбез учёта изменяемой брони')
diamond(6,6.1,'Слот\nдоступен?')
box(3.4,4.8,4.6,.72,'Обновить время и площадку; записать\nстарые и новые значения в историю')
box(4.9,3.85,2.2,.55,'OK')
diamond(9.65,6.1,'Причина —\nCONFLICT?')
box(8.25,4.8,3,.72,'Найти альтернативы\nв заданном горизонте')
box(8.25,3.55,3,.62,'SLOT_UNAVAILABLE\nрезультат и список альтернатив')
box(4.9,.4,2.2,.5,'Конец','round')
line([(6,14.25),(6,13.89)]);line([(6,13.25),(6,12.81)]);line([(6,12.25),(6,11.8)])
line([(5.2,11.28),(2.5,11.28)],'нет',(3.7,11.4));line([(6,10.76),(6,10.42)],'да',(6.25,10.55))
line([(5.2,9.9),(2.5,9.9)],'нет',(3.7,10.02));line([(6,9.38),(6,9.07)],'да',(6.25,9.15))
line([(5.2,8.55),(2.5,8.55)],'нет',(3.7,8.67));line([(6,8.03),(6,7.87)],'да',(6.25,7.93))
line([(6,7.15),(6,6.62)]);line([(6,5.58),(6,5.52)],'да',(6.25,5.55));line([(6,4.8),(6,4.4)])
line([(6.8,6.1),(8.85,6.1)],'нет',(7.8,6.23));line([(9.65,5.58),(9.65,5.52)],'да',(9.9,5.55))
line([(9.65,4.8),(9.65,4.17)])
line([(10.45,6.1),(11.7,6.1),(11.7,3.86),(11.25,3.86)],'нет',(11.0,6.23))
for y in (11.22,9.9,8.54): line([(.3,y),(.12,y),(.12,1.1),(5.6,1.1),(5.6,.9)])
line([(6,3.85),(6,.9)]);line([(9.65,3.55),(9.65,1.1),(6.4,1.1),(6.4,.9)])
Path('docs/figures').mkdir(parents=True,exist_ok=True)
fig.savefig('docs/figures/a5_stage1.png',bbox_inches='tight',facecolor='white');plt.close(fig)
