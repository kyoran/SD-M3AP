# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Created by kyoRan on 2022/1/4 10:10

from random import randint

class Color():

    def __init__(self, n_color=8888):
        self.color = []
        for i in range(n_color):
            self.color.append('#%06X' % randint(0, 0xFFFFFF))

    def __getitem__(self, item):
        return self.color[item]