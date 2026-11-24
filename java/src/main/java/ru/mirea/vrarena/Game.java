package ru.mirea.vrarena;
import java.util.Objects;
public record Game(long id, String title, int minPlayers, int maxPlayers, boolean allowsGroupMerge) {
    public Game { Objects.requireNonNull(title); if (id <= 0 || minPlayers < 1 || maxPlayers < minPlayers) throw new IllegalArgumentException("game"); }
}
