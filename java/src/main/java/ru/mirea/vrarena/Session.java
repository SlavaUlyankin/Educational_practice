package ru.mirea.vrarena;
import java.time.Instant;
public final class Session {
    public final long id; public final int playersCount, durationMin;
    private SessionStatus status=SessionStatus.PREPARED; private Instant startedAt, actualEndAt;
    public Session(long id,int playersCount,int durationMin) { if(id<=0 || playersCount<1 || durationMin<1) throw new IllegalArgumentException("session"); this.id=id;this.playersCount=playersCount;this.durationMin=durationMin; }
    public SessionStatus status(){return status;} public Instant startedAt(){return startedAt;} public Instant actualEndAt(){return actualEndAt;}
    void start(Instant now){status=SessionStatus.IN_PROGRESS;startedAt=now;} void finish(Instant now){status=SessionStatus.COMPLETED;actualEndAt=now;}
}
