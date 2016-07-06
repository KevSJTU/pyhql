# -*- coding: utf-8 -*-
import six
from abc import ABCMeta
from collections import defaultdict
from datetime import datetime
class Field(dict):
    """保存Field的信息"""
    def __init__(self, **kwargs): # known special case of dict.__init__
        assert "type" not in kwargs
        if "params" in kwargs:
            assert isinstance(kwargs["params"], list)
            assert all(isinstance(k, Field) for k in kwargs["params"]) #约定params存储参数
            assert all(not k.startswith("_") for k in kwargs) # _开头的作为保留字段
            kwargs["_params_dict"] = {p["name"] : p for p in kwargs["params"]}
        super(Field, self).__init__(**kwargs)
    def description(self):
        ret = {
            "type" : self.__class__.__name__,
            "id" : self.identifier()
        }
        for key, val in self.items():
            if key == "params":
                ret["params"] = [v.description() for v in val]
            elif key.startswith("_") or key == "func":
                pass
            else:
                ret[key] = val
        return ret
    def identifier(self):
        if "_model_name" in self:
            return self["_model_name"] + "." + self["name"]
        return self["name"]

    def valid_params(self, js):
        if js == None and self["_params_dict"] is not None:
            return False
        if js is not None and self["_params_dict"] is None:
            return False
        if len(self["params"]) != len(self["_params_dict"]): return False
        for v in js:
            if v["name"] not in self["_params_dict"]:
                return False
            if not self["_params_dict"][v["name"]].valid(v["val"]):
                return False
        return True


class IntField(Field):
    def valid(self, v, check_val = True):
        if check_val and not isinstance(v["val"], int): return False
        if not self.valid_params(v.get("params")): return False
        return True

class FloatField(Field):
    def valid(self, v, check_val = True):
        if check_val and not (isinstance(v["val"], float) or isinstance(v["val"], int)): return False
        if not self.valid_params(v.get("params")): return False
        return True
class DateField(Field):
    def valid(self, v, check_val = True):
        if check_val:
            if not isinstance(v["val"], str): return False
            try:
                datetime.strptime(v["val"], "%Y%m%d")

            except:
                return False
        if not self.valid_params(v.get("params")): return False
        return True
class StrField(Field):
    def valid(self, v, check_val = True):
        if check_val and not isinstance(v["val"], str): return False
        if not self.valid_params(v.get("params")): return False
        return True

class BoolField(Field):
    def valid(self, v, check_val = True):
        if check_val and not isinstance(v["val"], bool): return False
        if not self.valid_params(v.get("params")): return False
        return True

class FileSelector(dict):
    pass


class ItemMeta(ABCMeta):
    def __new__(mcs, class_name, bases, attrs):
        new_bases = tuple(base._class for base in bases if hasattr(base, '_class'))
        _class = super(ItemMeta, mcs).__new__(mcs, 'x_' + class_name, new_bases, attrs)
        fields = getattr(_class, 'fields', {})
        new_attrs = {}
        for n in dir(_class):
            v = getattr(_class, n)
            if isinstance(v, Field):
                fields[n] = v
                v["_model"] = _class
                v["_model_name"] = class_name
                v["name"] = n
            elif n in attrs:
                new_attrs[n] = attrs[n]

        new_attrs['fields'] = fields
        new_attrs['_class'] = _class
        return super(ItemMeta, mcs).__new__(mcs, class_name, bases, new_attrs)


@six.add_metaclass(ItemMeta)
class Model:
    """
    model用来描述如何访问某个格式的文件
    """
    fields = {}
    file_selector = [] # 可以重载,用来保存如何选择查询的文件
    @classmethod
    def _init_env_(cls):
        """
        初始化模型需要的代码.比如import模块
        :return:
        """
        pass

class TextModel(Model):
    """
    用于表示json,tsv等格式的数据
    """
    @classmethod
    def load(cls, str):
        """
        用于载入一行数据
        :param str: 一行文本
        :return: data
        """
        raise "Not Implemented"

class NaiveView(TextModel):
    """
    有些文件是不保存的,如果需要就生成
    """
    @classmethod
    def __mapper__(cls, str, fields):
        pass
    @classmethod
    def __reducer__(cls, group, fields):
        pass
    view_src = None # 重载参数,添加依赖




class ParquetModel(Model):
    """
    用于表示parquet格式的数据
    """
    pass
