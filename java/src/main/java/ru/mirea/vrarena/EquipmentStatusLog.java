package ru.mirea.vrarena;
import java.time.Instant;
public record EquipmentStatusLog(long equipmentId, EquipmentStatus oldStatus, EquipmentStatus newStatus, Instant changedAt, String comment) { }
