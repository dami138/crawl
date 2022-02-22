import cx_Oracle
import re
from pymongo import MongoClient


def internal_f():
    client = MongoClient("mongodb://localhost:27017")  ##DB
    db = client.crawl  ##DB
    db['internal'].drop()

    connect = cx_Oracle.connect("abc/aiqlr1aiqlr@172.17.17.104:1521/kaiser")
    cursor = connect.cursor()



    sql = 'select * from (select ROWNUM, CREATE_DT, ARTICLE_TITLE,  DBMS_LOB.SUBSTR(ARTICLE_TEXT,DBMS_LOB.GETLENGTH(ARTICLE_TEXT),1), ' \
          'DBMS_LOB.GETLENGTH(ARTICLE_TEXT) from  nhome.v_abc_게시물글조회 order by CREATE_DT  desc) where rownum <=50 '


    cursor.execute(sql)


    for row in cursor:

        t = row[3]
        tag = re.compile('<.*?>')
        text = re.sub(tag, '',str(t))
        text = text.replace('&nbsp;','')
        #
        # tag2 = re.compile('img src=\".*?\"')
        # search = re.search(tag2, t).group()
        # print(search)
        #
        # img = str(search) if str(search) != 'None' else ''
        # if re.search('cms', img):
        #     img = re.sub(r'.*?img src=\"', 'www.kumoh.ac.kr',img)
        # else:
        #     img = ''
        # print(img)

        r = dict()


        r['source'] = "교내정보"
        r['title'] = str(row[2])
        r['date'] = str(row[1])
        r['url'] = ''
        r['text'] = text
        r['text2'] = ''
        r['img'] = ''
        r['subtitle'] = ''

        if r['text'] != "None":
            db['internal'].insert_one(r)  # DB삽입

            #print(r)
            print(row[4])
            #print('\n\n')

    cursor.close()
    connect.close()


if __name__ == '__main__':
    internal_f()