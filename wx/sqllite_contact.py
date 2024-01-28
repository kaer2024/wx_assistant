
import config as config
import pysqlcipher3.dbapi2 as sqlite
import json
import myEncoder as dbToJson
import myEncoder
import wx_mongodb as wx_write
import hashlib
import os
def decrypt(path, fileName,oldTimestamp,isGroup):
    # ———————————————————————————————————数据库操作———————————————————————————————————
    # 参考：https://www.sqlite.org/pragma.html#pragma_wal_checkpoint

    # 连接数据库如果文件不存在，会自动在当前目录创建:
    db = sqlite.connect(path + fileName)
    # 创建一个Cursor:
    db_cursor = db.cursor()

    # ————————————————————————————————————解密数据DB———————————————————————————————————
    # sqlcipher加密解密参考：https://github.com/sqlcipher/android-database-sqlcipher/issues/94
    # sqlcipher开源库地址：https://github.com/sqlcipher/sqlcipher/issues
    # sqlcipherApi：https://www.zetetic.net/sqlcipher/sqlcipher-api/
    db_cursor.execute("PRAGMA key='" + config.DB_KEY + "';")
    db_cursor.execute("PRAGMA cipher_compatibility=3;")
    db_cursor.execute("PRAGMA cipher_page_size=1024;")
    db_cursor.execute("PRAGMA kdf_iter=64000;")
    db_cursor.execute("PRAGMA cipher_hmac_algorithm=HMAC_SHA1;")
    db_cursor.execute("PRAGMA cipher_kdf_algorithm=PBKDF2_HMAC_SHA1;")
    # 将解密文件导入新的DB文件
    decrypt = config.DB_OUT_PATH + 'decrypt_' + fileName
    if (os.path.exists(decrypt)):
        os.remove(decrypt)
    db_cursor.execute("ATTACH DATABASE '" + decrypt + "' AS db_de KEY '" + config.DB_NEW_KEY + "';  -- empty key will disable encryption")
    db_cursor.execute("SELECT sqlcipher_export('db_de');")
    db_cursor.execute("DETACH DATABASE db_de;")
    db_cursor.close()
    parse(decrypt,oldTimestamp,isGroup);

def parse(decryptPath,oldTimestamp,isGroup):
    db = sqlite.connect(decryptPath)
    db_cursor = db.cursor()
    all_table="";
    if isGroup:
        all_table =[('GroupMember',)];
    else:
        all_table = db_cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';").fetchall();
    for x in all_table:
        table_name = x[0]
        try:
            if isGroup:
                dbToJson.tableToJsonGroup(db_cursor,table_name)
            else:
                dbToJson.tableToJson2(db_cursor,table_name)
        except BaseException as e:
            print(e)
            continue
    db_cursor.close()
    db.close()

def wx_contact(path,fileName):
    db = sqlite.connect(path + fileName)
    db_cursor = db.cursor()
    query = 'SELECT * FROM WCContact'

    # 获取加密结果
    rows = db_cursor.execute(query)
    for x in  rows:
        item = {}
        # 更新md5对象
        s=x[0]
        # 创建md5对象
        md5 = hashlib.md5()
        md5.update(s.encode('utf-8'))
        #Chat_4570092fe23d49dbb9520b2b2ef89b2d
        result = md5.hexdigest()
        value='Chat_'+result
        item.update({'user_nick': s})
        item.update({'chat_table': value})
        # print(s,"====",item)
        wx_write.writeContact('wx_contact3', item)
