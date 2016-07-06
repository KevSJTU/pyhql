# -*- coding: utf-8 -*-
import six
from abc import ABCMeta
from collections import defaultdict

class Field(dict):
    """保存Field的信息"""
    def __init__(self, **kwargs): # known special case of dict.__init__
        assert "type" not in kwargs
        if "params" in kwargs:
            assert isinstance(kwargs["params"], list)
            assert all(isinstance(k, Field) for k in kwargs["params"])
            assert all(not k.startswith("_") for k in kwargs)
        super(Field, self).__init__(**kwargs)
    def description(self):
        ret = {
            "type" : self.__class__.__name__
        }
        for key, val in self.items():
            if key == "params":
                ret["params"] = [v.description() for v in val]
            elif key == "_foreign":
                ret["_foreign"] = val
            elif key.startswith("_") or key == "func":
                pass
            else:
                ret[key] = val
        return ret
    def identifier(self):
        return self["_model"].__name__ + "." + self["name"]

class IntField(Field):
    pass
class FloatField(Field):
    pass
class DateField(Field):
    pass
class StrField(Field):
    pass
class BoolField(Field):
    pass
class DateField(Field):
    pass
class SetField(Field):
    pass
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
        self.describe_relations = defaultdict(list)
        self.foreigns = {}
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
        self.describe_relations[concept].append(DescribeRelation(model, primary))
    def foreign(self, field, concept):
        field["_foreign"] = concept
        self.foreigns[field.identifier()] = concept

    def description(self):
        return {
            "datas" : [self.concept_description(concept) for concept in self.concepts]
        }
    def concept_description(self, concept):
        concept_data = self.concepts[concept]
        return {
            "name" : concept,
            "desc" : concept_data["desc"],
            "tables" : [self.table_description(r) for r in self.describe_relations[concept]]
        }
    def table_description(self, relation):
        return {
            "name" : relation.model.__name__,
            "fields": [x.description() for x in relation.model.fields.values()]
        }
