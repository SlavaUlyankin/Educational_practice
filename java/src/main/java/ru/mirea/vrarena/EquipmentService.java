package ru.mirea.vrarena;
import java.time.Clock;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public final class EquipmentService {
    private final Clock clock; private final List<EquipmentSet> kits; private final List<SessionEquipment> issues; private final List<EquipmentStatusLog> log;
    public EquipmentService(Clock clock,List<EquipmentSet> kits,List<SessionEquipment> issues,List<EquipmentStatusLog> log){this.clock=Objects.requireNonNull(clock);this.kits=Objects.requireNonNull(kits);this.issues=Objects.requireNonNull(issues);this.log=Objects.requireNonNull(log);}
    public void changeStatus(EquipmentSet kit,EquipmentStatus target,String comment){
        Objects.requireNonNull(kit);Objects.requireNonNull(target);EquipmentStatus old=kit.status();
        boolean allowed=switch(old){
            case AVAILABLE -> Set.of(EquipmentStatus.ISSUED,EquipmentStatus.FAULTY).contains(target);
            case ISSUED -> Set.of(EquipmentStatus.RETURNED_PENDING,EquipmentStatus.FAULTY).contains(target);
            case RETURNED_PENDING -> Set.of(EquipmentStatus.SERVICING,EquipmentStatus.FAULTY).contains(target);
            case SERVICING -> Set.of(EquipmentStatus.AVAILABLE,EquipmentStatus.FAULTY).contains(target);
            case FAULTY -> target==EquipmentStatus.SERVICING;
        };
        if(!allowed) throw new IllegalStateException("INVALID_TRANSITION");
        kit.setStatus(target);log.add(new EquipmentStatusLog(kit.id,old,target,clock.instant(),comment));
    }
    public List<Long> issue(Session session,long arenaId){
        if(session.status()!=SessionStatus.PREPARED) throw new IllegalStateException("INVALID_STATE");
        if(issues.stream().anyMatch(r->r.sessionId==session.id && r.returnedAt()==null)) throw new IllegalStateException("ALREADY_ISSUED");
        List<EquipmentSet> selected=kits.stream().filter(k->k.arenaId==arenaId && k.status()==EquipmentStatus.AVAILABLE).limit(session.playersCount).toList();
        if(selected.size()<session.playersCount) throw new IllegalStateException("NOT_ENOUGH_AVAILABLE");
        Instant now=clock.instant();List<Long> ids=new ArrayList<>();
        for(EquipmentSet kit:selected){changeStatus(kit,EquipmentStatus.ISSUED,"выдан в сеанс");issues.add(new SessionEquipment(session.id,kit.id,now));ids.add(kit.id);}
        return List.copyOf(ids);
    }
    public List<Long> returnEquipment(Session session,Map<Long,String> conditions){
        if(session.status()!=SessionStatus.COMPLETED) throw new IllegalStateException("INVALID_STATE");
        List<SessionEquipment> active=issues.stream().filter(r->r.sessionId==session.id && r.returnedAt()==null).toList();
        if(active.isEmpty()) throw new IllegalStateException("NO_ACTIVE_ISSUE");
        for(SessionEquipment row:active){
            String condition=conditions.get(row.equipmentId);if(!"ok".equals(condition) && !"damaged".equals(condition)) throw new IllegalArgumentException("MISSING_CONDITION");
            EquipmentSet kit=find(row.equipmentId);
            if((kit.status()!=EquipmentStatus.ISSUED && kit.status()!=EquipmentStatus.FAULTY) || (kit.status()==EquipmentStatus.FAULTY && condition.equals("ok"))) throw new IllegalStateException("INCONSISTENT_STATE");
        }
        Instant now=clock.instant();List<Long> ids=new ArrayList<>();
        for(SessionEquipment row:active){String condition=conditions.get(row.equipmentId);EquipmentSet kit=find(row.equipmentId);row.returned(now,condition);EquipmentStatus target=condition.equals("damaged")?EquipmentStatus.FAULTY:EquipmentStatus.RETURNED_PENDING;if(kit.status()!=target)changeStatus(kit,target,"возврат из сеанса");ids.add(kit.id);}
        return List.copyOf(ids);
    }
    public long replace(Session session,long faultyId){
        if(session.status()!=SessionStatus.IN_PROGRESS) throw new IllegalStateException("INVALID_STATE");
        SessionEquipment row=issues.stream().filter(r->r.sessionId==session.id && r.equipmentId==faultyId && r.returnedAt()==null).findFirst().orElseThrow(()->new IllegalStateException("NOT_ISSUED"));
        EquipmentSet kit=find(faultyId);if(kit.status()!=EquipmentStatus.ISSUED && kit.status()!=EquipmentStatus.FAULTY)throw new IllegalStateException("INCONSISTENT_STATE");
        if(kit.status()==EquipmentStatus.ISSUED)changeStatus(kit,EquipmentStatus.FAULTY,"неисправность во время сеанса");
        row.returned(clock.instant(),"damaged");
        EquipmentSet replacement=kits.stream().filter(k->k.arenaId==kit.arenaId && k.kind==kit.kind && k.status()==EquipmentStatus.AVAILABLE).findFirst().orElseThrow(()->new IllegalStateException("NO_REPLACEMENT"));
        changeStatus(replacement,EquipmentStatus.ISSUED,"замена комплекта");issues.add(new SessionEquipment(session.id,replacement.id,clock.instant()));return replacement.id;
    }
    private EquipmentSet find(long id){return kits.stream().filter(k->k.id==id).findFirst().orElseThrow(()->new IllegalStateException("INCONSISTENT_STATE"));}
}
