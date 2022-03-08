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

  while(cnt < 3):
    n = random.randint(0,50)

    interData = db.internal.find({'source':"교내정보"}, {'_id' : False})[n]

    if 'img src=' not in interData ['text'] and '/cms/' not in interData['text'] :
        print(interData)
        print('\n')
        db2.generalTable.insert_one(interData)
        cnt += 1


  n = random.randint(0,30)
  db2.generalTable.insert_one(db.external.find({'source': "AI타임스"}, {'_id' : False})[n])
  db2.generalTable.insert_one(db.external.find({'source': "전자신문"}, {'_id' : False})[n])
  db2.generalTable.insert_one(db.external.find({'source': "KBS"}, {'_id' : False})[n])


  print("generalTable 생성 완료")
