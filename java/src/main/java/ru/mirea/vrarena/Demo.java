package ru.mirea.vrarena;
import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class Demo {
    private static Instant at(String time){return Instant.parse("2026-11-10T"+time+":00Z");}
    private static Clock clock(String time){return Clock.fixed(at(time),ZoneOffset.UTC);}
    public static void main(String[] args){
        List<Booking> bookings=new ArrayList<>();List<BookingHistory> history=new ArrayList<>();List<EquipmentSet> kits=new ArrayList<>();
        List<SessionEquipment> issues=new ArrayList<>();List<EquipmentStatusLog> log=new ArrayList<>();
        for(int i=1;i<=8;i++)kits.add(new EquipmentSet(i,1,"SET-"+i,EquipmentKind.HEADSET));
        Game game=new Game(1,"VR",2,6,false);Tariff hour=new Tariff(1,1L,"60 min",60,BigDecimal.TEN,false,true);Tariff shortTariff=new Tariff(2,1L,"45 min",45,BigDecimal.TEN,false,true);Arena arena=new Arena(1,"Arena",8,10,true);
        BookingService booking=new BookingService(clock("12:00"),bookings,kits,history);
        Booking b1=booking.create(101,game,hour,arena,at("18:00"),4,BigDecimal.ZERO);
        System.out.println("Бронь 1: "+b1.status()+", слот 18:00");
        System.out.println("Конфликт 19:00: "+booking.checkSlot(at("19:00"),30,4,game,arena,null).code());
        Booking b2=booking.create(103,game,shortTariff,arena,at("19:15"),5,BigDecimal.ZERO);
        Booking b3=booking.create(104,game,shortTariff,arena,at("20:30"),6,BigDecimal.ZERO);
        System.out.println("Перенос на занятый слот: "+booking.reschedule(b3.id,at("19:30"),game,arena,"запрос").check().code());
        booking.cancel(b2.id,"запрос");System.out.println("Отмена брони 2: "+b2.status());
        System.out.println("Повторный перенос: "+booking.reschedule(b3.id,at("19:30"),game,arena,"запрос").success());
        Session session=new Session(1,4,60);EquipmentService equipment=new EquipmentService(clock("18:02"),kits,issues,log);
        System.out.println("Выданные комплекты: "+equipment.issue(session,1));
        new SessionService(clock("18:02"),bookings).start(session,b1);
        System.out.println("Замена комплекта 2: "+equipment.replace(session,2));
        System.out.println("Время сеанса в 19:04: "+new SessionService(clock("19:04"),bookings).timeState(session,5));
        new SessionService(clock("19:09"),bookings).finish(session);
        equipment=new EquipmentService(clock("19:09"),kits,issues,log);
        System.out.println("Возврат: "+equipment.returnEquipment(session,Map.of(1L,"ok",3L,"ok",4L,"ok",5L,"ok")));
        new BookingService(clock("19:45"),bookings,kits,history).markNoShow(b3.id,"неявка");
        System.out.println("Неявка брони 3: "+b3.status());
        System.out.println("История: "+history.stream().map(h->h.eventType().name()).toList());
        System.out.println("Записей в истории: "+history.size()+", журнал статусов: "+log.size());
    }
}
