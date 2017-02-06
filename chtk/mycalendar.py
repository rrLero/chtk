# -*- coding: utf-8 -*-
class MyCalendar:
    list_of_tournaments = {
        1: '17.01.2016',
        2: '31.01.2016',
        3: '14.02.2016',
        4: '27.02.2016',
        5: '13.03.2016',
        6: '27.03.2016',
        7: '10.04.2016',
        8: '17.04.2016',
        9: '30.04.2016',
        10: '22.05.2016',
        11: '28.05.2016',
        12: '19.06.2016',
        13: '26.06.2016',
        14: '24.07.2016',
        15: '09.08.2016',
        16: '02.10.2016',
        17: '16.10.2016',
        18: '06.11.2016',
        19: '11.12.2016',
        20: '25.12.2016',
        }
    list_of_tournaments_2017 = {
        1: '15.01.2017',
        2: '05.02.2017',

    }

    def get_date(self, n):
        if n in self.list_of_tournaments:
            return self.list_of_tournaments[n]
        else:
            return False

    def get_date_2017(self, n):
        if n in self.list_of_tournaments_2017:
            return self.list_of_tournaments_2017[n]
        else:
            return False
