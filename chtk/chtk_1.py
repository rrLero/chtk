# -*- coding: utf-8 -*-
from points import Points
from tour_result import TourResult
import json
from getPlayer_from_list import GetPlayer

print('С каким годом будете работать 2016 или 2017')
year = int(input())

if year == 2016:
    f = open('new_list_2.txt', 'r')
    json_string = f.readline()
    parsed_string = json.loads(json_string)
    f.close()
elif year == 2017:
    f = open('new_list_2017.txt', 'r')
    json_string = f.readline()
    parsed_string = json.loads(json_string)
    f.close()


n = 1

points = Points()
tour_result = TourResult(parsed_string)


def number_of_tournaments():
    return len(parsed_string[0])-2


while n != 0:
    print('\n| Введите что Вы хотите делать:')
    print('| 0 - Если хотите выйти')
    print('| 1 - Если хотите добавить результаты нового турнира')
    print('| 2 - Если хотите вывести результаты турнира на выбор')
    print('| 3 - Если хотите увидеть рейтинг:')
    print('| 4 - Если хотите изменить данные игрока')
    print('| 5 - Если хотите добавить игрока игрока')
    print('| 6 - Если хотите создать новый файл на 2017 год')

    n = int(input())
    rating = {}
    print()

    if n == 1:
        s = int(input('| Введите номер турнира - '))
        for el in parsed_string:
            el['Турнир_' + str(s)] = 0
        print(parsed_string)
        i = 0
        q = int(input('| Введите к-во игроков принимавших участие - '))
        while i != q:
            y = False
            surname = input('Введите фамилию игрока - ')
            name = input('Введите имя игрока - ')
            player = GetPlayer(parsed_string)
            if player.get_player(name, surname):
                print('Такой игок есть в списке')
                p = int(input('Введите место на этом турнире которое занял игрок - '))
                if points.get_points(p):
                    parsed_string[player.get_string_number(name, surname)]['Турнир_' + str(s)] = points.get_points(p)
                    i += 1
                else:
                    print('Некорректный ввод')
            else:
                print('Некорректный ввод')
        f.close()
        f = open('new_list_2017.txt', 'w')
        f.write(json.dumps(parsed_string))
        f.close()
        print(parsed_string)

    elif n == 2:

        tour_result.tour_result(int(input('введите номер турнира - ')))

    elif n == 3:
        new_list = []
        for el in parsed_string:
            s = 1
            points_1 = 0
            while ('Турнир_' + str(s)) in el:
                points_1 += int(el['Турнир_' + str(s)])
                s += 1
            rating.update({el['Фамилия'] + ' ' + el['Имя']: points_1})
        while rating:
            for key, el in rating.items():
                if el == max(rating.values()):
                    new_list.append([key, el])
                    rating.pop(key)
                    break
        for el in new_list:
            print(el)

    elif n == 4:
        print('Введите фамилию игрока которого хотите изменить')
        surname = input()
        print('Введите имя игрока которого хотите изменить')
        name = input()
        player = GetPlayer(parsed_string)
        if player.get_player(name, surname):
            print('Такой игок есть в списке')
            print('Введите новую фамилию игрока которого хотите изменить')
            new_surname = input()
            print('Введите новое имя игрока которого хотите изменить')
            new_name = input()
            for el in parsed_string:
                if el['Фамилия'] == surname and el['Имя'] == name:
                    el['Имя'] = new_name
                    el['Фамилия'] = new_surname
                    f.close()
                    f = open('new_list_2017.txt', 'w')
                    f.write(json.dumps(parsed_string))
                    f.close()
                    break

    elif n == 5:
        new_player = {}
        print('Введите фамилию игрока которого хотите добавить')
        surname = input()
        print('Введите имя игрока которого хотите добавить')
        name = input()
        player = GetPlayer(parsed_string)
        while player.get_player(name, surname):
            print('Такой игок есть в списке')
            print('Введите новую фамилию игрока которого хотите добавить')
            surname = input()
            print('Введите новое имя игрока которого хотите добавить')
            name = input()
        new_player['Имя'] = name
        new_player['Фамилия'] = surname
        for i in range(1, number_of_tournaments()+1):
            new_player['Турнир_'+str(i)] = 0
        parsed_string.append(new_player)
        f = open('new_list_2017.txt', 'w')
        f.write(json.dumps(parsed_string))
        f.close()

    elif n == 6:
        parsed_string_new = []
        el_new = {}
        f = open('new_list_2.txt', 'r')
        json_string = f.readline()
        parsed_string = json.loads(json_string)
        f.close()
        i = 0
        for el in parsed_string:

            el_new['Фамилия'] = el['Фамилия']
            el_new['Имя'] = el['Имя']

            parsed_string_new.append(dict(el_new))

            i += 1

        print(parsed_string_new)
        f_2017 = open('new_list_2017.txt', 'w')
        f_2017.write(json.dumps(parsed_string_new))
   # f.close()