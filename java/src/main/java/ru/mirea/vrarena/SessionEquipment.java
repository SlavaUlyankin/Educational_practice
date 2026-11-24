package ru.mirea.vrarena;
import java.time.Instant;
import java.util.Objects;
public final class SessionEquipment {
    public final long sessionId,equipmentId; public final Instant issuedAt;
    private Instant returnedAt; private String condition;
    public SessionEquipment(long sessionId,long equipmentId,Instant issuedAt){if(sessionId<=0 || equipmentId<=0) throw new IllegalArgumentException("issue");this.sessionId=sessionId;this.equipmentId=equipmentId;this.issuedAt=Objects.requireNonNull(issuedAt);}
    public Instant returnedAt(){return returnedAt;} public String condition(){return condition;}
    void returned(Instant at,String condition){this.returnedAt=at;this.condition=condition;}
}
