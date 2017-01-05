# -*- coding: utf-8 -*-
class TourResult:

    def __init__(self, list_of_players):
        self.list_of_players = list_of_players

    def tour_result(self, num_of_tour):
        self.s = []
        for el in self.list_of_players:
            if ('Турнир_' + str(num_of_tour)) in el.keys():
                if el['Турнир_' + str(num_of_tour)] != '0' and el['Турнир_' + str(num_of_tour)] != 0:
                    x = [int(el['Турнир_' + str(num_of_tour)]), [el['Фамилия'], el['Имя']]]
                    self.s.append(x)
            else:
                return False
            self.s.sort(reverse=True)

        return self.s
#         for el in self.s:
#             print(el[1][0], el[1][1], ' - ', el[0])
