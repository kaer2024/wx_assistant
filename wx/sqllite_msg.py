
import config as cf
import pysqlcipher3.dbapi2 as sqlite
import myEncoder as dbToJson
import os
def decrypt(path, fileName,oldTimestamp):
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
    db_cursor.execute("PRAGMA key='" + cf.DB_KEY + "';")
    db_cursor.execute("PRAGMA cipher_compatibility=3;")
    db_cursor.execute("PRAGMA cipher_page_size=1024;")
    db_cursor.execute("PRAGMA kdf_iter=64000;")
    db_cursor.execute("PRAGMA cipher_hmac_algorithm=HMAC_SHA1;")
    db_cursor.execute("PRAGMA cipher_kdf_algorithm=PBKDF2_HMAC_SHA1;")
    # 将解密文件导入新的DB文件
    decrypt = cf.DB_OUT_PATH + 'decrypt_' + fileName
    if (os.path.exists(decrypt)):
        os.remove(decrypt)
    db_cursor.execute("ATTACH DATABASE '" + decrypt + "' AS db_de KEY '" + cf.DB_NEW_KEY + "';  -- empty key will disable encryption")
    db_cursor.execute("SELECT sqlcipher_export('db_de');")
    db_cursor.execute("DETACH DATABASE db_de;")
    db_cursor.close()
    parse(decrypt,oldTimestamp);

def parse(decryptPath,oldTimestamp):
    # print("decryptPath",decryptPath)
    db = sqlite.connect(decryptPath)
    db_cursor = db.cursor()

    all_table = db_cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';").fetchall()
    # print("all_table",all_table)
    # print("all_table_count",len(all_table))

    for x in all_table:
        table_name = x[0]
        # print("Searching", table_name)
        try:
            # t = db_cursor.execute('SELECT * FROM ' + table_name + ';')
            dbToJson.tableToJson(db_cursor,table_name,oldTimestamp)
            # print('\n')

        except BaseException as e:
            print(e)
            continue
    db_cursor.close()
    db.close()