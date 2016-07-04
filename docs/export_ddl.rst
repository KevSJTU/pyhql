============
导出的数据描述文件的格式
============


.. code-block:: javascript
    //example
    {
        "datas" : [
            {
                "name" : "user",
                "desc" : "用户",
                "tables" : [
                    {
                        "name" : "UserProfile",
                        "fields" : [
                            {
                                "name" : "uid",
                                "type" : "IntField",
                                "desc" : "用户的ID",
                                "primary" : true
                            },
                            {
                                "name" : "has_been_city",
                                "type" : "IntField",
                                "desc" : "最近是否出现在某城市",
                                "params" : [
                                    {
                                        "name" : "city_id",
                                        "type" : "IntField",
                                        "desc" : "城市名称",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "name" : "calllog",
                "desc" : "通话记录",
                "tables" : [
                    {
                        "name" : "Calllog",
                        "fields" : [
                            {
                                "name" : "uid",
                                "type" : "StrField",
                                "desc" : "用户的ID",
                                "foreign" : "user"
                            },
                            {
                                "name" : "call_type",
                                "type" : "StrField",
                                "desc" : "拨打类型",
                                "cat" : [
                                    {"name" : "INCOMING", "desc" : "拨入"},
                                    {"name" : "OUTCOMING", "desc" : "拨出"}
                                ]
                            },
                            {
                                "name" : "other_phone",
                                "type" : "StrField",
                                "desc" : "对方的电话"
                            }
                        ]
                    }
                ]
            }
        ]
    }
