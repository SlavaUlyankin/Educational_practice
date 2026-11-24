package ru.mirea.vrarena;
import java.time.Instant;
public record BookingHistory(long id, long bookingId, BookingEventType eventType, Instant changedAt,
                             Instant oldStart, Instant newStart, Long oldArenaId, Long newArenaId, String reason) { }
