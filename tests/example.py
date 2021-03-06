# -*- coding: utf-8 -*-
from pyhql.ddl import TextModel, ParquetModel, IntField, StrField, DataBase, BoolField, DateField, FileSelector, \
    NaiveView


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

    is_outcoming = BoolField(desc = "是否是拨打该集合内的电话", func = is_outcoming_func, param = [StrField(name = "phone", desc = "拨打电话")])

class CalllogUserView(NaiveView):
    modules = []
    @classmethod
    def _init_env_(cls):
        import json
        cls.modules["json"] = json
    @classmethod
    def load(cls, str):
        larr = str.strip().split("\t")
        larr[1] = cls.modules["json"].loads(larr[1])
        return larr
    @classmethod
    def uid_func(cls, data):
        return data[0]

    uid = StrField(desc = "用户的ID", func = uid_func)
    @classmethod
    def __mapper__(cls, str, field_exps):
        # 根据需要的field,进行的map操作
        pass
    @classmethod
    def __reducer__(cls, group, field_exps):
        # 根据需要的field,进行的reduce操作
        pass
    view_src = Calllog # 重载参数,添加依赖

    @classmethod
    def called_phone_func(cls, data, phone):
        return data[1]["called_phone"][phone]
    called_phone = BoolField(desc = "用户是否拨打拨打了该电话", param=StrField(name = "phone", desc = "拨打的电话"))

    @classmethod
    def called_type_func(cls, data, typ):
        return data[1]["called_type"][typ]
    called_type = BoolField(desc = "用户是否拨打了该类型的电话", param = StrField(name = "type", desc = "拨打电话类型"))




db = DataBase()
db.concept("user", desc = "用户")
db.describe("user", UserProfile, "uid")
db.describe("user", CalllogUserView, "uid")

db.concept("calllog", desc = "通话记录")
db.describe("calllog", Calllog)

print(db.description())

