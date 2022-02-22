from pymongo import MongoClient


def uploadGeneraltoDB():
  client = MongoClient("mongodb://localhost:27017")  ##DB

  db = client.crawl
  indata = list(db.internal.find({}, {'_id' : False}))[:3]


  db = client.crawl
  exdata = list(db.external.find({}, {'_id' : False}))[:3]


  db = client.post
  #table drop
  db.generalTable.drop()
  #table insert
  db.generalTable.insert_many(indata)
  db.generalTable.insert_many(exdata)

if __name__ == '__main__':
    uploadGeneraltoDB()
