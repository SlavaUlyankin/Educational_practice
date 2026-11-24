package ru.mirea.vrarena;
import java.math.BigDecimal;
import java.util.Objects;
public record Tariff(long id, Long gameId, String name, int durationMin, BigDecimal price, boolean prepaymentRequired, boolean active) {
    public Tariff { Objects.requireNonNull(name); Objects.requireNonNull(price); if (id <= 0 || durationMin <= 0 || price.signum() < 0) throw new IllegalArgumentException("tariff"); }
}
