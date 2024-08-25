## Endpoints
- Cоздавать и удалять места для совместных просмотров  
GET, POST, DELETE /api/v1/places/{place_id}
- Cоздавать, удалять, изменять или отменять совместные просмотры  
GET, POST, DELETE /api/v1/watches/{watch_id}
- Бронировать или отменять бронь для совместных просмотров  
GET, POST, DELETE /api/v1/reservations/{reservation_id}
- Поиск совместных просмотров по:
    - Юзер хосту
    - Фильму
    - Месту
    - Своим просмотрам   
GET /api/v1/watches?find=host|film|place|my-watches&id=\<id>