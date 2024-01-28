import json

import numpy as np
from pysqlcipher3._sqlite3 import OperationalError

import hashlib
import config as cf_wx
import wx_mongodb as wx_write


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            # utf-8会报错：'utf-8' codec can't decode byte 0xfc in position 14: invalid start byte
            return str(obj, encoding='ISO-8859-15')
        return json.JSONEncoder.default(self, obj)


def tableToJson(cursor, table,oldTimestamp):
    query = 'SELECT * FROM ' + table + ' where msgCreateTime>=' + str(oldTimestamp)
    try:
        rows = cursor.execute(query)
        items = []
        for row in rows:
            # print(row)
            item = {}
            i = 0
            for key in cursor.description:
                item.update({key[0]: row[i]})
                i = i + 1
            item.update({'chat_table':table})
            print("item",item)
            items.append(item)
            wx_write.writeMsg(table, item)
        # 注意不要写道for里面了，不然数据结果不对
        # js = json.dumps(items, ensure_ascii=False, cls=MyEncoder, indent=4)
        # print(items)
    except OperationalError as oper:
        pass
    except Exception as e:
        print("Exception",repr(e))



def tableToJson2(cursor, table):
    query = 'SELECT * FROM ' + table
    try:
        rows = cursor.execute(query)
        items = []
        for row in rows:
            # print(row)
            item = {}
            i = 0
            add=True
            for key in cursor.description:
                # item.update({key[0]: row[i]})
                if key[0]== 'm_nsUsrName' and 'wxid' not in row[i] and row[i]!='zhl1149249801':
                    # print("m_nsUsrName not in",key[0])
                    add=False
                    continue
                if key[0]=='m_nsAliasName':
                    item.update({key[0]: row[i]})
                if key[0]=='m_nsUsrName':
                    item.update({key[0]: row[i]})
                if key[0] == 'nickname':
                    item.update({key[0]: row[i]})
                i = i + 1
            if add:
                s = row[0]
                # 创建md5对象
                md5 = hashlib.md5()
                md5.update(s.encode('utf-8'))
                # Chat_4570092fe23d49dbb9520b2b2ef89b2d
                result = md5.hexdigest()
                value = 'Chat_' + result
                # item.update({'user_nick': s})
                item.update({'chat_table': value})
                # print("tableToJson2",item)
                items.append(item)
                wx_write.writeContact(table, item)
    except OperationalError as oper:
        pass
    except Exception as e:
        print("Exception",repr(e))


def tableToJsonGroup(cursor, table):
    query = 'SELECT * FROM ' + table
    try:
        rows = cursor.execute(query)
        items = []
        for row in rows:
            # print(row)
            item = {}
            i = 0
            add=True
            for key in cursor.description:
                # item.update({key[0]: row[i]})
                if key[0]=='m_nsAliasName':
                    item.update({key[0]: row[i]})
                if key[0]=='m_nsUsrName':
                    item.update({key[0]: row[i]})
                if key[0] == 'nickname':
                    item.update({key[0]: row[i]})
                i = i + 1
            if add:
                s = row[0]
                # 创建md5对象
                md5 = hashlib.md5()
                md5.update(s.encode('utf-8'))
                # Chat_4570092fe23d49dbb9520b2b2ef89b2d
                result = md5.hexdigest()
                value = 'Chat_' + result
                # item.update({'user_nick': s})
                item.update({'chat_table': value})
                items.append(item)
                wx_write.writeContactGroup(table, item)
    except OperationalError as oper:
        pass
    except Exception as e:
        print("Exception",repr(e))



def tableToFile(cursor, table):
    query = 'SELECT * FROM ' + table
    rows = cursor.execute(query)
    items = []
    for row in rows:
        item = {}
        # 参考：https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
        for idx, col in enumerate(cursor.description):
            value = row[idx]
            item.update({col[0]: value})
        items.append(item)

    # 注意不要写道for里面了,不然数据结果不对
    json_name = ""
    if (table.endswith('.db')):
        json_name = table[:(table.__len__ - 3)]
    else:
        json_name = table
    file = open(cf_wx.DB_OUT_JSON_PATH + json_name + ".json", 'w+')
    # ensure_ascii默认为True,汉字会被编码成'\u4e00\u6839\u806a'
    js = json.dumps(items, ensure_ascii=False, cls=MyEncoder, indent=4)
    file.write(js)
    file.close()
