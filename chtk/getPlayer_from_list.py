# -*- coding: utf-8 -*-
class GetPlayer:

    def __init__(self, list_of_players):
        self.list_of_players = list_of_players

    def get_player(self, name, surname):
        for el in self.list_of_players:
            if name in el['Имя'] and surname in el['Фамилия']:
                return True
        return False

    def get_string_number(self, name, surname):
        self.counter=0
        for el in self.list_of_players:
            if name in el['Имя'] and surname in el['Фамилия']:
                return self.counter
            self.counter += 1
        return False
