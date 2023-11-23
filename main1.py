import random   #Для ИИ


class BoardOutException(Exception):   #Исключение при выстреле за пределы доски
    pass
class ShotTwiceException(Exception):   #Исключение при выстреле в ту точку, куда уже стреляли
    pass
class EndShips(Exception):   #Корабли кончились
    pass


class Koord:   #Класс точек, от 0 до 5(По индексу)
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'({self.x} {self.y})'


class Ship:   #Класс корабликов
    def __init__(self, size, end, direction):
        self.size = size
        self.end = end
        self.direction = direction
        self.lives = size

    @property
    def koords(self):
        koords_list = []
        for k in range(self.size):
            koord_x = self.end.x
            koord_y = self.end.y
            if self.direction:
                koord_x += k
            else:
                koord_y += k
            koords_list.append(Koord(koord_x, koord_y))
        return koords_list


class Board:   #Класс доски
    def __init__(self, field_size=6, hid=True):
        self.field_size = field_size
        self.hid = hid
        self.field = [['o'] * field_size for i in range(6)]
        self.ships_list = []
        self.shots = []
        self.taken = []
        self.ships_count = 0
        self.damaged_koord = Koord(-1, -1)

    def add_ship(self, ship):   #Функция добавления корабля
        for g in ship.koords:
            if g in self.taken or self.out(g):
                raise BoardOutException

        for g in ship.koords:
            self.field[g.x][g.y] = '■'
            self.taken.append(g)
        self.ships_list.append(ship)
        self.ships_count += 1

    def out(self, koord):   #Функция, которая не позволит выйти за пределы поля
        return not (0 <= koord.x < self.field_size and 0 <= koord.y < self.field_size)

    def contour(self, ship, reveal=False):   #Установка границ
        limits = [[j, i] for j in (-1, 0, 1) for i in (-1, 0, 1)]
        for m in ship.koords:
            for xx, yy in limits:
                xy_koord = Koord(m.x + xx, m.y + yy)
                if not self.out(xy_koord):
                    if reveal:
                        self.field[xy_koord.x][xy_koord.y] = '.'
                        self.shots.append(Koord(xy_koord.x, xy_koord.y))
                    else:
                        self.taken.append(xy_koord)

    def shot(self, koord):   #Выстрелы
        check = False

        if not self.hid and self.damaged_koord != Koord(-1, -1):  #Здесь инструкции для бота, как работать
            print('Обстрелянная точка', self.damaged_koord)
            if bool(random.randint(0, 1)):
                count = 1
            else:
                count = -1
            if bool(random.randint(0, 1)):
                bot_koord = Koord(self.damaged_koord.x + count, self.damaged_koord.y)
            else:
                bot_koord = Koord(self.damaged_koord.x, self.damaged_koord.y + count)
            koord = bot_koord

        if self.out(koord):
            print('Ну ты и мазила')
            raise BoardOutException
        if koord in self.shots:
            print('Там ничего не осталось, стреляй в другие места, мб получится')
            raise ShotTwiceException
        self.taken.append(koord)
        self.shots.append(koord)
        for ship in self.ships_list:
            if koord in ship.koords:   #Действия при попадании по кораблю, при любом попадании
                self.field[koord.x][koord.y] = '#'
                ship.lives -= 1
                if ship.lives == 0:   #Действия при устранении корабля
                    print('Потеряли пацанов')
                    self.contour(ship, reveal=True)
                    self.ships_count -= 1
                    print(self)
                    check = True
                    if not self.hid:
                        self.damaged_koord = Koord(-1, -1)

                else:   #Здесь если его ранили
                    print('Есть пробитие')
                    print(self)
                    if not self.hid:
                        self.damaged_koord = koord
                check = True

        if not check:   #Промах
            self.field[koord.x][koord.y] = 'T'
            print('Тут противника не было, меняемся')
        return check

    def __str__(self):   #Отрисовка доски
        up = '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for h, i in enumerate(self.field):
            up += f'\n{h + 1} | ' + ' | '.join(i) + ' |'
            if self.hid:
                up = up.replace('■', 'o')
        return up


class Player:
    def __init__(self, field, enemy_field):
        self.field = field
        self.enemy_field = enemy_field

    def ask(self):
        coord = Koord(6, 5)
        return coord

    def move(self):
        while True:
            try:
                if not self.enemy_field.shot(self.ask()):
                    return True
            except BoardOutException:
                continue
            except ShotTwiceException:
                continue
            except EndShips:
                print('ГГ ВП')
                return False


class User(Player):
    def ask(self):
        while True:   #Тут у игрока запрашивают координаты для удара
            if self.enemy_field.ships_count != 0:
                hit = input('Введите координаты места, куда вы хотите нанести точечный удар (X Y): ')
                try:
                    x = int(hit[0])
                    y = int(hit[-1])
                except ValueError:
                    print('Нужны целые числа')
                    continue
                else:
                    return Koord(x - 1, y - 1)
            else:
                raise EndShips


class Bot(Player):
    def ask(self):   #Здесь же у бота координаты запрашивают. Он бьёт по случайным точкам
        coord = Koord(random.randint(0, self.field.field_size - 1), random.randint(0, self.field.field_size - 1))
        print('Компьютер бабахнул по координатам: ', Koord(coord.x+1, coord.y+1))
        return coord


class Game:
    def __init__(self):
        self.player_board = self.random_field(False)
        self.bot_board = self.random_field(True)
        self.player = User(self.player_board, self.bot_board)
        self.bot = Bot(self.bot_board, self.player_board)

    def random_board(self, hide):    #Расстановка кораблей по полю. Бывает срабатывает не с первого раза, поэтому здесь защита от беск.цикла
        field6 = Board(6, hide)
        ship_length_list = [3, 2, 2, 1, 1, 1, 1]
        for ship_length in ship_length_list:
            tries = 0
            while True:
                try:
                    ship = Ship(ship_length,
                                Koord(random.randint(0, field6.field_size), random.randint(0, field6.field_size)),
                                bool(random.randint(0, 1)))
                    field6.add_ship(ship)
                    field6.contour(ship, False)
                    break
                except BoardOutException:
                    tries += 1
                    if tries < 150:
                        continue
                    else:
                        return False
        return field6

    def random_field(self, hide):
        field6 = self.random_board(hide)
        while not field6:
            field6 = self.random_board(hide)
        return field6

    def greet(self):   #Приветствие
        print('Сейчас вы будете играть в Морской Бой. \n'
              'Правила всем известны. \n'
              'Погнали чё \n'
              '-----------\n'
              'Ваша доска:')
        print(self.player_board)

    def mode(self):   #Условия выигрыша
        if self.player_board.ships_count == 0:
            print('Бот выиграл. Начало восстания машин')
            return False
        if self.bot_board.ships_count == 0:
            print('Игрок победил. Юхууу....')
            return False
        else:
            return True

    def loop(self):   #Цикл
        while self.mode():
            print('-----------')
            print('Ваш ход, куда стрелять надумаете?: ')
            print(self.bot_board)
            print('Кол-во живых кораблей противника: ', self.bot_board.ships_count)
            print('Кол-во ваших живых кораблей: ', self.player_board.ships_count)
            self.player.move()
            print(self.bot_board)
            if self.bot_board.ships_count != 0:
                print('Ход компьютера')
                self.bot.move()
                print(self.player_board)

    def start(self):   #Запуск игры
        self.greet()
        self.loop()


gameeeeeee = Game()
gameeeeeee.start()

#Наслаждайтесь