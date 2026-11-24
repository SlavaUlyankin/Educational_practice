"""Схемы взаимодействия пулов для сеансового обслуживания VR-арены."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon, FancyArrowPatch

out=Path('docs/figures');out.mkdir(parents=True,exist_ok=True)
def canvas(w,h):
    fig,ax=plt.subplots(figsize=(w,h),dpi=220);ax.set(xlim=(0,w),ylim=(0,h));ax.axis('off');return fig,ax
def box(ax,x,y,w,h,t,rounded=True,ls='solid',fontsize=9,fill='white'):
    kw=dict(facecolor=fill,edgecolor='#1e293b',linewidth=1.3,linestyle=ls)
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.03,rounding_size=.08',**kw) if rounded else Rectangle((x,y),w,h,**kw)
    ax.add_patch(p);ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fontsize,zorder=5)
def event(ax,x,y,end=False):ax.add_patch(Circle((x,y),.17,facecolor='white',edgecolor='#1e293b',lw=2 if end else 1.2))
def diamond(ax,x,y):
    ax.add_patch(Polygon([(x,y+.28),(x+.28,y),(x,y-.28),(x-.28,y)],closed=True,facecolor='white',edgecolor='#1e293b',lw=1.2));ax.text(x,y,'×',ha='center',va='center',fontsize=13)
def arr(ax,points,label='',dashed=False,xy=None):
    x,y=zip(*points);ax.plot(x[:-1],y[:-1],color='#344b6a',lw=1.2,linestyle='--' if dashed else '-')
    ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=11,color='#344b6a',lw=1.2,linestyle='--' if dashed else '-'))
    if label:ax.text(*(xy or points[0]),label,fontsize=8,ha='center',va='center',bbox=dict(facecolor='white',edgecolor='none',pad=.6))

# Рисунок 1: общая модель и обмен между пулами.
fig,ax=canvas(18,10)
box(ax,.3,9,17.4,.65,'Пул «Клиент» (внешний участник)',False,fill='#f3f5f8')
box(ax,.3,.3,17.4,8.2,'',False)
for y,t in [(8.0,'VR-арена · Администратор'),(3.9,'Технический специалист'),(2.1,'Система учёта')]:
    ax.text(.55,y,t,fontsize=10,fontweight='bold')
for y in (4.2,2.45):ax.plot([.3,17.7],[y,y],color='#9aa8b7',lw=.8)
event(ax,.9,7.15)
for x,t in [(1.35,'SP1\nЗаявка и\nбронирование'),(4.35,'SP2\nПриём\nклиентов'),(7.0,'SP3\nИнструктаж и\nвыдача'),(9.65,'SP4\nСеанс'),(12.3,'SP5\nРасчёт')]:
    box(ax,x,6.65,2,.95,t,fontsize=8)
    ax.text(x+1,6.72,'+',fontsize=10,ha='center',va='bottom')
diamond(ax,3.8,7.15)
for a,b in [((1.07,7.15),(1.35,7.15)),((3.35,7.15),(3.52,7.15)),((4.08,7.15),(4.35,7.15)),((6.35,7.15),(7,7.15)),((9,7.15),(9.65,7.15)),((11.65,7.15),(12.3,7.15))]:arr(ax,[a,b])
box(ax,14.9,3.05,2,.9,'SP6\nПодготовка\nплощадки',fontsize=8);event(ax,17.25,3.5,True)
arr(ax,[(14.3,7.15),(15.9,7.15),(15.9,3.95)]);arr(ax,[(16.9,3.5),(17.08,3.5)])
event(ax,3.8,6.0,True);arr(ax,[(3.8,6.87),(3.8,6.17)],'нет',xy=(4.05,6.45));ax.text(4.15,7.35,'да',fontsize=8)
box(ax,1.35,4.65,4.0,1.0,'ESP1 · отмена / перенос\nнепрерывающий подпроцесс-событие',False,ls='dotted',fontsize=8)
box(ax,8.4,4.65,3.6,1.0,'ESP2 · неисправность\nнепрерывающий подпроцесс-событие',False,ls='dotted',fontsize=8)
for x,t in [(1.5,'DS1\nброни и история'),(6.0,'DS2\nоборудование'),(10.4,'DS3\nсеансы и расчёты')]:box(ax,x,.8,3.2,1,t,fontsize=8,fill='#f7f8fc')
arr(ax,[(2.1,9),(2.1,7.6)],'ML1: заявка',True,(2.85,8.55))
arr(ax,[(2.7,7.6),(2.7,9)],'ML2 / ML3 / ML4.2',True,(4.1,8.25))
arr(ax,[(3.1,9),(3.1,7.6)],'ML4.1: согласие',True,(5.3,8.55))
arr(ax,[(1.15,9),(1.15,5.15),(1.35,5.15)],'ML5: запрос',True,(.95,6.0))
arr(ax,[(5.35,5.15),(6.65,5.15),(6.65,9)],'ML6: результат',True,(6.7,6.0))
arr(ax,[(13.7,9),(13.7,7.6)],'ML7: оплата',True,(14.5,8.55))
arr(ax,[(14.0,7.6),(14.0,9)],'ML8: чек',True,(15,8.15))
arr(ax,[(9.4,9),(9.4,5.65)],'ML9: неисправность',True,(10.5,8.55))
ax.text(.8,.42,'Сплошная стрелка — последовательность; пунктирная — сообщение между пулами. Детализация ESP1 — рисунок 4.',fontsize=7)
fig.savefig(out/'bpmn_overview.png',bbox_inches='tight',facecolor='white');plt.close(fig)

# Рисунок 2: явный обмен клиента с пулом арены.
fig,ax=canvas(16,9)
box(ax,.3,7.8,15.4,.8,'Пул «VR-арена» (внешний для сценария клиента)',False,fill='#f3f5f8')
box(ax,.3,.3,15.4,7.1,'',False);ax.text(.55,7.1,'Пул «Клиент»',fontsize=11,fontweight='bold')
event(ax,1,5.7)
box(ax,1.5,5.25,2,.9,'K1.2\nОтправить заявку',fontsize=8)
box(ax,4.0,5.25,2,.9,'K1.3\nПолучить предложение',fontsize=8)
diamond(ax,6.6,5.7)
box(ax,7.2,5.25,2,.9,'K1.5\nПодтвердить выбор',fontsize=8)
box(ax,9.8,5.25,2,.9,'K1.7\nПолучить\nподтверждение',fontsize=8)
event(ax,12.45,5.7,True)
box(ax,5.6,3.2,2,.9,'K1.6\nОтказаться',fontsize=8);event(ax,8.2,3.65,True)
for a,b in [((1.17,5.7),(1.5,5.7)),((3.5,5.7),(4,5.7)),((6,5.7),(6.32,5.7)),((6.88,5.7),(7.2,5.7)),((9.2,5.7),(9.8,5.7)),((11.8,5.7),(12.28,5.7)),((6.6,5.42),(6.6,4.1)),((7.6,3.65),(8.03,3.65))]:arr(ax,[a,b])
ax.text(7,5.9,'да',fontsize=8);ax.text(6.8,4.7,'нет',fontsize=8);ax.text(6.6,6.15,'K1.4: слот подходит?',fontsize=8,ha='center')
for a,b,l,x in [((2.5,6.15),(2.5,7.8),'ML1: заявка',2.5),((5,7.8),(5,6.15),'ML2 / ML3: предложение',5),((8.2,6.15),(8.2,7.8),'ML4.1: согласие',8.2),((10.8,7.8),(10.8,6.15),'ML4.2: подтверждение',10.8)]:arr(ax,[a,b],l,True,(x,7.45))
ax.text(1,1.1,'Дальнейшая отмена или перенос передаются клиентом сообщениями ML5.1 / ML5.2;\nрезультат возвращается ML6.1–ML6.3 (рисунок 4).',fontsize=9)
fig.savefig(out/'bpmn_client.png',bbox_inches='tight',facecolor='white');plt.close(fig)
