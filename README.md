#API для работы с аппаратной частью умного склада
Содержание:  
1. Классы-наследники StorageApi и их основные методы
2. Класс StorageMaker
3. Маршруты
4. Вспомогательные классы
  
  #Классы Storage
  1. StorageApi - родитель всех классов с названием Storage. 
  Он работает на основе запросов к аппаратной части, при этом, все методы возвращают текст.
  Для инициализации требует хост и порт сервера с запущенной аппаратной частью.
  Имеет следующие методы:
      * `get_schema_api()`
      * `put_item_api(data)`
      * `position_api(destination)  `
  
  2. RenderStorage - наследник StorageApi, отвечает за отрисовку схемы склада, при инициализации собирает все данные, которые можно собрать для работы со складом.
  Основная функция - `render()`, остальные функции служебные. 
 
  3. Storage - наследник RenderStorage, в нем определена вся логика распределения товаров на складе.
  Методы:
  
      * `put(way_bill)` - принимает на вход объект класса WayBill, вызывает служебный метод 
      `_solve_how_to_put(items)`, в который передает список объектов Items, возвращает в итоге
      2 варианта ответа:
        1. OK
        2. ERROR  
       * `get(uuid = "", type_of_work = 0, cell_name = "")` - в зависимости от параметра, может искать позицию на складе, как через uuid, так и через имя полки.
       При type_of_work=0, использует uuid, не требуя cell_name.
       При type_of_work=1, использует cell_name, не требуя uuid.  
   4. StorageImproved - наследник Storage, был создан, чтобы просто добавить массив unique_cells, 
   который упрощает рендер html-страниц, в unique_cells нет клеток, которые находятся в одной группе объединения.
   # Класс StorageMaker
   Этот класс необходим для хранения в себе объекта StorageImproved, через которого осуществляется вся логика программы.
   Также класс решает важную проблему сохранения данных: `save()` вызывает переопределенный магический метод `__del__()`, который всегда вызывается при уничтожении объекта сборщиком мусора.
   Таким образом, переопределение метода `__del__()` позволяет сохранить данные, даже при аварийном завершении работы. 