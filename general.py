from pymongo import MongoClient
import random

def uploadGeneraltoDB():
  client = MongoClient("mongodb://localhost:27017")  ##DB

  db = client.crawl
  db2 = client.post


  #table drop
  db2.generalTable.drop()


  #table insert

  cnt = 0
  n= 0

  while(cnt < 3):

    interData = db.internal.find({'source':"교내정보"}, {'_id' : False})[n]
    #interData = db.internal.find({'_id' : False})[n]
    #print(interData)

# 제너럴 테이블 생성이 안된다면,, 어쩔 수 없이 아래 두 줄 주석 해제해서 글없는 게시물이라도 넣기
    if 'img src' in interData['text']:
        interData['text'] = ''

    if 'img src=' not in interData ['text'] and '/cms/' not in interData['text'] :

        db2.generalTable.insert_one(interData)
        #print(n)
        #print(interData)
        #print('\n')

        cnt += 1

    n+=1




  db2.generalTable.insert_one(db.external.find({'source': "AITimes"}, {'_id' : False})[1])
  db2.generalTable.insert_one(db.external.find({'source': "ETNews"}, {'_id' : False})[1])
  db2.generalTable.insert_one(db.external.find({'source': "KBS"}, {'_id' : False})[1])


  print("generalTable 생성 완료")




if __name__ == '__main__':
    uploadGeneraltoDB()
