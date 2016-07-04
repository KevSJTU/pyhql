# -*- coding: utf-8 -*-
from pyhql.ddl import TextModel, ParquetModel, IntField, StrField, DataBase, BoolField


class UserProfile(TextModel):
    modules = []
    @classmethod
    def _init_env_(cls):
        import json
        cls.modules["json"] = json
    @classmethod
    def load(cls, str):
        return cls.modules["json"].loads(str)
    @classmethod
    def uid_func(cls, data):
        return data["uid"]
    @classmethod
    def age_func(cls, data):
        return data["age"]
    @classmethod
    def gender_func(cls, data):
        return data["gender"]
    @classmethod
    def has_been_city_func(cls, data, city):
        if "location" not in data or data["location"] is None:
            return False
        location_js = cls.modules["json"].loads(data["location"])
        if location_js["locations"] is None:
            return False
        locations = location_js["locations"]
        return any(l["city"] == city  for l in locations)
    uid = IntField(name = "uid", desc = "用户的id", func = uid_func)
    age = IntField(name = "age", desc = "用户的年龄",
                         cat = {-1 : "当前为空",
                                1 : "0~18岁",
                                2 : "19~24岁",
                                3 : "25~34岁",
                                4 : "35~44岁",
                                5 : "45~54岁",
                                6 : "55~64岁",
                                7 : "大于64岁"},
                   func = age_func)
    gender = IntField(name = "gender", desc = "用户的性别", func = gender_func,
                      cat = {-1 : "当前为空",
                             0 : "男",
                             1 : "女"})
    has_been_city = BoolField(name = "has_been_city", desc = "曾经出现在哪个城市", func = has_been_city_func, param = [IntField(name = "城市的ID")])


