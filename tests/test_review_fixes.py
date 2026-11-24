"""Регрессии по полученным замечаниям о комплектах и истории."""
import unittest
from datetime import datetime, timedelta
from vr_arena.a1_slots import check_slot_availability
from vr_arena.a3_equipment import issue_equipment
from vr_arena.a4_bookings import reschedule_booking
from vr_arena.models import Booking, Code, EquipmentSet, EquipmentStatus, Reason, Session

class ReviewFixTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,11,10,12)
        self.start=self.now+timedelta(hours=6)
        self.booking=Booking(1,1,1,1,self.start,60,2,arena_id=1)

    def test_non_available_statuses_cannot_confirm_booking(self):
        for status in (EquipmentStatus.ISSUED, EquipmentStatus.RETURNED_PENDING,
                       EquipmentStatus.SERVICING, EquipmentStatus.FAULTY):
            with self.subTest(status=status):
                kits=[EquipmentSet(1,'one',status=status), EquipmentSet(2,'two')]
                result=check_slot_availability(self.start,60,2,1,2,[],kits,self.now)
                self.assertEqual(Reason.NOT_ENOUGH_KITS,result.reason)

    def test_issue_filters_by_session_arena(self):
        session=Session(1,2,60,arena_id=1,booking_id=1)
        kits=[EquipmentSet(1,'one',arena_id=1), EquipmentSet(2,'two',arena_id=2)]
        rows=[];log=[]
        code,_,_=issue_equipment(session,kits,rows,self.now,log)
        self.assertEqual(Code.NOT_ENOUGH_AVAILABLE,code)
        self.assertEqual([],rows)
        self.assertEqual(EquipmentStatus.AVAILABLE,kits[1].status)

    def test_same_slot_does_not_create_event(self):
        history=[]
        code,_,_=reschedule_booking([self.booking],1,self.start,[],1,2,self.now,history=history)
        self.assertEqual(Code.OK,code)
        self.assertEqual([],history)

if __name__=='__main__':
    unittest.main()
