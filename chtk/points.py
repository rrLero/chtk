# -*- coding: utf-8 -*-
class Points:

    list_of_points = {
        1: 800,
        2: 560,
        3: 400,
        4: 320,
        5: 280,
        6: 220,
        7: 180,
        8: 120,
        9: 80,
        10: 40,
        11: 20,
        12: 10,
        13: 5,
        14: 3,
        15: 2,
        16: 1,
    }

    def get_points(self, n):
        if n in self.list_of_points:
            return self.list_of_points[n]
        else:
            return False

    def get_place(self, n):
        for self.key, self.val in self.list_of_points.items():
            if self.val == n:
                return self.key
