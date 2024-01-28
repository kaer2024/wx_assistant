import pymongo
import json
import config as cf
import uuid

# myclient = pymongo.MongoClient('mongodb://18.218.72.82:27017')
uri = "mongodb://kaer:kaer2023@18.218.72.82:27017/?authMechanism=DEFAULT"
myclient = pymongo.MongoClient(uri)
mydb = myclient['chat_gpt_x']


def writeMsg(table, jsonStr):
    jsonStr['messageId'] = uuid.uuid4().int >> 64
    if "@" in jsonStr["msgContent"]:
        jsonStr['isSpecial'] = "1"
    else:
        jsonStr['isSpecial'] = "0"
    chat_table = jsonStr['chat_table']
    print('chat_table11', chat_table)
    myquery = {"chat_table": chat_table}
    wxContactMycol = mydb["WCContact"]
    mydoc = list(wxContactMycol.find(myquery))
    print('WCContact mydoc', len(mydoc))
    jsonStr['isGroup'] = "0"
    user_nick = ''
    isGroup = False
    if len(mydoc) > 0:
        for x in mydoc:
            user_nick = x['m_nsAliasName']
            print("WCContact results", x['m_nsAliasName'])
    else:
        wxContactMycol = mydb["GroupContact"]
        mydoc = list(wxContactMycol.find(myquery))
        print('GroupContact mydoc', mydoc)
        if len(mydoc) > 0:
            jsonStr['isGroup'] = "1"
            isGroup = True
            for x in mydoc:
                user_nick = x['nickname']
                print("GroupContact results", x['m_nsAliasName'])
                if "周五交流群" not in user_nick:
                    print("group not 周五交流群 results", x['m_nsAliasName'])
                    return
        else:
            print("没有好友群信息")
            return
    wxMsgTableCol = mydb['wxMsgTable']
    if isGroup:
        jsonStr['from_id'] = user_nick
        jsonStr['to_id'] = cf.ROBOT_WEIXIN_ID
        if jsonStr['msgStatus'] == 3:
            jsonStr['from_id'] = cf.ROBOT_WEIXIN_ID
            jsonStr['to_id'] = user_nick
    else:
        jsonStr['from_id'] = cf.ROBOT_WEIXIN_ID
        jsonStr['to_id'] = user_nick
        if jsonStr['msgStatus'] == 3:
            jsonStr['from_id'] = user_nick
            jsonStr['to_id'] = cf.ROBOT_WEIXIN_ID
    x = wxMsgTableCol.insert_one(jsonStr)
    print('writeMsg', x.inserted_id)


def writeContact(table, jsonStr):
    jsonStr['messageId'] = uuid.uuid4().int >> 64
    mycol = mydb[table]
    myquery = {"m_nsAliasName": jsonStr['m_nsAliasName']}
    wxContactMycol = mydb["WCContact"]
    results = list(wxContactMycol.find(myquery))
    mydocCount = len(results)
    if mydocCount <= 0:
        x = mycol.insert_one(jsonStr)
        print('writeContact', x.inserted_id)


def writeContactGroup(table, jsonStr):
    jsonStr['messageId'] = uuid.uuid4().int >> 64
    mycol = mydb[table]
    myquery = {"m_nsAliasName": jsonStr['m_nsAliasName']}
    wxContactMycol = mydb["GroupContact"]
    results = list(wxContactMycol.find(myquery))
    mydocCount = len(results)
    if mydocCount <= 0:
        x = mycol.insert_one(jsonStr)
        print('GroupContact', x.inserted_id)
