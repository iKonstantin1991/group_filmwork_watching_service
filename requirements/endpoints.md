## Endpoints
- Cоздавать и удалять места для совместных просмотров  
POST, DELETE /api/v1/places/{place_id}
- Получить места для совместных просмотров:
    - все места GET /api/v1/places?only_open=True|False
    - по place_id GET /api/v1/places/{place_id}
    - свои GET /api/v1/places/my
- Cоздавать и отменять совместные просмотры  
POST, DELETE /api/v1/watches/{watch_id}
- Поиск совместных просмотров по:
    - Юзер хосту GET /api/v1/watches/find?host_id=<host_id> (можно задавать несколько фильтров)
    - Фильму GET /api/v1/watches/find?film_id=<film_id>
    - Месту GET /api/v1/watches/find?place_id=<place_id>
    - Просмотру GET /api/v1/watches/find?watch_id=<watch_id> или GET /api/v1/watches/{watch_id}
    - Своим просмотрам GET /api/v1/watches/my  
    - Все просмотры GET /api/v1/watches/find
- Бронировать или отменять бронь для совместных просмотров  
POST, DELETE /api/v1/reservations/{reservation_id}
- Получить брони для совместных просмотров:
    - все брони GET /api/v1/reservations
    - по юзер хосту GET /api/v1/reservations?host_id=<host_id> (можно задавать несколько фильтров)
    - по фильму GET /api/v1/reservations?film_id=<film_id>
    - по участнику GET /api/v1/reservations?participant_id=<participant_id>
    - указать фильтр с только будущими просмотрами GET /api/v1/reservations?only_incoming=True 
    - по reservation_id GET /api/v1/reservations/{reservation_id}
    - свои GET /api/v1/reservations/my
- Обновление статуса брони (успешная оплата или нет)  
POST /api/v1/{reservation_id}/complete