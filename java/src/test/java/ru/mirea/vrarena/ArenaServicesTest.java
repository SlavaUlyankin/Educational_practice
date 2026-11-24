package ru.mirea.vrarena;

import static org.junit.jupiter.api.Assertions.*;
import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ArenaServicesTest {
    static final class MutableClock extends Clock {
        Instant now=Instant.parse("2026-11-10T12:00:00Z");
        @Override public ZoneId getZone(){return ZoneOffset.UTC;}
        @Override public Clock withZone(ZoneId zone){return Clock.fixed(now,zone);}
        @Override public Instant instant(){return now;}
    }
    MutableClock clock; List<Booking> bookings; List<BookingHistory> history; List<EquipmentSet> kits;
    List<SessionEquipment> issues; List<EquipmentStatusLog> log; BookingService service;
    Game game; Tariff tariff; Arena arena; Instant start;
    @BeforeEach void setup(){
        clock=new MutableClock();bookings=new ArrayList<>();history=new ArrayList<>();kits=new ArrayList<>();issues=new ArrayList<>();log=new ArrayList<>();
        for(int i=1;i<=3;i++)kits.add(new EquipmentSet(i,1,"SET-"+i,EquipmentKind.HEADSET));
        game=new Game(1,"Game",1,3,false);tariff=new Tariff(1,1L,"Hour",60,BigDecimal.TEN,false,true);arena=new Arena(1,"Hall",3,10,true);
        service=new BookingService(clock,bookings,kits,history);start=Instant.parse("2026-11-10T18:00:00Z");
    }
    Booking create(){return service.create(1,game,tariff,arena,start,2,BigDecimal.ZERO);}
    @Test void touchingBoundaryAndArenaIsolation(){
        create();
        assertEquals(BookingService.SlotCode.CONFLICT,service.checkSlot(start.plusSeconds(69*60),30,1,game,arena,null).code());
        assertEquals(BookingService.SlotCode.OK,service.checkSlot(start.plusSeconds(70*60),30,1,game,arena,null).code());
        Arena other=new Arena(2,"Other",3,10,true);kits.add(new EquipmentSet(4,2,"OTHER",EquipmentKind.HEADSET));
        assertEquals(BookingService.SlotCode.OK,service.checkSlot(start,30,1,game,other,null).code());
    }
    @Test void rejectedMovePreservesBookingAndHistory(){
        Booking one=create();service.create(2,game,tariff,arena,start.plusSeconds(2*3600),1,BigDecimal.ZERO);
        int count=history.size();var result=service.reschedule(one.id,start.plusSeconds(2*3600),game,arena,"request");
        assertFalse(result.success());assertEquals(start,one.start());assertEquals(count,history.size());
        assertFalse(result.alternatives().isEmpty());
    }
    @Test void moveRecordsOldAndNewAndCancelFreesSlot(){
        Booking one=create();Instant next=start.plusSeconds(2*3600);
        assertTrue(service.reschedule(one.id,next,game,arena,"move").success());
        var event=history.get(history.size()-1);assertEquals(start,event.oldStart());assertEquals(next,event.newStart());
        service.cancel(one.id,"cancel");assertEquals(BookingStatus.CANCELLED,one.status());
        assertEquals(BookingService.SlotCode.OK,service.checkSlot(next,30,1,game,arena,null).code());
    }
    @Test void moveBetweenArenasKeepsBothHistoryValues(){
        Booking one=create();Arena target=new Arena(2,"Other",3,10,true);
        kits.add(new EquipmentSet(4,2,"O1",EquipmentKind.HEADSET));kits.add(new EquipmentSet(5,2,"O2",EquipmentKind.HEADSET));
        assertTrue(service.reschedule(one.id,start,game,target,"other arena").success());
        assertEquals(2,one.arenaId());BookingHistory e=history.get(history.size()-1);
        assertEquals(1L,e.oldArenaId());assertEquals(2L,e.newArenaId());assertEquals(start,e.oldStart());assertEquals(start,e.newStart());
    }
    @Test void noShowRequiresFullWaitingPeriod(){
        Booking one=create();clock.now=start.plusSeconds(14*60+59);
        assertThrows(IllegalStateException.class,()->service.markNoShow(one.id,"absent"));
        clock.now=start.plusSeconds(15*60);service.markNoShow(one.id,"absent");
        assertEquals(BookingStatus.NO_SHOW,one.status());assertEquals(BookingEventType.NO_SHOW,history.get(history.size()-1).eventType());
    }
    @Test void sessionBoundariesAndCompletion(){
        Booking one=create();Session s=new Session(1,one);SessionService sessions=new SessionService(clock,bookings);sessions.start(s,one);
        clock.now=clock.now.plusSeconds(55*60);assertEquals(SessionService.TimeState.ENDING_SOON,sessions.timeState(s,5).state());
        clock.now=clock.now.plusSeconds(5*60);assertEquals(SessionService.TimeState.TIME_UP,sessions.timeState(s,5).state());
        sessions.finish(s);assertEquals(BookingStatus.COMPLETED,one.status());assertEquals(SessionStatus.COMPLETED,s.status());
    }
    @Test void returnValidatesAllConditionsBeforeMutation(){
        Booking one=create();Session s=new Session(1,one);EquipmentService equipment=new EquipmentService(clock,kits,issues,log);
        equipment.issue(s);SessionService sessions=new SessionService(clock,bookings);sessions.start(s,one);clock.now=clock.now.plusSeconds(61*60);sessions.finish(s);
        int before=log.size();assertThrows(IllegalArgumentException.class,()->equipment.returnEquipment(s,Map.of(1L,"ok")));
        assertNull(issues.get(0).returnedAt());assertEquals(before,log.size());assertEquals(EquipmentStatus.ISSUED,kits.get(0).status());
        assertEquals(List.of(1L,2L),equipment.returnEquipment(s,Map.of(1L,"ok",2L,"damaged")));
        assertEquals(EquipmentStatus.RETURNED_PENDING,kits.get(0).status());assertEquals(EquipmentStatus.FAULTY,kits.get(1).status());
    }
    @Test void replacementLogsFaultAndIssue(){
        Booking one=create();Session s=new Session(1,one);EquipmentService equipment=new EquipmentService(clock,kits,issues,log);
        equipment.issue(s);new SessionService(clock,bookings).start(s,one);
        assertEquals(3L,equipment.replace(s,1).replacementId());assertEquals(EquipmentStatus.FAULTY,kits.get(0).status());
        assertEquals(EquipmentStatus.ISSUED,kits.get(2).status());assertNotNull(issues.get(0).returnedAt());
        assertThrows(IllegalStateException.class,()->equipment.changeStatus(kits.get(0),EquipmentStatus.AVAILABLE,"invalid"));
    }
    @Test void noReplacementStillRecordsFaultAndRemoval(){
        Booking one=create();Session s=new Session(1,one);EquipmentService equipment=new EquipmentService(clock,kits,issues,log);
        equipment.issue(s);equipment.changeStatus(kits.get(2),EquipmentStatus.FAULTY,"unavailable");
        new SessionService(clock,bookings).start(s,one);
        var result=equipment.replace(s,1);assertTrue(result.faultRecorded());assertNull(result.replacementId());assertEquals("NO_REPLACEMENT",result.reason());
        assertEquals(EquipmentStatus.FAULTY,kits.get(0).status());assertNotNull(issues.get(0).returnedAt());
    }
    @Test void slotCheckRejectsEquipmentNotCurrentlyAvailable(){
        for(EquipmentStatus status:List.of(EquipmentStatus.ISSUED,EquipmentStatus.RETURNED_PENDING,EquipmentStatus.SERVICING,EquipmentStatus.FAULTY)) {
            kits.get(0).setStatus(status);kits.get(1).setStatus(status);
            assertEquals(BookingService.SlotCode.NOT_ENOUGH_KITS,service.checkSlot(start,60,2,game,arena,null).code());
        }
    }
    @Test void issueNeverTakesKitsFromAnotherArena(){
        Booking one=create();Session s=new Session(1,one);
        kits.removeIf(k->k.arenaId==1 && k.id>1);
        kits.add(new EquipmentSet(4,2,"OTHER1",EquipmentKind.HEADSET));kits.add(new EquipmentSet(5,2,"OTHER2",EquipmentKind.HEADSET));
        EquipmentService equipment=new EquipmentService(clock,kits,issues,log);
        assertThrows(IllegalStateException.class,()->equipment.issue(s));assertTrue(issues.isEmpty());
    }
    @Test void sameSlotLeavesHistoryUntouched(){
        Booking one=create();int before=history.size();
        assertTrue(service.reschedule(one.id,start,game,arena,"same").success());assertEquals(before,history.size());
    }
    @Test void cancelReturnsRecordedPrepaymentWithoutExecutingRefund(){
        Booking one=service.create(1,game,tariff,arena,start,2,new BigDecimal("100.00"));
        assertEquals(new BigDecimal("100.00"),service.cancel(one.id,"cancel"));
        assertEquals(BookingStatus.CANCELLED,one.status());
    }
    @Test void finishReturnsOvertime(){
        Booking one=create();Session s=new Session(1,one);SessionService sessions=new SessionService(clock,bookings);
        sessions.start(s,one);clock.now=clock.now.plusSeconds(90*60);
        assertEquals(30,sessions.finish(s).overtimeMin());
    }
    @Test void startRejectsBookingOutsideService(){
        Booking foreign=new Booking(99,1,1,1,1,start,60,2,BigDecimal.ZERO,clock.instant());
        Session s=new Session(1,foreign);
        assertThrows(IllegalArgumentException.class,()->new SessionService(clock,bookings).start(s,foreign));
    }
}
