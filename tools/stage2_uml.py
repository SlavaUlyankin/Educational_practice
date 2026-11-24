"""Схема проектируемого Java-модуля: состав классов и ответственности."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

fig,ax=plt.subplots(figsize=(12,14),dpi=220)
ax.set(xlim=(0,12),ylim=(0,14));ax.axis('off')
classes=[
('Client',['id; fullName; phone','email; createdAt']),('Game',['id; title','minPlayers; maxPlayers']),('Tariff',['id; gameId; name','durationMin; price']),
('Arena',['id; name; capacity','prepMin; active']),('Booking',['id; clientId; arenaId','gameId; tariffId; start; status']),('BookingHistory',['id; bookingId; eventType','old/new time, arena; reason']),
('Session',['id; bookingId; arenaId','status; durationMin; times']),('SessionEquipment',['sessionId; equipmentId','issuedAt; returnedAt; condition']),('EquipmentSet',['id; arenaId; kind; status','isAvailableForIssue()']),
('EquipmentStatusLog',['equipmentId; oldStatus','newStatus; changedAt; comment']),('«enumeration»',['BookingStatus; SessionStatus','EquipmentStatus; BookingEventType']),('«JDK» Clock',['instant()','Источник времени для сервисов']),
('BookingService',['checkSlot(); create();','cancel(); reschedule(); markNoShow()']),('SessionService',['start(); timeState();','finish(): FinishReport']),('EquipmentService',['changeStatus(); issue();','returnEquipment(); replace(): outcome'])]
for i,(name,fields) in enumerate(classes):
    col=i%3;row=i//3;x=.25+col*3.95;y=12.9-row*2.45;w=3.65;h=1.25
    ax.add_patch(Rectangle((x,y-h),w,h,facecolor='#f4f7fa' if i<12 else '#fff7e8',edgecolor='#1d2c42',lw=1.3))
    ax.plot([x,x+w],[y-.38,y-.38],color='#1d2c42',lw=1)
    ax.text(x+w/2,y-.2,name,fontsize=13,ha='center',va='center',weight='bold')
    for j,line in enumerate(fields):ax.text(x+.1,y-.62-j*.28,line,fontsize=10,va='center')
for start,end in [((7.85,12.25),(8.15,12.25)), ((3.9,9.8),(4.2,9.8)),
                  ((7.85,9.8),(8.15,9.8)), ((3.9,7.35),(4.2,7.35)),
                  ((7.85,7.35),(8.15,7.35))]:
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-',linewidth=1.4,color='#1d2c42'))
ax.text(.35,.72,'Связи по идентификаторам: Booking → Client, Game, Tariff, Arena, Session;\nBookingHistory → Booking и Arena; SessionEquipment → Session и EquipmentSet;\nEquipmentSet → Arena; EquipmentStatusLog → EquipmentSet.',fontsize=10,va='bottom')
ax.text(.35,.12,'Сервисы используют доменные объекты и Clock; состояние хранится в памяти. Состав полей сокращён.',fontsize=9,va='bottom')
Path('docs/figures').mkdir(parents=True,exist_ok=True)
fig.savefig('docs/figures/uml_stage2.png',bbox_inches='tight',facecolor='white');plt.close(fig)
