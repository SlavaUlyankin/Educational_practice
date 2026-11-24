"""Обновлённая схема проверки доступности слота A1."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

fig, ax = plt.subplots(figsize=(12,15), dpi=220)
ax.set(xlim=(0,12),ylim=(0,15));ax.axis('off')
def box(x,y,w,h,t,rounded=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.02,rounding_size=.15' if rounded else 'square,pad=.02',facecolor='white',edgecolor='#1e293b',lw=1.2))
    ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=9)
def diamond(x,y,t):
    ax.add_patch(Polygon([(x,y+.5),(x+.9,y),(x,y-.5),(x-.9,y)],closed=True,facecolor='white',edgecolor='#1e293b',lw=1.2))
    ax.text(x,y,t,ha='center',va='center',fontsize=8)
def line(points,label=None,pos=None):
    xs,ys=zip(*points);ax.plot(xs,ys,color='#1e293b',lw=1.1)
    ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=12,lw=1.1,color='#1e293b'))
    if label: ax.text(*pos,label,fontsize=8,ha='center',bbox=dict(facecolor='white',edgecolor='none',pad=1))
box(5,14.2,2,.5,'Начало',True)
box(3.45,13.2,5.1,.65,'Вход: время, длительность, игроки, площадка,\nрасписание, комплекты и параметры проверки')
diamond(6,12.1,'Входные данные\nкорректны?')
box(.3,11.83,2.25,.55,'INVALID_INPUT')
diamond(6,10.75,'Число игроков\nдопустимо?')
box(.3,10.48,2.25,.55,'PLAYERS_OUT_OF_RANGE')
diamond(6,9.4,'Время начала\nне в прошлом?')
box(.3,9.13,2.25,.55,'IN_THE_PAST')
box(3.5,8.0,5,.7,'Посчитать комплекты площадки,\nне отмеченные как faulty')
diamond(6,6.95,'Комплектов\nдостаточно?')
box(.3,6.68,2.25,.55,'NOT_ENOUGH_KITS')
box(3.4,5.55,5.2,.72,'Проверить пересечение с подтверждёнными бронями\nплощадки, исключив изменяемую бронь')
diamond(6,4.4,'Конфликт\nнайден?')
box(8.9,4.12,2.6,.62,'CONFLICT\nс id брони')
box(4.9,3.08,2.2,.55,'OK')
box(5,.35,2,.5,'Конец',True)
line([(6,14.2),(6,13.85)]);line([(6,13.2),(6,12.6)])
for y,next_y,out_y in [(12.1,11.25,12.1),(10.75,9.9,10.75),(9.4,8.7,9.4)]:
    line([(5.1,y),(2.55,out_y)],'нет',(3.8,y+.12));line([(6,y-.5),(6,next_y)],'да',(6.25,(y-.5+next_y)/2))
line([(6,8),(6,7.45)]);line([(5.1,6.95),(2.55,6.95)],'нет',(3.8,7.07));line([(6,6.45),(6,6.27)],'да',(6.25,6.35))
line([(6,5.55),(6,4.9)]);line([(6.9,4.4),(8.9,4.4)],'да',(7.9,4.53));line([(6,3.9),(6,3.63)],'нет',(6.28,3.75))
for y in (12.1,10.75,9.4,6.95): line([(.3,y),(.12,y),(.12,1.0),(5.5,1.0),(5.5,.85)])
line([(6,3.08),(6,.85)]);line([(10.2,4.12),(10.2,1),(6.5,1),(6.5,.85)])
Path('docs/figures').mkdir(parents=True,exist_ok=True)
fig.savefig('docs/figures/a1_stage1.png',bbox_inches='tight',facecolor='white');plt.close(fig)
