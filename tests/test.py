# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/1 22:49

class T:
    def ttt(self, *, aa=None, bb=None):
        print(aa)
        print(bb)


t = T()
t.ttt(aa=222, bb=333)
