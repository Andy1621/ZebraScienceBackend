from DBClass import DbOperate
import random
'''
修改数据库，更改数据库字段名，新增字段
'''
class ModifyDB():
    Operate=DbOperate()
    db=Operate.client.Business
    '''
    更改collection集合的字段名，由old_name改为new_name
    '''
    def change_fieldname(self,collection,old_name,new_name):
        self.db[collection].update({},{$rename:{old_name:new_name}},False,True )

    '''
    在collection中新增字段，字段名,初始值
    给所有的document新增一个字段{'field_name':'initial_value'}
    initial_values是一个包含初始值取值范围的列表，随机从其中取出值来给新字段复制
    '''
    def add_field(self,collection,field_name,initial_values):
        for item in self.db[collection].find():
            item[field_name]=random.choice(initial_values)
            self.db[collection].update({'_id':item['_id']},{'$set':item})