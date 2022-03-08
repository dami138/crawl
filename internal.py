import cx_Oracle
import re
from pymongo import MongoClient
from html2text import *

def internal_f():
    client = MongoClient("mongodb://localhost:27017")  ##DB
    db = client.crawl  ##DB
    db['internal'].drop()

    connect = cx_Oracle.connect("abc/aiqlr1aiqlr@172.17.17.104:1521/kaiser")
    cursor = connect.cursor()


    sql =  'select * from (select ROWNUM, CREATE_DT, ARTICLE_TITLE,  DBMS_LOB.SUBSTR(ARTICLE_TEXT,32767,1), ' \
          'DBMS_LOB.GETLENGTH(ARTICLE_TEXT),MEMBER_TEL from  nhome.v_abc_게시물글조회 \
          inner join nhome.v_abc_게시글관리자정보 \
          on nhome.v_abc_게시물글조회.board_no = nhome.v_abc_게시글관리자정보.board_no \
          order by CREATE_DT  desc) where rownum <=50 '



    cursor.execute(sql)


    for row in cursor:
        #문자열 제한 4000byte때문에 모든 내용을 가져올 수는 없음
        t = str(row[3])
        text = html2text(t)
        text = text.replace("\n\n","\n")


        # tag = re.compile('<.*?>')
        # text = re.sub(tag, '',str(t))
        # text = text.replace('&nbsp;','').replace('\\r\\n','\n')
        # text = text.replace('\n\n','\n')
        #
        #tag2 = re.compile('img src=\".*?\"')
        #search = re.search(tag2, str(t)).group()
        #print(search)

        #img = str(search) if str(search) != 'None' else ''
        #if re.search('cms', img):
        #    img = re.sub(r'.*?img src=\"', 'www.kumoh.ac.kr',img)
        #else:
        #    img = ''
        #print(img)



        r = dict()

        r['source'] = "교내정보" if (str(row[5]) == 'None' or str(row[5]) == '대표 관리자') else str(row[5])
        r['title'] = str(row[2])
        r['date'] = str(row[1])
        r['url'] = ''
        r['text'] = text
        r['text2'] = ''
        r['img'] = ''
        r['subtitle'] = ''

        if r['text'] != "None":
            db['internal'].insert_one(r)  # DB삽입

            print('\n\n')
            print(r)
            print(row[4])
            print('\n\n')

    cursor.close()
    connect.close()


if __name__ == '__main__':
    internal_f()


