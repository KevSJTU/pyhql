# -*- coding: utf-8 -*-
import six
from abc import ABCMeta

class Field(dict):
    """保存Field的信息"""
    pass
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

class DataBase:
    def __init__(self):
        pass
    def describe(self, concept, model):
        """
        数据是用来描述一个什么概念.
        :param concept: 这个概念的名称
        :param model: model
        :return:
        """
        pass
    def fields(self, primary_key):
        """
        返回数据库中的,primary_key
        :param primary_key: 主键
        :return: [Field]
        """
        pass
    def __getitem__(self, **kwargs):
        """
        选中需要查询的数据的范围.
        :return:
        """
        pass