class DescribeRelation:
    def __init__(self, model, primary):
        self.model = model
        self.primary = primary

class DataBase:
    def __init__(self):
        self.concepts = {}
        self.describe_relations = defaultdict(dict)
        self.fields = {}
    def concept(self, name, **kwargs):
        self.concepts[name] = kwargs
    def describe(self, concept, model, primary=None):
        """
        数据是用来描述一个什么概念.
        :param concept: 这个概念的名称
        :param model: model
        :param primary: 主键
        :return:
        """
        for f in model.fields.values():
            self.fields[f.identifier()] = f
        self.describe_relations[concept][model.__name__] = DescribeRelation(model, primary)

    def description(self):
        return {
            "datas" : [self.concept_description(concept) for concept in self.concepts]
        }
    def concept_description(self, concept):
        concept_data = self.concepts[concept]
        return {
            "name" : concept,
            "desc" : concept_data["desc"],
            "tables" : [self.table_description(r) for r in self.describe_relations[concept].values()]
        }
    def table_description(self, relation):
        return {
            "name" : relation.model.__name__,
            "fields": [x.description() for x in relation.model.fields.values()]
        }

class ConditionExp:
    def __init__(self, name, vals):
        self.name = name
        self.vals = vals
    @classmethod
    def from_json(cls, js, db):
        """
        接受js格式的数据
        {
            "id" : string, //当前的值域id
            "vals" : [
                {
                    "val" : val, //根据不同的Field,不同的类型
                    "params" : [{"name": string, "val": val}] | null //val根据不同的Field,不同的类型
                }
            ]
        }
        :param js:
        :return:
        """
        _id = js["id"]
        assert _id in db.fields
        f = db.fields[_id]
        vals = js["vals"]
        for v in vals:
            if not f.valid(v):
                raise "id: %s, invalid %s" % (_id, str(v))
        return ConditionExp(_id, vals)

class TargetExp:
    def __init__(self, name, params):
        self.name = name
        self.params = params
    @classmethod
    def from_json(cls, js, db):
        """
        接受js格式的数据
        {
            "id" : string, //当前的值域id
            "vals": [{
                "params" : [{"name": string, "val": val}] | null //val根据不同的Field,不同的类型
            }]
        }
        :param js:
        :return:
        """
        _id = js["id"]
        assert _id in db.fields
        f = db.fields[_id]
        params = js["params"]
        for p in params:
            if not f.valid(p, False):
                raise "id: %s, invalid %s" % (_id, str(p))
        return TargetExp(_id, params)
class SelectExp:
    def __init__(self, _id, concept, conditions):
        self._id = _id
        self.concept = concept
        self.conditions = conditions
    @classmethod
    def from_json(cls, js, db):
        """
        接受js格式的数据
        {
            "type": "select",
            "_id" : string, //当前表达式的id
            "concept" : string, //当前表达式在选什么
            "conditions" : [ConditionExp], //选择条件
        }
        :param js:
        :return:
        """
        _id = js["_id"]
        concept = js["concept"]
        assert concept in db.concepts
        conditions = [ConditionExp.from_json(x, db) for x in js["conditions"]]
        return SelectExp(_id, concept, conditions)

class GroupExp:
    def __init__(self,_id, concept, targets):
        self._id = _id
        self.concept = concept
        self.targets = targets
    @classmethod
    def from_json(cls, js, db):
        """
        接受的js格式
        {
            "type" : "group",
            "_id" : string, //当前表达式的id
            "concept" : string, //当前表达式group哪个concept的属性
            "targets" : [TargetExp], //选择target
        }
        :param js:
        :param db:
        :return:
        """
        _id = js["_id"]
        concept = js["concept"]
        assert concept in db.concepts
        targets = [TargetExp.from_json(x, db) for x in js["targets"]]
        return GroupExp(_id, concept, targets)
class AggExp:
    @classmethod
    def from_json(cls, js, db):
        """
        接受的js格式
        {
            "type" : "agg",
            "_id" : string, //当前表达式的id
            "concept" :
        }
        :param js:
        :param db:
        :return:
        """
class QueryLanguage:
    @classmethod
    def from_json(cls, js, db):
        """
        {
            "exps" : [Exp], //一个表达式的数组
        }
        Exp格式: {
            "type" : string
            ....
        }
        :param js:
        :return:
        """
        exps = [globals()[d["type"]].from_json(d, db) for d in js["exps"]]
