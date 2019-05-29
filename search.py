from elasticsearch import Elasticsearch
from elasticsearch import helpers
from pymongo import MongoClient

ONCE = 10          # 调用mongo2es中find的数据条数
SKIPNUM = 0         # 第几次调用mongo2es函数
ERROR_ELE = []      # 未插入es的数据序号列表
INSERT_NUM = 1      # 一次批量插入的条数

class zebrasearch():
    """
    连接Elaticsearch
    """
    def connect_es(self, host, port):
        self.es = Elasticsearch([{u'host': host, u'port': port}], timeout=3600)

    """
    连接到mongodb
    """
    def connect_mongo(self, host, port):
        self.client = MongoClient(host, port)

    """
    将mongodb中的db数据库的collection插入
    elaticsearch的index索引的types中
    """
    def mongo2es(self, db, collection, index, types):
        db = self.client[db]
        collection = db[collection]
        count = 0
        actions = []
        tmp = collection.find().skip(SKIPNUM * ONCE).limit(ONCE)
        for item in tmp:
            item = dict(item)
            item.pop('_id')
            action = {
                "_index": index,
                "_type": types,
                "_source": item
            }
            actions.append(action)
            count += 1
            print('第' + str(SKIPNUM * ONCE + count) + '篇论文已加入列表')
            try:
                if len(actions) == INSERT_NUM:
                    print("截止到" + str(SKIPNUM * ONCE + count) + "篇论文正在准备插入")
                    helpers.bulk(client=self.es, actions=actions)
                    actions.clear()
            except:
                actions.clear()
                ERROR_ELE.append(SKIPNUM * ONCE + count)
        if count > 0:
            helpers.bulk(self.es, actions)

    """
    将es的index索引的types清空
    """
    def cleartypes(self, index, types):
        query = {'query': {'match_all': {}}}
        self.es.delete_by_query(index=index, body=query, doc_type=types)


if __name__ == '__main__':
    zebrasearch = zebrasearch()
    zebrasearch.connect_es(u'139.199.96.196', 9200)
    zebrasearch.connect_mongo('139.199.96.196', 27017)
    # zebrasearch.mongo2es('Business', 'mechanism', 'business', 'user')
    # print(zebrasearch.es.search(index='business', doc_type='scisource'))
    # zebrasearch.cleartypes('busscisource', 'scisource')

    for i in range(0, 756):
        print("第" + str(i) + "轮")
        zebrasearch.mongo2es('Business', 'scmessage', 'scholar_index', '_doc')
        SKIPNUM += 1

    print(ERROR_ELE)
