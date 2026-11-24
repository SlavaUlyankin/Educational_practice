package ru.mirea.vrarena;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.Objects;
public final class Booking {
    public final long id, clientId, gameId, tariffId;
    public final int durationMin, players;
    public final BigDecimal prepaidAmount;
    public final Instant createdAt;
    private long arenaId; private Instant start; private BookingStatus status = BookingStatus.CONFIRMED; private Long sessionId;
    public Booking(long id, long clientId, long gameId, long tariffId, long arenaId, Instant start, int durationMin, int players, BigDecimal prepaidAmount, Instant createdAt) {
        if (id <= 0 || clientId <= 0 || gameId <= 0 || tariffId <= 0 || arenaId <= 0 || durationMin <= 0 || players <= 0) throw new IllegalArgumentException("booking");
        this.prepaidAmount=Objects.requireNonNull(prepaidAmount); if (prepaidAmount.signum()<0) throw new IllegalArgumentException("prepaidAmount");
        this.id=id; this.clientId=clientId; this.gameId=gameId; this.tariffId=tariffId; this.arenaId=arenaId; this.start=Objects.requireNonNull(start); this.durationMin=durationMin; this.players=players; this.createdAt=Objects.requireNonNull(createdAt);
    }
    public long arenaId() { return arenaId; } public Instant start() { return start; }
    public BookingStatus status() { return status; } public Long sessionId() { return sessionId; }
    void reschedule(Instant time, long arena) { start=time; arenaId=arena; }
    void setStatus(BookingStatus value) { status=value; }
    void attachSession(long id) { if (id<=0 || sessionId!=null) throw new IllegalStateException("session"); sessionId=id; }
}
