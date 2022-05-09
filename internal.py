import cx_Oracle
import re
from pymongo import MongoClient
from crawl.html2text import *


def internal_f():
    client = MongoClient("mongodb://localhost:27017")  ##DB
    db = client.crawl  ##DB
    db['internal'].drop()

    majors = ['None', '전자공학부', '건축학부', '산업공학부', '고분자공학전공', '소재디자인공학', '환경공학', '응용화학', \
              '화학공학', '신소재공학부', '기계공학과', '기계설계공학과', '기계시스템공학과', '토목공학과', '토목공학과', \
              '컴퓨터공학과', '광시스템공학과', '메디컬IT융합공학과', '응용수학과', '대표 관리자', '경영학과', 'IT융합학과']

    connect = cx_Oracle.connect("abc/aiqlr1aiqlr@172.17.17.104:1521/kaiser")

    for major in majors:
        cursor = connect.cursor()
        sql = 'select * from (select ROWNUM, CREATE_DT, ARTICLE_TITLE,  DBMS_LOB.SUBSTR(ARTICLE_TEXT,32767,1), \
               DBMS_LOB.GETLENGTH(ARTICLE_TEXT),MEMBER_TEL,BOARD_NO,ARTICLE_NO from  nhome.v_abc_게시물글조회 \
               inner join nhome.v_abc_게시글관리자정보 \
               on nhome.v_abc_게시물글조회.board_no = nhome.v_abc_게시글관리자정보.board_no \
               order by CREATE_DT  desc) where MEMBER_TEL = \'{}\' AND rownum <=10 '.format(major)

        cursor.execute(sql)

        for row in cursor:
            # 문자열 제한 4000byte때문에 모든 내용을 가져올 수는 없음
            t = str(row[3])
            text = html2text(t)
            text = text.replace("**", "")
            text = text.replace("\n\n", "\n")

            matchObj = re.search('<[^0-9A-Z]', text)
            if matchObj:
                text2 = text[:matchObj.start()]
            else:
                text2 = text

            boardNo = row[6]
            articleNo = row[7]
            url = 'https://www.kumoh.ac.kr/_custom/kumoh/_common/board/index/{}.do?mode=view&articleNo={}'.format(boardNo,articleNo)

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
            if (str(row[5])=='None' or str(row[5]) == '대표 관리자'):
                temp = '교내정보'
            elif str(row[5]) == "건축학부" or str(row[5]) == "건축학전공" or str(row[5]) == '건축공학전공':
                temp = '건축학부'
            elif str(row[5]) == "산업공학부" or str(row[5]) == '산업경영공학전공' or str(row[5]) == "디자인공학전공" or str(row[5]) == '산업시스템공학전공' or str(row[5]) == '산업경영공학과':
                temp = '산업공학부'
            elif str(row[5]) == '전자공학부' or str(row[5]) == "전자 공학부" or str(row[5]) == '정보전자전공' or str(row[5]) == "제어및로봇전공" or str(row[5]) == "전자통신전공" or \
                    str(row[5]) == "전자및전파전공" or str(row[5]) == "전자IT융합전공":
                temp = '전자공학부'
            elif str(row[5]) == "화학소재공학부" or str(row[5]) == '고분자공학전공' or str(row[5]) == "소재디자인공학>전공" or str(row[5]) == "화학공학전공" or str(row[5]) == '신소재공학부' or str(row[5]) == '화학소재융합공학부' or str(row[5]) == '에너지융합소재공학부' or str(row[5]) == '소재디자인공학' or str(row[5]) == '응용화학' or str(row[5]) == '>화학공학' :
                temp = '화학소재공학부'
            elif str(row[5]) == "기계공학과" or str(row[5]) == '기계설계공학과' or str(row[5]) == "기계시스템공학과" or str(row[5]) == '기계 공학과' or str(row[5]) == '기계 설계공학과' or str(row[5]) == '기계융합공학과':
                temp = '기계공학과'
            elif str(row[5]) == "컴퓨터공학과" or str(row[5]) == '컴퓨터소프트웨어공학과' or str(row[5]) == "인공지능>공학과":
                temp = '컴퓨터공학과'
            elif str(row[5]) == "수리빅데이터학과" or str(row[5]) == '응용수학과':
                temp = '수리빅데이터학과'
            elif str(row[5]) == "환경공학과" or str(row[5]) == '환경공학':
                temp = '환경공학과'
            else:
                temp = str(row[5])

            r['source'] = temp

            r['title'] = str(row[2])
            r['date'] = str(row[1])
            r['url'] = url
            r['text'] = text2
            r['text2'] = ''
            r['img'] = ''
            r['subtitle'] = ''
            if r['text'] != "None" :
                if r['title'] != 0 :
                    db['internal'].insert_one(r)  # DB삽입

                    # print('\n\n')
                    # print(r)
                    # print(row[4])
                    # print('\n\n')

        cursor.close()

    connect.close()


if __name__ == '__main__':
    internal_f()



