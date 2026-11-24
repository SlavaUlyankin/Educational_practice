package ru.mirea.vrarena;
import java.time.Instant;
import java.util.Objects;
public record Client(long id, String fullName, String phone, String email, Instant createdAt) {
    public Client { if (id <= 0) throw new IllegalArgumentException("id"); Objects.requireNonNull(fullName); Objects.requireNonNull(phone); }
}
