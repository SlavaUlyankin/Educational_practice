package ru.mirea.vrarena;
import java.time.Instant;
import java.util.Objects;
public final class Session {
    public final long id, bookingId, arenaId; public final int playersCount, durationMin;
    private final Booking booking;
    private SessionStatus status=SessionStatus.PREPARED; private Instant startedAt, actualEndAt;
    public Session(long id,Booking booking) {
        this.booking=Objects.requireNonNull(booking);
        if(id<=0 || booking.status()!=BookingStatus.CONFIRMED || booking.sessionId()!=null) throw new IllegalArgumentException("session/booking");
        this.id=id;this.bookingId=booking.id;this.arenaId=booking.arenaId();this.playersCount=booking.players;this.durationMin=booking.durationMin;
    }
    public SessionStatus status(){return status;} public Instant startedAt(){return startedAt;} public Instant actualEndAt(){return actualEndAt;}
    boolean matches(Booking b){return booking==b && booking.id==bookingId && booking.arenaId()==arenaId;}
    void verifyBookable(){if(!matches(booking) || booking.status()!=BookingStatus.CONFIRMED || booking.sessionId()!=null) throw new IllegalStateException("INVALID_BOOKING");}
    void start(Instant now){status=SessionStatus.IN_PROGRESS;startedAt=now;} void finish(Instant now){status=SessionStatus.COMPLETED;actualEndAt=now;}
}
