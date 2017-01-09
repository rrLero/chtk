# -*- coding: utf-8 -*-


class StatsPlayers:

    def get_number_of_tours(self, list_of_players, name, surname):

        self.counter_of_tours = 0
        self.rating = 0
        self.counter_of_gold = 0
        self.counter_of_silver = 0
        self.counter_of_bronze = 0

        for player in list_of_players:
            if player['Имя'] == name and player['Фамилия'] == surname:
                for val, key in player.items():
                    if 'Турнир_' in val and int(key) != 0:
                        self.counter_of_tours += 1
                        self.rating += int(key)
                        if int(key) == 800:
                            self.counter_of_gold += 1
                        elif int(key) == 560:
                            self.counter_of_silver += 1
                        elif int(key) == 400:
                            self.counter_of_bronze += 1
        return [self.rating, self.counter_of_tours, self.counter_of_gold, self.counter_of_silver, self.counter_of_bronze]
