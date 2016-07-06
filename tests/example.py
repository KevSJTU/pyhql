# -*- coding: utf-8 -*-
from pyhql.ddl import TextModel, ParquetModel, IntField, StrField, DataBase, BoolField, DateField, FileSelector, \
    SetField


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

    @classmethod
    def file_path_by_date(cls, date = None):
        pass
    # 重载file_selectors
    file_selectors = [
        FileSelector(desc = "选取哪一天的用户数据", func = file_path_by_date, params = [DateField(name = "date", desc="日期")])
    ]
    uid = IntField(desc = "用户的id", func = uid_func)
    age = IntField(desc = "用户的年龄",
                         cat = {-1 : "当前为空",
                                1 : "0~18岁",
                                2 : "19~24岁",
                                3 : "25~34岁",
                                4 : "35~44岁",
                                5 : "45~54岁",
                                6 : "55~64岁",
                                7 : "大于64岁"},
                   func = age_func)
    gender = IntField(desc = "用户的性别", func = gender_func,
                      cat = {-1 : "当前为空",
                             0 : "男",
                             1 : "女"})
    has_been_city = BoolField(desc = "最近出现在哪个城市", func = has_been_city_func, params = [IntField(name = "city_id",desc = "城市的ID")])

class Calllog(ParquetModel):
    uid = StrField(desc = "用户的ID", field = "uid")
    call_type = StrField(desc = "通话的类型", field = "callItem.call_type", cat = {"INCOMING" : "打入的电话", "OUTCOMING" : "打出的电话"})
    other_phone = StrField(desc = "对方的电话", field = "callItem.other_phone")
    @classmethod
    def file_path_by_date(cls, start_date, end_date):
        pass
    file_selectors = [
        FileSelector(desc = "选取哪个时间段的数据", func = file_path_by_date, params = [DateField(name = "start_date", desc = "起始日期"),DateField(name = "end_date", desc = "终止日期")])
    ]

    def is_outcoming_func(self, phone_set):
        pass

    is_outcoming = BoolField(desc = "是否是拨打该集合内的电话", func = is_outcoming_func, param = [SetField(name = "phone_set", desc = "拨打电话的集合", elm_type = StrField())])


db = DataBase()
db.concept("user", desc = "用户")
db.describe("user", UserProfile, "uid")
db.concept("calllog", desc = "通话记录")
db.describe("calllog", Calllog) #并没有primary key
db.foreign(Calllog.fields["uid"], "user")

print(db.description())

