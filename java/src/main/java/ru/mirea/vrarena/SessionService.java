package ru.mirea.vrarena;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Objects;
public final class SessionService {
    public enum TimeState { NOT_STARTED, RUNNING, ENDING_SOON, TIME_UP, COMPLETED }
    public record TimeResult(TimeState state,long remainingMin,long overtimeMin) { }
    private final Clock clock; private final List<Booking> bookings;
    public SessionService(Clock clock,List<Booking> bookings){this.clock=Objects.requireNonNull(clock);this.bookings=Objects.requireNonNull(bookings);}
    public Instant start(Session s,Booking b){
        Objects.requireNonNull(s);Objects.requireNonNull(b);
        if(s.status()!=SessionStatus.PREPARED || b.status()!=BookingStatus.CONFIRMED || b.sessionId()!=null) throw new IllegalStateException("INVALID_STATE");
        if(s.playersCount!=b.players || s.durationMin!=b.durationMin) throw new IllegalArgumentException("session/booking mismatch");
        Instant now=clock.instant();b.attachSession(s.id);s.start(now);return now.plus(Duration.ofMinutes(s.durationMin));
    }
    public TimeResult timeState(Session s,int warnMin){
        if(warnMin<0) throw new IllegalArgumentException("warnMin");
        if(s.status()==SessionStatus.PREPARED) return new TimeResult(TimeState.NOT_STARTED,0,0);
        if(s.status()==SessionStatus.COMPLETED) return new TimeResult(TimeState.COMPLETED,0,0);
        Instant now=clock.instant();if(now.isBefore(s.startedAt())) throw new IllegalStateException("INVALID_TIME");
        long seconds=Duration.between(now,s.startedAt().plus(Duration.ofMinutes(s.durationMin))).getSeconds();
        if(seconds> (long)warnMin*60) return new TimeResult(TimeState.RUNNING,seconds/60,0);
        if(seconds>0) return new TimeResult(TimeState.ENDING_SOON,seconds/60,0);
        return new TimeResult(TimeState.TIME_UP,0,Math.floorDiv(-seconds,60));
    }
    public void finish(Session s){Instant now=clock.instant();if(s.status()!=SessionStatus.IN_PROGRESS || !now.isAfter(s.startedAt())) throw new IllegalStateException("INVALID_STATE_OR_TIME");s.finish(now);bookings.stream().filter(b->Objects.equals(b.sessionId(),s.id) && b.status()==BookingStatus.CONFIRMED).forEach(b->b.setStatus(BookingStatus.COMPLETED));}
}
