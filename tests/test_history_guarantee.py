"""Проверки журнала при отсутствии общего хранилища."""
import unittest
from datetime import datetime, timedelta

from vr_arena.a1_slots import create_booking
from vr_arena.a4_bookings import cancel_booking, mark_no_show, reschedule_booking
from vr_arena.models import BookingEventType, EquipmentSet


class HistoryGuaranteeTests(unittest.TestCase):
    def test_events_are_retained_without_external_history(self):
        now = datetime(2026, 11, 10, 12)
        kits = [EquipmentSet(1, 'one')]
        bookings = []
        b, _, _ = create_booking(1, 1, 1, now + timedelta(hours=1), 30, 1, 0,
                                 1, 1, bookings, kits, now)
        reschedule_booking(bookings, b.booking_id, now + timedelta(hours=2),
                           kits, 1, 1, now)
        cancel_booking(bookings, b.booking_id, now)
        self.assertEqual([e.event_type for e in b.history],
                         [BookingEventType.CREATED, BookingEventType.RESCHEDULED,
                          BookingEventType.CANCELLED])
        self.assertEqual(b.history[1].old_start_time, now + timedelta(hours=1))
        self.assertEqual(b.history[1].new_start_time, now + timedelta(hours=2))

    def test_no_show_and_shared_history(self):
        now = datetime(2026, 11, 10, 12)
        history, bookings = [], []
        b, _, _ = create_booking(1, 1, 1, now + timedelta(hours=1), 30, 1, 0,
                                 1, 1, bookings, [EquipmentSet(1, 'one')], now,
                                 history=history)
        mark_no_show(bookings, b.booking_id, now + timedelta(hours=1, minutes=15),
                     history=history)
        self.assertEqual(b.history, history)
        self.assertEqual(b.history[-1].event_type, BookingEventType.NO_SHOW)


if __name__ == '__main__':
    unittest.main()
