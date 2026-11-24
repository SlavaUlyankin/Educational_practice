package ru.mirea.vrarena;
import java.util.Objects;
public final class EquipmentSet {
    public final long id, arenaId; public final String inventoryCode; public final EquipmentKind kind;
    private EquipmentStatus status=EquipmentStatus.AVAILABLE;
    public EquipmentSet(long id,long arenaId,String inventoryCode,EquipmentKind kind){if(id<=0 || arenaId<=0) throw new IllegalArgumentException("equipment");this.id=id;this.arenaId=arenaId;this.inventoryCode=Objects.requireNonNull(inventoryCode);this.kind=Objects.requireNonNull(kind);}
    public EquipmentStatus status(){return status;} void setStatus(EquipmentStatus s){status=s;}
}
