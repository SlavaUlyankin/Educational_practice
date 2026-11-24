"""Схема приёма и обработки сообщений об отмене/переносе."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon, FancyArrowPatch

out = Path('docs/figures')
out.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(17, 11), dpi=220)
ax.set(xlim=(0, 17), ylim=(0, 11))
ax.axis('off')

def rect(x,y,w,h,text, rounded=True, **kw):
    cls = FancyBboxPatch if rounded else Rectangle
    args = dict(facecolor='white',edgecolor='#172b4d',linewidth=1.3)
    if rounded: args['boxstyle']='round,pad=0.03,rounding_size=0.08'
    args.update(kw)
    ax.add_patch(cls((x,y),w,h,**args))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9,zorder=4)

def arrow(start,end, label='', dashed=False, labelpos=None):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='->' if dashed else '-|>',mutation_scale=13,
                                linestyle=(0,(5,3)) if dashed else 'solid',
                                color='#344b6a',linewidth=1.25,zorder=3))
    if label:
        p = labelpos or ((start[0]+end[0])/2,(start[1]+end[1])/2+0.13)
        ax.text(*p,label,fontsize=8,ha='center',va='center',
                bbox=dict(facecolor='white',edgecolor='none',pad=1),zorder=5)

def gateway(x,y,text):
    ax.add_patch(Polygon([(x,y+.38),(x+.38,y),(x,y-.38),(x-.38,y)],
                         closed=True,facecolor='white',edgecolor='#172b4d',lw=1.3))
    ax.text(x,y,'×',fontsize=18,ha='center',va='center')
    ax.text(x,y-.55,text,fontsize=8,ha='center',va='top', bbox=dict(facecolor='white',edgecolor='none',pad=0.4))

def routed_message(points, text, labelpos):
    x, y = zip(*points)
    ax.plot(x[:-1], y[:-1], color='#344b6a', linewidth=1.2,
            linestyle=(0,(5,3)), zorder=2)
    arrow(points[-2], points[-1], dashed=True)
    ax.text(*labelpos,text,fontsize=8,ha='center',va='center',
            bbox=dict(facecolor='white',edgecolor='none',pad=1),zorder=5)

def event(x,y,noninterrupt=False,end=False):
    ax.add_patch(Circle((x,y),.22,facecolor='white',edgecolor='#172b4d',
                        lw=2 if end else 1.4,linestyle='--' if noninterrupt else '-'))
    if noninterrupt:
        ax.add_patch(Rectangle((x-.12,y-.075),.24,.15,facecolor='none',edgecolor='#172b4d',lw=.8))
        ax.plot([x-.12,x,x+.12],[y+.075,y-.01,y+.075],color='#172b4d',lw=.8)

# Пулы и граница подпроцесса-события.
rect(.3,9.75,16.4,.8,'Клиент — внешний пул',rounded=False,facecolor='#f5f7fa')
rect(.3,.4,16.4,8.8,'',rounded=False)
ax.text(.5,8.95,'VR-арена · администратор и система учёта',fontsize=11,fontweight='bold')
ax.add_patch(Rectangle((.7,.8),15.6,7.9,fill=False,edgecolor='#526b89',lw=1.3,linestyle=(0,(2,3))))
ax.text(.9,8.42,'ESP1 — непрерывающий подпроцесс-событие',fontsize=10,fontweight='bold')

event(1.2,6.8,True)
rect(1.9,6.4,2.0,.8,'X1.2\nНайти бронь в DS1')
gateway(4.65,6.8,'X1.3: найдена?')
gateway(6.25,6.8,'X1.6')
rect(7.05,7.3,2.2,.9,'X1.7–X1.9\nОтменить бронь;\nурегулировать предоплату')
rect(9.65,7.3,2.1,.9,'Записать отмену\nв историю')
rect(12.15,7.3,2.1,.9,'Ответ клиенту\nML6.1')
event(15.0,7.75,end=True)
rect(7.05,5.15,2.2,.9,'X1.13\nПроверить слот\nи площадку')
gateway(10.0,5.6,'X1.14: доступен?')
rect(10.8,5.15,2.0,.9,'X1.15\nИзменить бронь\nи записать историю')
rect(13.15,5.15,2.0,.9,'Ответ клиенту\nML6.2')
event(15.65,5.6,end=True)
rect(10.8,3.35,2.0,.9,'X1.18–X1.19\nСохранить бронь;\nпредложить варианты')
rect(13.15,3.35,2.0,.9,'Ответ клиенту\nML6.3')
event(15.65,3.8,end=True)
rect(3.65,2.0,2.2,.9,'X1.4\nСообщить об\nотсутствии брони')
event(6.35,2.45,end=True)

arrow((1.42,6.8),(1.9,6.8)); arrow((3.9,6.8),(4.27,6.8))
arrow((5.03,6.8),(5.87,6.8),'да'); arrow((6.25,7.18),(7.05,7.75),'отмена')
arrow((9.25,7.75),(9.65,7.75)); arrow((11.75,7.75),(12.15,7.75)); arrow((14.25,7.75),(14.78,7.75))
arrow((6.25,6.42),(7.05,5.6),'перенос'); arrow((9.25,5.6),(9.62,5.6))
arrow((10.38,5.6),(10.8,5.6),'да'); arrow((12.8,5.6),(13.15,5.6)); arrow((15.15,5.6),(15.43,5.6))
arrow((10,5.22),(10.8,3.8),'нет'); arrow((12.8,3.8),(13.15,3.8)); arrow((15.15,3.8),(15.43,3.8))
arrow((4.65,6.42),(4.65,2.9),'нет',labelpos=(4.35,4.5)); arrow((5.85,2.45),(6.13,2.45))
arrow((1.2,9.75),(1.2,7.02),'ML5.1 / ML5.2',True,(2.05,9.35))
arrow((13.2,8.2),(13.2,9.75),'ML6.1',True,(13.5,9.15))
routed_message([(14.15,6.05),(14.15,6.6),(15.55,6.6),(15.55,9.75)], 'ML6.2', (15.8,8.3))
routed_message([(14.15,4.25),(14.15,4.55),(16.05,4.55),(16.05,9.75)], 'ML6.3', (16.25,6.5))
routed_message([(3.65,2.45),(.55,2.45),(.55,9.75)], 'ML6.3', (.95,4.9))
ax.text(.9,1.05,'Сплошная стрелка — поток управления; пунктирная стрелка — сообщение между пулами.\nПосле отмены SP2 для этой брони не выполняется; после переноса SP2 использует обновлённую бронь.',fontsize=8,va='bottom')
fig.savefig(out/'bpmn_esp1_draft.png',bbox_inches='tight',facecolor='white')
plt.close(fig)
