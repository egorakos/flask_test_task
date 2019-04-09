# flask_test_task
В качестве тестового задания необходимо реализовать процесс Турнира между игроками:

  ##Входные данные:
  * 200 игроков:
      * id = uuid4()
      * name = any
      * power = random.ranint(1, 1000)
      * medals = 1000
      * money = 0

   * Турнир
      * Продолжительность турнира 2 минуты
      * Максимальное количество игроков в турнирной группе: 50
      * Игроки формируются в группы по параметру 'power'


  ##Процесс турнира:
    * Все игроки делятся на группы по 50 человек (сортируем пользователей по параметру power и объединяем в группы)
    * Между пользователями происходит соревнование кто больше всего соберет медалей за турнир
    * Игроки выигрывают медали нападая на других игроков
        * результат нападения высчитывается по формуле random.randint(-10, 10)
        * если результат отрицательный нападающий отдает это количество оппоненту
        * если результат положительный нападающий забирает медали у оппонента
    * Требования
       * игрок может нападать на любых игроков
       * игрок должен сделать хотя бы одно нападение за турнир
       * победитель определяется по количеству медалей на конец турнира
    * Ограничения
       * игрок не может нападать чаще чем раз в 5 секунды
       * 2 игрока не могут напасть одновременно на одного игрока 
       * 1 пользователь не может напасть дважды на одного и того же игрока
       * игрок не может нападать сам на себя
    * По завершении турнира победителям начисляются награды в зависимости от их места в группе
      * 1 место 300 money
      * 2 место 200 money
      * 3 место 100 money


Backend должен предоставлять API (Может быть дополнено или изменено по вашему усмотрению):
  ####Admin:
    * POST player (name, power, medals, money)  - добавляет пользователя
    * GET player (id) - возвращает данные игрока
    * POST tournament (start_timestamp) - начинает турнир
    * GET tournament (id) - возвращает состояние турнирных групп 

  ####Game:
    * GET opponent(player_id) - находит пользователя для нападения
    * POST attack(from_player_id, to_player_id) - атака 


В результате должно быть:
     * скрипт backend.py 
           * Запускает сервер турнира
     * скрипт tournament.py (должен запускаться локально, работает с backend.py)
           * генерирует 200 игроков
           * начинает турнир 
           * совершает атаки
           * по завершении турнира выводит список турнирных групп и победителей
