"""Блок-схема переноса брони по текущему алгоритму A5."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

fig, ax = plt.subplots(figsize=(12, 16.5), dpi=220)
ax.set(xlim=(0,12),ylim=(0,16.5)); ax.axis('off')
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

box(4.9,15.75,2.2,.48,'Начало','round')
box(3.5,14.75,5,.64,'Вход: id брони, новое время и площадка,\nрасписание, комплекты, текущее время')
box(4.0,13.75,4,.56,'Найти бронь по id')
diamond(6,12.78,'Бронь\nнайдена?')
box(.3,12.45,2.2,.55,'NOT_FOUND')
diamond(6,11.4,'Подтверждена,\nсеанс не начат?')
box(.3,11.13,2.2,.55,'INVALID_STATE')
diamond(6,10.05,'now < время\nтекущей брони?')
box(.3,9.77,2.2,.55,'TOO_LATE')
diamond(6,8.55,'Тот же слот\nи площадка?')
box(8.7,8.28,2.7,.55,'OK без записи истории')
box(3.5,7.15,5,.72,'Определить целевую площадку; проверить слот\nбез учёта изменяемой брони')
diamond(6,6.1,'Слот\nдоступен?')
box(3.4,4.8,4.6,.72,'Обновить время и площадку; записать\nстарые и новые значения в историю')
box(4.9,3.85,2.2,.55,'OK')
diamond(9.65,6.1,'Причина —\nCONFLICT?')
box(8.25,4.8,3,.72,'Найти альтернативы\nв заданном горизонте')
box(8.25,3.55,3,.62,'SLOT_UNAVAILABLE\nрезультат и список альтернатив')
box(4.9,.4,2.2,.5,'Конец','round')
line([(6,15.75),(6,15.39)]);line([(6,14.75),(6,14.31)]);line([(6,13.75),(6,13.30)])
line([(5.2,12.78),(2.5,12.78)],'нет',(3.7,12.9));line([(6,12.26),(6,11.92)],'да',(6.25,12.05))
line([(5.2,11.4),(2.5,11.4)],'нет',(3.7,11.52));line([(6,10.88),(6,10.57)],'да',(6.25,10.65))
line([(5.2,10.05),(2.5,10.05)],'нет',(3.7,10.17));line([(6,9.53),(6,9.07)],'да',(6.25,9.25))
line([(6.8,8.55),(8.7,8.55)],'да',(7.75,8.68));line([(6,8.03),(6,7.87)],'нет',(6.3,7.93))
line([(6,7.15),(6,6.62)]);line([(6,5.58),(6,5.52)],'да',(6.25,5.55));line([(6,4.8),(6,4.4)])
line([(6.8,6.1),(8.85,6.1)],'нет',(7.8,6.23));line([(9.65,5.58),(9.65,5.52)],'да',(9.9,5.55))
line([(9.65,4.8),(9.65,4.17)])
line([(10.45,6.1),(11.7,6.1),(11.7,3.86),(11.25,3.86)],'нет',(11.0,6.23))
for y in (12.72,11.4,10.04): line([(.3,y),(.12,y),(.12,1.1),(5.6,1.1),(5.6,.9)])
line([(6,3.85),(6,.9)]);line([(9.65,3.55),(9.65,1.1),(6.4,1.1),(6.4,.9)])
line([(11.4,8.55),(11.9,8.55),(11.9,.6),(7.1,.6)])
Path('docs/figures').mkdir(parents=True,exist_ok=True)
fig.savefig('docs/figures/a5_stage1.png',bbox_inches='tight',facecolor='white');plt.close(fig)
