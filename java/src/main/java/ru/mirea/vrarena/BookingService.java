package ru.mirea.vrarena;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** Проверка слотов, операции с бронью и журнал успешных изменений. */
public final class BookingService {
    public enum SlotCode { OK, INVALID_INPUT, PLAYERS_OUT_OF_RANGE, IN_THE_PAST, NOT_ENOUGH_KITS, CONFLICT }
    public record SlotResult(SlotCode code, Long conflictId) { public boolean available(){ return code==SlotCode.OK; } }
    public record MoveResult(boolean success, SlotResult check, List<Instant> alternatives) { }
    private final Clock clock; private final List<Booking> bookings; private final List<EquipmentSet> kits; private final List<BookingHistory> history;
    public BookingService(Clock clock,List<Booking> bookings,List<EquipmentSet> kits,List<BookingHistory> history) {
        this.clock=Objects.requireNonNull(clock); this.bookings=Objects.requireNonNull(bookings); this.kits=Objects.requireNonNull(kits); this.history=Objects.requireNonNull(history);
    }
    public SlotResult checkSlot(Instant start,int duration,int players,Game game,Arena arena,Long excludeId) {
        Objects.requireNonNull(start);Objects.requireNonNull(game);Objects.requireNonNull(arena);
        if(duration<=0 || players<1 || !arena.active()) return new SlotResult(SlotCode.INVALID_INPUT,null);
        if(players<game.minPlayers() || players>game.maxPlayers() || players>arena.capacity()) return new SlotResult(SlotCode.PLAYERS_OUT_OF_RANGE,null);
        if(start.isBefore(clock.instant())) return new SlotResult(SlotCode.IN_THE_PAST,null);
        long usable=kits.stream().filter(k->k.arenaId==arena.id() && k.status()!=EquipmentStatus.FAULTY).count();
        if(usable<players) return new SlotResult(SlotCode.NOT_ENOUGH_KITS,null);
        Instant end=start.plus(Duration.ofMinutes((long)duration+arena.prepMin()));
        for(Booking b:bookings) {
            if(b.arenaId()!=arena.id() || b.status()!=BookingStatus.CONFIRMED || Objects.equals(excludeId,b.id)) continue;
            Instant bEnd=b.start().plus(Duration.ofMinutes((long)b.durationMin+arena.prepMin()));
            if(start.isBefore(bEnd) && b.start().isBefore(end)) return new SlotResult(SlotCode.CONFLICT,b.id);
        }
        return new SlotResult(SlotCode.OK,null);
    }
    public Booking create(long clientId,Game game,Tariff tariff,Arena arena,Instant start,int players,BigDecimal prepaidAmount) {
        Objects.requireNonNull(tariff);Objects.requireNonNull(prepaidAmount);
        if (!tariff.active() || (tariff.gameId()!=null && tariff.gameId()!=game.id())) throw new IllegalArgumentException("tariff/game mismatch");
        SlotResult result=checkSlot(start,tariff.durationMin(),players,game,arena,null);
        if(!result.available()) throw new IllegalStateException(result.code().name());
        long id=bookings.stream().mapToLong(b->b.id).max().orElse(0)+1; Instant now=clock.instant();
        Booking b=new Booking(id,clientId,game.id(),tariff.id(),arena.id(),start,tariff.durationMin(),players,prepaidAmount,now);
        bookings.add(b);record(b,BookingEventType.CREATED,now,null,start,null,arena.id(),"оформление брони");return b;
    }
    public void cancel(long id,String reason) {
        Booking b=active(id); Instant now=clock.instant(); if(!now.isBefore(b.start())) throw new IllegalStateException("TOO_LATE");
        b.setStatus(BookingStatus.CANCELLED);record(b,BookingEventType.CANCELLED,now,b.start(),null,b.arenaId(),null,reason);
    }
    public MoveResult reschedule(long id,Instant newStart,Game game,Arena target,String reason) {
        Booking b=active(id);Instant now=clock.instant();if(!now.isBefore(b.start())) throw new IllegalStateException("TOO_LATE");
        if(game.id()!=b.gameId) throw new IllegalArgumentException("game mismatch");
        SlotResult check=checkSlot(newStart,b.durationMin,b.players,game,target,b.id);
        if(!check.available()) {
            List<Instant> alternatives=new ArrayList<>();
            if(check.code()==SlotCode.CONFLICT) for(int minutes=15;minutes<=240 && alternatives.size()<3;minutes+=15) {
                Instant candidate=newStart.plus(Duration.ofMinutes(minutes));
                if(checkSlot(candidate,b.durationMin,b.players,game,target,b.id).available()) alternatives.add(candidate);
            }
            return new MoveResult(false,check,List.copyOf(alternatives));
        }
        Instant old=b.start();long oldArena=b.arenaId();b.reschedule(newStart,target.id());
        record(b,BookingEventType.RESCHEDULED,now,old,newStart,oldArena,target.id(),reason);
        return new MoveResult(true,check,List.of());
    }
    public void markNoShow(long id,String reason) {
        Booking b=active(id);Instant now=clock.instant();
        if(now.isBefore(b.start().plus(Duration.ofMinutes(15)))) throw new IllegalStateException("TOO_EARLY");
        b.setStatus(BookingStatus.NO_SHOW);record(b,BookingEventType.NO_SHOW,now,b.start(),null,b.arenaId(),null,reason);
    }
    private Booking active(long id) {
        Booking b=bookings.stream().filter(x->x.id==id).findFirst().orElseThrow(()->new IllegalArgumentException("NOT_FOUND"));
        if(b.status()!=BookingStatus.CONFIRMED || b.sessionId()!=null) throw new IllegalStateException("INVALID_STATE");return b;
    }
    private void record(Booking b,BookingEventType event,Instant at,Instant oldStart,Instant newStart,Long oldArena,Long newArena,String reason) {
        long next=history.stream().mapToLong(BookingHistory::id).max().orElse(0)+1;
        history.add(new BookingHistory(next,b.id,event,at,oldStart,newStart,oldArena,newArena,reason));
    }
}
