package ru.mirea.vrarena;
import java.util.Objects;
public record Arena(long id, String name, int capacity, int prepMin, boolean active) {
    public Arena { Objects.requireNonNull(name); if (id <= 0 || capacity < 1 || prepMin < 0) throw new IllegalArgumentException("arena"); }
}
