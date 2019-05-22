from DBClass import DbOperate
import random
import copy
from itertools import permutations
'''
修改数据库，更改数据库字段名，新增字段
'''
class ModifyDB():
    Operate=DbOperate()
    db=Operate.client.Scholar
    '''
    更改collection集合的字段名，由old_name改为new_name
    '''
    def change_field_name(self,collection,old_name,new_name):
        for item in self.db[collection].find():
            item[new_name]=item[old_name]
            self.db[collection].update_one({'_id':item['_id']},{'$set':item})
        self.db[collection].update({},{'$unset':{old_name:''}},multi=True)

    '''
    在collection中新增字段，字段名,初始值
    给所有的document新增一个字段{'field_name':'initial_value'}
    initial_values是一个包含初始值取值范围的列表，随机从其中取出值来给新字段复制
    '''
    def add_field(self,collection,field_name,initial_values):
        for item in self.db[collection].find():
            item[field_name]=random.choice(initial_values)
            self.db[collection].update({'_id':item['_id']},{'$set':item})

    '''
    在mongodb数据库中新建一个collection,插入一个类似[{'key':value'},……]
    的字典数组，更新数据库
    '''
    def create_collection(self,collection,key_values):
        self.db[collection].insert_many(key_values)

    '''
    将论文表中所有的author字段改为dict类型
    并且所有作者初始值为''
    '''
    def author_list2dct(self,sci_source):
        count = 0
        for item in self.db[sci_source].find():
            count +=1
            print(count)
            authors = item['author']
            if type(authors)!=dict:
                temp = {}
                for author in authors:
                    author=author.replace('.','') #key中不能有.,否则报错
                    temp[author]=''
                self.db[sci_source].update_one({'paperid':item['paperid']},{'$set':{'author':temp}})

    '''
    判断学者表论文表的名字是不是一个人的
    比如 Yao Jiao Jiao Yao Yao,Jiao  Yao-Jiao和姚佼可能是一个人
    '''

    def is_same_person(self,sci_name, scmessage_name):
        if scmessage_name == sci_name:
            return True
        from xpinyin import Pinyin
        pin = Pinyin()
        name_words = pin.get_pinyin(scmessage_name).split('-')
        temp = copy.deepcopy(name_words)
        for name in name_words:
            temp.append(name.capitalize())
        name_words = temp
        name_words_list = []
        for item in permutations(name_words):
            words = ''
            for i in item:
                words += i
            if len(name_words_list)>1000:
                break
            name_words_list.append(words)
        sci_name = sci_name.replace(' ', '').replace('-', '').replace(',','')
        for item in name_words_list:
            if sci_name in item:
                return True
        return False

    '''
    将sci_dource表的author列表改为{author:scholarid}字典
    '''
    def insert_author_id(self,sci_source,scmessage):
        count=0
        for item in self.db[scmessage].find({}):
            count += 1
            print('第'+str(count)+'个学者')
            scid,name,papers = item['scid'],item['name'],item['paper']
            print(name)
            # continue
            for paper in papers:
                paperid,paper_author = paper['paperid'],paper['author']
                sci_source_paper=self.db[sci_source].find_one({'paperid':paperid})
                if sci_source_paper != None and len(sci_source_paper['author'])>0:
                    if type(sci_source_paper['author'])==dict:
                        for author_name in list(sci_source_paper['author'].keys()):
                            author_name = author_name.replace('.','')
                            if self.is_same_person(author_name,name):
                                sci_source_paper['author'][author_name]=scid
                        self.db[sci_source].update({'paperid':paperid},{'$set':{'author':sci_source_paper['author']}})
                    else:
                        temp = dict()
                        for author_name in sci_source_paper['author']:
                            temp[author_name] = ''
                            if self.is_same_person(author_name,name):
                                temp[author_name] = scid
                        self.db[sci_source].update({'paperid': paperid},{'$set': {'author': temp}})

if __name__ == '__main__':
    modifydb = ModifyDB()
    modifydb.insert_author_id('paper' , 'scmessage')
    #将userid更名为user_id
    # modifydb.change_field_name('user','userid','user_id')
