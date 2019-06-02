import copy
import re
import Config
import random
import time
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from elasticsearch import Elasticsearch


class DbOperate:
    '''
    连接数据库和ES
    '''
    def __init__(self):
        self.host = Config.HOST
        self.port = Config.PORT_DB
        self.client = MongoClient(self.host, self.port)
        self.es = Elasticsearch([{u'host': Config.HOST, u'port': Config.PORT_ES}], timeout=3600)

#######################################################接口 1-9#######################################################
    '''
    取得Business数据库的指定表
    '''
    def getCol(self, name):
        db = self.client[Config.DATABASE]
        col = db[name]
        return col

    '''
    将url中的scholarID提取出来
    '''
    def scurl2id(self, url):
        pattern = re.compile('scholarID\/(.*?)(\?.*?|\s|\Z)')
        results = pattern.findall(url)
        for result in results:
            if len(result) > 0:
                return result[0]
            else:
                print('url转id错误！')
                return ''

    '''
    获取需要显示在页面上的用户数据，并修改res
    '''
    def get_user_data(self, find_user, res):
        # 去掉某些不必要字段
        find_user.pop('_id')
        find_user.pop('password')
        # 将star_list和follow_list中的id和简略信息一并返回
        # 令star_list列表中存放“资源的简略信息”
        tmp_star = copy.deepcopy(find_user['star_list'])
        find_user['star_list'].clear()
        res['reason'] = '收藏列表获取失败'
        for one_star in tmp_star:
            star_info = self.getCol('sci_source').find_one({'paperid': one_star})
            star_info.pop('_id')
            star_info.pop('source_url')
            star_info.pop('free_download_url')
            star_info.pop('abstract')
            find_user['star_list'].append(star_info)
        # 令follow_list列表中存放“用户的简略信息”
        tmp_follow = copy.deepcopy(find_user['follow_list'])
        find_user['follow_list'].clear()
        res['reason'] = '关注列表获取失败'
        for one_follow in tmp_follow:
            follow_info_all = self.getCol('scmessage').find_one({'scid': one_follow})
            follow_info_simple = {}
            follow_info_simple['scid'] = one_follow
            follow_info_simple['name'] = follow_info_all['name']
            follow_info_simple['mechanism'] = follow_info_all['mechanism']
            follow_info_simple['citedtimes'] = follow_info_all['citedtimes']
            follow_info_simple['resultsnumber'] = follow_info_all['resultsnumber']
            follow_info_simple['field'] = follow_info_all['field']
            find_user['follow_list'].append(follow_info_simple)
        # 若是专家类型用户登录，额外返回专家信息，暂时只有论文列表paper_list
        if find_user['user_type'] == 'EXPERT':
            res['reason'] = '获取论文列表失败'
            same_exp = self.getCol('scmessage').find_one({'scid': find_user['scid']})
            find_user['paper_list'] = same_exp['paper']
        # 设置返回值
        res['state'] = 'success'
        res['msg'] = find_user

    def LCS(self, input_x, input_y):
        # input_y as column, input_x as row
        dp = [([0] * (len(input_y) + 1)) for i in range(len(input_x) + 1)]
        for i in range(1, len(input_x) + 1):
            for j in range(1, len(input_y) + 1):
                if i == 0 or j == 0:  # 在边界上，自行+1
                    dp[i][j] = 1
                elif input_x[i - 1] == input_y[j - 1]:  # 不在边界上，相等就加一
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:  # 不相等
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        return dp[-1][-1]

    '''
    1. 邮箱查重 验证码生成并存入数据库 √
    '''
    def generate_email_code(self, email):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            test = self.getCol('user').find_one({'email': email})
            # 邮箱已被注册
            if test:
                res['reason'] = '邮箱已被注册'
            else:
                col_tempcode = self.getCol('tempcode')
                search_res2 = col_tempcode.find_one({'email': email})
                # 申请过注册
                if search_res2:
                    col_tempcode.delete_one(search_res2)
                # 生成时间戳和验证码并插入数据库
                newcode = {'email': email}
                t_time = round(time.time())
                t_code = ''
                for i in range(7):
                    rand1 = random.randint(0, 2)
                    if rand1 == 0:
                        rand2 = str(random.randint(0, 9))
                    elif rand1 == 1:
                        rand2 = chr(random.randint(65, 90))
                    else:
                        rand2 = chr(random.randint(97, 122))
                    t_code += rand2
                newcode['time'] = t_time
                newcode['code'] = t_code
                col_tempcode.insert_one(newcode)
                # 设置返回值res
                res['email_code'] = t_code
                res['state'] = 'success'
            return res
        except:
            return res

    '''
    2. 注册用户 √
    '''
    def create_user(self, password, email, username, email_code):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            has_user = self.getCol('user').find_one({'email': email})
            real_code = self.getCol('tempcode').find_one({'email': email})
            # 这里想记录时间差，但是得先保证 real_code 不为空，否则异常
            if real_code:
                time_dif = time.time() - real_code['time']
            # 排除邮箱已注册情况
            if has_user:
                res['reason'] = '邮箱已被注册'
            # 邮箱未注册,验证码表中该用户存在并且5min内并且匹配，插入并设置返回值success
            elif real_code and time_dif <= 300 and real_code['code'] == email_code:
                newuser = {'username': username,
                           'email': email,
                           'password': password,
                           'user_type': 'USER',
                           'star_list': [],
                           'follow_list': []
                           }
                self.getCol('user').insert_one(newuser)
                self.getCol('tempcode').delete_one(real_code)
                res['state'] = 'success'
            # 枚举异常情况
            elif real_code and time_dif > 300:
                res['reason'] = '验证码过期'
            elif real_code and real_code['code'] != email_code:
                res['reason'] = '验证码错误'
            else:
                res['reason'] = '没有记录该用户获取过验证码'
            return res
        except:
            return res

    '''
    3. 比对密码并返回用户信息 √
    '''
    def compare_password(self, password, email):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            find_user = self.getCol('user').find_one({'email': email})
            # 搜索到唯一用户
            if find_user:
                real_psw = find_user['password']
                if real_psw == password:
                    self.get_user_data(find_user, res)
                else:
                    res['reason'] = '密码错误'
            # 用户不存在
            else:
                res['reason'] = '用户不存在'
            return res
        except:
            return res

    '''
    4-1. 查询专家（不在意专家是否注册）（返回 专家scolarID 专家姓名 机构名称 被引次数 成果数 所属领域） √
    '''
    def search_professor(self, professor_name):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            # 不在意专家是否已注册
            experts = self.getCol('scmessage').find({'name': professor_name})
            test = self.getCol('scmessage').find_one({'name': professor_name})
            # 在专家总表中搜索到该姓名专家
            if test:
                experts_list = []
                # 根据所查同名专家列表experts，逐个专家提取其中基本信息到tmp中，并放入结果experts_list中
                for one_exp in experts:
                    tmp = {}
                    tmp['scid'] = one_exp['scid']
                    tmp['name'] = one_exp['name']
                    tmp['mechanism'] = one_exp['mechanism']
                    tmp['citedtimes'] = one_exp['citedtimes']
                    tmp['resultsnumber'] = one_exp['resultsnumber']
                    tmp['field'] = one_exp['field']
                    experts_list.append(tmp)
                res['msg'] = experts_list
                res['state'] = 'success'
            # 专家总表中没有记录该姓名专家信息
            else:
                res['reason'] = '未搜索到该专家'
            return res
        except:
            return res

    '''
    4-2 高级搜索，匹配专家名和机构名
    '''
    def search_professor_nb(self, professor_name, organization_name):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！', 'msg': []}
        try:
            body ={
                    "query": {
                    "bool": {
                        "must" : [
                            {"match": {"name": professor_name}},
                            {"match": {"mechanism": organization_name}}
                        ]
                    }
                },
                "highlight": {
                    "pre_tags" : ['<span style="font-color: red">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "message": {
                            "fragment_size": 150,
                            "number_of_fragments": 0
                        },
                        "name": {},
                        "mechanism":{}
                    }
                }
            }
            body = json.dumps(body, ensure_ascii=False)
            print(body)
            temp_scholars = self.es.search(index='scholar_index', body=body)
            count = len(temp_scholars['hits']['hits'])
            print(count)
            scholars = []
            for temp in temp_scholars['hits']['hits']:
                source = temp['_source']
                highlight = temp['highlight']
                if 'name' in highlight.keys():
                    source['name'] = highlight['name']
                if 'mechanism' in highlight.keys():
                    source['mechanism'] = highlight['mechanism']

                tmp = {}
                tmp['scid'] = source['scid']
                tmp['name'] = source['name']
                tmp['mechanism'] = source['mechanism']
                tmp['citedtimes'] = source['citedtimes']
                tmp['resultsnumber'] = source['resultsnumber']
                tmp['field'] = source['field']

                print(json.dumps(tmp, ensure_ascii=False, indent=4))
                scholars.append(tmp)
            if count > 0:
                res['msg'] = scholars
                res['state'] = 'success'
                res['reason'] = '成功查询'
            else:
                res['reason'] = '未找到相关论文'
            print(res)
            return res
        except:
            res['reason'] = '未搜索到该专家'
            return res

    '''
    5. 获取专家信息 √
    '''
    def get_professor_details(self, professor_id):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            find_exp = self.getCol('scmessage').find_one({'scid': professor_id})
            # 专家总表中查询到该专家
            if find_exp:
                # 去除部分没用的字段
                find_exp.pop('_id')
                find_exp.pop('scurl')
                # 对于copinfo（合作专家）字段，从其中的url字段提取scolarID，并将其修改为scid字段
                tmp = find_exp['copinfo']
                res['reason'] = '专家ID提取失败'
                for one_cop in tmp:
                    t_scholarID = self.scurl2id(one_cop['url'])
                    # scid提取失败，手动抛出异常
                    if t_scholarID == '':
                        gg = 1 / 0
                    one_cop.pop('url')
                    one_cop['scid'] = t_scholarID
                # 由于有部分专家paper字段中会出现_id，这里判断删除掉该字段
                tmp2 = find_exp['paper']
                res['reason'] = '_id修改失败'
                for one_paper in tmp2:
                    if '_id' in one_paper.keys():
                        one_paper.pop('_id')
                # 设置返回值
                res['state'] = 'success'
                res['msg'] = find_exp
            # 该专家不存在
            else:
                res['reason'] = '该专家不存在'
            return res
        except:
            return res

    '''
    6. 获取用户信息 √
    '''
    def get_user_details(self, email):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            find_user = self.getCol('user').find_one({'email': email})
            # 搜索到指定用户
            if find_user:
                self.get_user_data(find_user, res)
            # 用户不存在
            else:
                res['reason'] = '用户不存在'
            return res
        except:
            return res

    '''
    7. 获取机构信息 √
    '''
    def get_organization_details(self, organization_name):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            find_org = self.getCol('mechanism').find_one({'mechanism': organization_name})
            # 成功搜索到该机构
            if find_org:
                find_org.pop('_id')
                # 之后在这里可能进行对简介部分字符串（长度、格式）的处理
                res['state'] = 'success'
                res['msg'] = find_org
            # 未搜索到该机构
            else:
                res['reason'] = '未搜索到该机构'
            return res
        except:
            return res

    '''
    8-1. 查询论文 √
    '''
    def search_paper(self, title, page_num):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            # 根据标题模糊查询
            temp_papers = self.getCol('sci_source').find({'name': {'$regex': title}})
            papers = temp_papers.skip((page_num - 1) * Config.PAPER_NUM).limit(Config.PAPER_NUM)
            test = self.getCol('sci_source').find_one({'name': {'$regex': title}})
            # 根据标题模糊匹配查找到相关论文列表
            if test:
                papers_list = []
                # 根据所查到的论文列表papers，逐个论文提取其中基本信息（去除不必要字段），并放入结果papers_list中
                for one_paper in papers:
                    one_paper.pop('_id')
                    one_paper.pop('source_url')
                    one_paper.pop('free_download_url')
                    # 之后在这里可能需要对过长的摘要做一些内容上的删减
                    papers_list.append(one_paper)
                res['msg'] = papers_list
                res['count'] = temp_papers.count()
                res['state'] = 'success'
            # 根据标题模糊匹配未查找到相关论文
            else:
                res['reason'] = '未查找到相关论文'
            return res
        except:
            return res

    '''
    8-2. 获取论文全部信息 √
    '''
    def get_paper_details(self, paper_id):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            find_paper = self.getCol('sci_source').find_one({'paperid': paper_id})
            # 成功搜索到该论文
            if find_paper:
                find_paper.pop('_id')
                # 之后在这里可能对论文的数据内容做处理，暂时返回全部内容
                res['state'] = 'success'
                res['msg'] = find_paper
            # 未搜索到该论文
            else:
                res['reason'] = '未搜索到该论文'
            print(res)
            return res
        except:
            return res

    '''
    8-3. 论文高级检索
    '''
    def search_paper_nb(self, title, page_num, keyw_and, keyw_or, keyw_not, author, journal, start_time, end_time ):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！', 'count': 0, 'msg': []}
        try:
            # 根据条件进行高级查询
            must_match = ''
            for key in keyw_and:
                must_match += key+' '
            must_not_match = ''
            for key in keyw_not:
                must_not_match += key+' '
            should_match = ''
            for key in keyw_or:
                should_match += key+' '
            try:
                start_time = int(start_time)
            except:
                start_time = 0
            try:
                end_time = int(end_time)
            except:
                end_time = 2020
            filter_query = {
                "range": {
                    "year": {
                        "gte": start_time,
                        "lte": end_time
                    }
                }
            }
            must_query = [
                {
                    "match": {
                        "name": title
                    }
                },
            ]
            if author != '':
                must_query.append(
                    {"match": {"author": author}}
                )
            if journal != '':
                must_query.append(
                    {"match": {"source_journal.name": journal}}
                )
            must_not_query = {
                "multi_match":{
                    "query": must_not_match,
                    "fields": [
                        "abstract",
                        "name",
                        "author",
                        "keyword"
                    ],
                    "operator": "and"
                }
            }
            should_query = [
                {
                    "multi_match":{
                        "query": should_match,
                        "fields": [
                            "abstract",
                            "name",
                            "author",
                            "keyword"
                        ]
                    }
                },
                {
                    "match": {
                        "name":{
                            "query": must_match,
                            "operator": "and"
                        }
                    }
                },
                {
                    "match": {
                        "author": {
                            "query": must_match,
                            "operator": "and"
                        }
                    }
                },
                {
                    "match": {
                        "abstract":{
                            "query": must_match,
                            "operator": "and"
                        }
                    }
                },
                {
                    "match": {
                        "keyword": {
                            "query": must_match,
                            "operator": "and"
                        }
                    }
                }
            ]
            body = {
                "query": {
                    "bool":{
                       "filter": filter_query,
                        "must": must_query,
                        "must_not": must_not_query,
                        "should": should_query
                    }
                },
                "highlight": {
                    "pre_tags" : ['<span style="font-color: red">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "message": {
                            "fragment_size": 150,
                            "number_of_fragments": 0
                        },
                        "abstract": {},
                        "name":{},
                        "keyword":{},
                        "author":{},
                        "source_journal.name":{},
                        "year":{}
                    }
                }
            }
            body = json.dumps(body, ensure_ascii=False)
            print(body)
            temp_papers = self.es.search(index='paper_index',body=body)
            count = len(temp_papers['hits']['hits'])
            print(count)
            papers = []
            for temp in temp_papers['hits']['hits']:
                source = temp['_source']
                highlight = temp['highlight']
                if 'source_journal.name' in highlight.keys():
                    source['source_journal']['name'] = highlight['source_journal.name'][0]
                if 'year' in highlight.keys():
                    source['year'] = highlight['year']
                if 'author' in highlight.keys():
                    for i in range(len(source['author'])):
                        for h_author in highlight['author']:
                            if len(source['author'][i]) == self.LCS(source['author'][i], h_author):
                                source['author'][i] = h_author
                if 'name' in highlight.keys():
                    source['name'] = highlight['name']
                if 'abstract' in highlight.keys():
                    abstract = ''
                    for item in highlight['abstract']:
                        abstract += item
                    source['abstract'] = abstract
                if 'keyword' in highlight.keys():
                    for i in range(len(source['keyword'])):
                        for kw in highlight['keyword']:
                            if len(source['keyword'][i]) == self.LCS(source['keyword'][i],kw):
                                source['keyword'][i] = kw
                print(json.dumps(source,ensure_ascii=False,indent=4))
                papers.append(source)
            if count>0:
                res['count'] = count
                res['msg'] = papers[(page_num-1)*10 : page_num*10]
                res['state'] = 'success'
                res['reason'] = '成功查询'
            else:
                res['reason'] = '未找到相关论文'
            print(res)
            return res
        except:
            return res

    '''
    9. 查询机构 √
    '''
    def search_organization(self, org_name, page_num):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            # 根据名称模糊查询
            temp_orgs = self.getCol('mechanism').find({'mechanism': {'$regex': org_name}})
            orgs = temp_orgs.skip((page_num - 1) * Config.ORG_NUM).limit(Config.ORG_NUM)
            test = self.getCol('mechanism').find_one({'mechanism': {'$regex': org_name}})
            # 根据名称模糊匹配查找到相关机构列表
            if test:
                org_list = []
                # 根据所查到的机构列表orgs，逐个机构提取其中基本信息（去除不必要字段），并放入结果org_list中
                for one_org in orgs:
                    one_org.pop('_id')
                    # 之后在这里可能需要对简介部分做一些内容上的删减
                    org_list.append(one_org)
                res['msg'] = org_list
                res['count'] = temp_orgs.count()
                res['state'] = 'success'
            # 根据名称模糊匹配未查找到相关机构
            else:
                res['reason'] = '未查找到相关机构'
            return res
        except:
            return res

#######################################################接口 10-18#######################################################
    '''
    10
    收藏/取消收藏资源，根据paper_id是否在收藏列表中来判断是收藏还是取消收藏
    测试成功！
    '''
    def collect(self, email, paper_id):
        res = {'state': 'success', 'reason': '用户已收藏该资源'}
        try:
            user = self.getCol('user').find_one({'email': email})
            star_list = user['star_list']
            if paper_id not in user['star_list']:
                res = {'state': 'success', 'reason': '用户尚未收藏该资源'}
                star_list.append(paper_id)
            else:
                star_list.remove(paper_id)
            user['star_list'] = star_list
            self.getCol('user').update_one({'email': user['email']}, {'$set': user})
        except:
            res = {'state': 'fail', 'reason': '更新数据库失败'}
        finally:
            return res

    '''
    11
    判断用户是否收藏该作品
    测试成功！
    '''
    def is_collect(self, email, paper_id):
        res = {'state': 'yes', 'reason': '用户已收藏该资源'}
        user = self.getCol('user').find_one({'email': email})
        if paper_id not in user['star_list']:
            res = {'state': 'no', 'reason': '用户尚未收藏该资源'}
        return res

    '''
    12
    关注/取消关注学者
    测试成功！
    '''
    def follow(self, email, professor_id):
        res = {'state': 'success', 'reason': '用户已关注该学者'}
        try:
            user = self.getCol('user').find_one({'email': email})
            follow_list = user['follow_list']
            if professor_id in user['follow_list']:
                follow_list.remove(professor_id)
            else:
                follow_list.append(professor_id)
                res = {'state': 'success', 'reason': '用户未关注该学者'}
            user['follow_list'] = follow_list
            self.getCol('user').update_one({'email': user['email']}, {'$set': user})
        except:
            res = {'state': 'fail', 'reason': '更新数据库失败'}
        finally:
            return res

    '''
    13
    判断用户是否关注专家
    测试成功！
    '''
    def is_follow(self, email, professor_id):
        user = self.getCol('user').find_one({'email': email})
        res = {'state': 'yes', 'reason': '用户已关注该专家'}
        if professor_id not in user['follow_list']:
            res = {'state': 'no', 'reason': '用户未关注该专家'}
        return res

    '''
    14 
    修改个人资料，专家不可改名
    测试成功，但是不知是否要判断修改后的用户名或头像与之前一样
    '''
    def change_info(self, email, username, avatar):
        user = self.getCol('user').find_one({'email': email})
        res = {'state': 'success', 'reason': '修改用户名成功'}
        try:
            if username != '':
                if user['user_type'] != 'EXPERT':
                    self.getCol('user').update_one({'email': email}, {'$set': {'username': username}})
                else:
                    res = {'state': 'fail', 'reason': '专家不可改名'}
            elif avatar != '':
                self.getCol('user').update_one({'email': email}, {'$set': {'avatar': avatar}})
                res['reason'] = '修改头像成功'
            else:
                res = {'state': 'fail', 'reason': '输入的用户名或上传的头像为空'}
        except:
            res = {'state': 'fail', 'reason': '数据库更新失败'}
        finally:
            return res

    '''
    15
    修改密码
    测试成功
    '''
    def change_pwd(self, email, old_password, new_password):
        user = self.getCol('user').find_one({'email': email})
        res = {'state': 'success', 'reason': '修改密码成功'}
        try:
            if user['password'] != old_password:
                res = {'state': 'fail', 'reason': '原来的密码输入错误'}
            else:
                self.getCol('user').update_one({'email': user['email']}, {'$set': {'password': new_password}})
        except:
            res = {'state': 'fail', 'reason': '数据库更新失败'}
        finally:
            return res

    '''
    16
    增加科技资源
    '''
    def add_resource(self, professor_id, paper_url):
        res = {'state': 'success', 'reason': '请求增加资源成功'}
        scholar = self.getCol('scmessage').find_one({'scid': professor_id})
        try:
            resource_application = self.client.Business.resource_application
            resource_application.insert_one({{"professor_id": professor_id, "paper_url": paper_url,
                                              "email": scholar['email'], "name": scholar['name'],
                                              "state": "waiting", "type": "ADD"}})
            res["name"] = scholar['name']
        except:
            res = {'state': 'fail', 'reason': '请求增加科技资源失败'}
        finally:
            return res

    '''
    删除科技资源
    17
    '''
    def rm_resource(self, professor_id, paper_id):
        res = {'state': 'success', 'reason': '请求删除科技资源成功'}
        scholar = self.getCol('scmessage').find_one({'scid': professor_id})
        paper = self.getCol('sci_source').find_one({'paperid': paper_id})
        try:
            resource_application = self.client.Business.resource_application
            resource_application.insert_one({{"professor_id": professor_id, "paper_id": paper_id,
                                              "email": scholar['email'], "name": scholar['name'],
                                              "state": "waiting", "type": "DELETE"}})
            res["name"] = scholar['name']
            res["paper_name"] = paper['name']
        except :
            res = {'state': 'fail', 'reason': '请求删除科技资源失败'}
        finally:
            return res

    '''
    18
    管理员处理修改科技资源申请，现在手动处理增加资源请求，审查论文url，手动添加数据库内容，管理员请通过后再确认同意增加
    '''
    def deal_request(self, apply_id, deal):
        state = {'state': 'success', "reason": "", "name": "", "email": ""}
        resource_application = self.client.Business.resource_application
        apply = resource_application.find_one({"_id": ObjectId(apply_id)})
        if apply is None:
            state["state"] = "fail"
            state["reason"] = "apply not found"
        elif apply["state"] is not "waiting":
            state["state"] = "fail"
            state["reason"] = "apply is already dealt with"
        else:
            if deal:
                apply["state"] = "accepted"
                result = self.client.Business.user.update_many({"email": apply["email"], "user_type": "USER"},
                                                               {"user_type": "EXPERT"})
                if result.matched_count == 0:
                    state["state"] = "fail"
                    state["reason"] = "but nothing changed"
                state["name"] = apply["name"]
                state["email"] = apply["email"]
                state["type"] = apply["type"]
            else:
                apply["state"] = "refused"
        return state

#######################################################接口 19-26#######################################################
    '''
    The 19th Method √
    评论资源
    '''
    def comment(self, email, paper_id, content):
        state = {'state': 'success', "reason": ""}
        comment_list = self.client.Business.comment
        papers = self.client.Business.sci_source
        query_paper_id = {"paperid": paper_id}
        user_collection = self.client.Business.user
        if papers.find_one(query_paper_id) is None:
            state["state"] = "fail"
            state["reason"] = "paper not found"
        elif user_collection.find_one({"email": email}) is None:
            state["state"] = "fail"
            state["reason"] = "user not found"
        else:
            this_comment = {"email": email, "paper_id": paper_id,
                            "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                            "content": content, "replies": []}
            comment_list.insert_one(this_comment)
        return state

    '''
    The 20th Method
    回复评论
    '''
    def reply_comment(self, from_email, comment_id, to_name, content, from_name):
        state = {'state': 'success', "reason": ""}
        comment_list = self.client.Business.comment
        new_comment = comment_list.find_one({"_id": ObjectId(comment_id)})
        if new_comment is None:
            state["state"] = "fail"
            state["reason"] = "comment not found"
        else:
            new_comment["replies"].append({"from_email": from_email, "to_name": to_name,
                                           "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                                           "content": content, "from_name": from_name})
            comment_list.update({"_id": ObjectId(comment_id)}, new_comment)
        return state

    '''
    The 21st Method √
    删除评论
    '''
    def delete_comment(self, comment_id):
        state = {'state': 'success', "reason": ""}
        comment_list = self.client.Business.comment
        if comment_list.find_one({"_id": ObjectId(comment_id)}) is None:
            state["state"] = "fail"
            state["reason"] = "comment not found"
        else:
            comment_list.remove({"_id": ObjectId(comment_id)})
        return state

    '''
    The 22nd Method
    发送系统通知（除管理员）
    '''
    def send_sys_message_to_all(self, msg_type, content):
        state = {'state': 'success', "reason": ""}
        msg = self.client.Business.message
        user_list = self.client.Business.user.find({"user_type": {"$ne": "ADMIN"}})
        if user_list.count() == 0:
            state["state"] = "fail"
            state["reason"] = "获取非管理员用户信息失败"
        else:
            for user in user_list:
                msg.insert_one({"content": content, "email": user["email"],
                                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                                "type": msg_type, "status": "No"})
        return state

    '''
    The 23th Method
    获取通知
    '''
    def get_sys_message(self, email):
        state = {'state': 'success', "reason": "", "messages": []}
        message = self.client.Business.message
        msg_list = message.find({"email": email})
        if msg_list.count() > 0:
            for msg in msg_list:
                if 'apply_id' in msg.keys() and 'apply_id' != "":
                    state["messages"].append({"content": msg["content"], "date": msg["date"],
                                              "type": msg["type"], "msg_id": str(msg["_id"]),
                                              "status": msg["status"], "apply_id": msg["apply_id"]})
                else:
                    state["messages"].append({"content": msg["content"], "date": msg["date"],
                                              "type": msg["type"], "status": msg["status"], "msg_id": str(msg["_id"])})
        else:
            state["state"] = "fail"
            state["reason"] = "消息列表为空"
        return state

    '''
    The 24th Method
    申请认证（实际是插入申请认证表）
    '''
    def certification(self, email, name, id_, field, text, scid):
        state = {'state': 'success', "reason": "", "_id": ""}
        applies = self.client.Business.application
        expert_list = self.client.Business.user.find({"user_type": "EXPERT", "email": email})
        if expert_list.count() > 0:
            state["state"] = "fail"
            state["reason"] = "该邮箱已被其他专家认证"
        else:
            app_list = applies.find({"email": email})
            if app_list.count() > 0:
                state["state"] = "fail"
                state["reason"] = "您已提交申请，请勿重复提交"
            else:
                result = applies.insert_one({"name": name, "ID": id_, "field": field, "email": email, "text": text,
                                             "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                                             "scid": scid, "state": "waiting"})
                state["_id"] = str(result.inserted_id)
        return state

    '''
    The 25th Method
    同名专家
    '''
    def common_name(self, professor_name):
        state = {'state': 'success', "reason": "", "user_ids": []}
        expert_list = self.client.Business.user.find({"user_type": "EXPERT", "username": professor_name})
        if expert_list.count() == 0:
            state["state"] = "fail"
            state["reason"] = "获取专家列表失败"
        else:
            for expert in expert_list:
                state["user_ids"].append(expert["email"])
        return state

    '''
    The 26th Method
    管理员处理认证 deal为bool变量
    '''
    def deal_certification(self, apply_id, deal):
        state = {'state': 'success', "reason": "", "name": "", "email": ""}
        applies = self.client.Business.application
        apply = applies.find_one({"_id": ObjectId(apply_id)})
        if apply is None:
            state["state"] = "fail"
            state["reason"] = "apply not found"
        elif apply["state"] != "waiting":
            state["state"] = "fail"
            state["reason"] = "apply is already dealt with"
        else:
            if deal:
                applies.update_one({"_id": ObjectId(apply_id)},
                                   {"$set": {"state": "accepted"}})
                result = self.client.Business.user.update_one({"email": apply["email"], "user_type": "USER"},
                                                              {"$set": {"user_type": "EXPERT",
                                                                        "username": apply["name"],
                                                                        "scid": apply["scid"]}})
                if result.matched_count == 0:
                    state["state"] = "fail"
                    state["reason"] = "but nothing changed"
                else:
                    state["name"] = apply["name"]
                    state["email"] = apply["email"]
            else:
                applies.update_one({"_id": ObjectId(apply_id)},
                                   {"$set": {"state": "refused"}})
        return state

    '''
    The 27th Method
    发送系统通知（仅管理员）
    '''
    def send_sys_message_to_admin(self, msg_type, content, apply_id=""):
        state = {'state': 'success', "reason": ""}
        msg = self.client.Business.message
        user_list = self.client.Business.user.find({"user_type": "ADMIN"})
        if user_list.count() == 0:
            state["state"] = "fail"
            state["reason"] = "获取管理员信息失败"
        else:
            for user in user_list:
                msg.insert_one({"content": content, "email": user["email"],
                                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                                "type": msg_type, "status": "No", "apply_id": apply_id})
        return state

    '''
    The 28th Method
    发送系统通知（单人）
    '''
    def send_sys_message_to_one(self, msg_type, content, email):
        state = {'state': 'success', "reason": ""}
        msg = self.client.Business.message
        user_list = self.client.Business.user.find({"email": email})
        if user_list.count() == 0:
            state["state"] = "fail"
            state["reason"] = "未获取到用户信息"
        else:
            for user in user_list:
                msg.insert_one({"content": content, "email": user["email"],
                                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                                "type": msg_type, "status": "No"})
        return state

    '''
    The 29th Method
    获取评论详情
    '''
    def get_comment(self, paper_id):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            find_com = self.getCol('comment').find({'paper_id': paper_id})
            test = self.getCol('comment').find_one({'paper_id': paper_id})
            # 成功搜索到相关评论
            if test:
                comment_list = []
                # 对每个评论，去掉不必要字段，把email替换为用户名
                for one_com in find_com:
                    one_com.pop('paper_id')
                    # 将评论者信息（id 用户名）封装到一个字典里
                    from_user_info = {}
                    find_user = self.getCol('user').find_one({'email': one_com['email']})
                    one_com.pop('email')
                    from_user_info['userid'] = find_user['email']
                    from_user_info['username'] = find_user['username']
                    one_com['from'] = from_user_info
                    # 处理ObjectID作为comment_id返回
                    cmt_id = str(one_com['_id'])
                    one_com.pop('_id')
                    one_com['comment_id'] = cmt_id
                    # 这里可能需要对回复列表进行内容的修改
                    comment_list.append(one_com)
                res['state'] = 'success'
                res['msg'] = comment_list
            # 未搜索到评论
            else:
                res['reason'] = '未搜索到相关评论'
            return res
        except:
            return res

    '''
    30-1. 删除一条消息 √
    '''
    def delete_message_onepiece(self, user_id, message_id):
        state = {'state': 'success', "reason": ""}
        msg_list = self.client.Business.message
        if msg_list.find_one({"_id": ObjectId(message_id)}) is None:
            state["state"] = "fail"
            state["reason"] = "message not found"
        else:
            msg_list.remove({"_id": ObjectId(message_id)})
        return state

    '''
    30-2. 删除同种消息 √
    '''
    def delete_message_onetype(self, user_id, message_type):
        state = {'state': 'success', "reason": ""}
        msg_list = self.client.Business.message
        if msg_list.find_one({"email": user_id, "type": message_type}) is None:
            state["state"] = "fail"
            state["reason"] = "message not found"
        else:
            msg_list.remove({"email": user_id, "type": message_type})
        return state

    '''
    31. 获取认证信息 √
    '''
    def get_apply(self, apply_id):
        res = {'state': 'fail', 'reason': '网络出错或BUG出现！'}
        try:
            find_mat = self.getCol('application').find_one({'_id': ObjectId(apply_id)})
            # 成功搜索到认证材料
            if find_mat:
                find_mat.pop('_id')
                res['state'] = 'success'
                res['msg'] = find_mat
            # 未搜索到认证材料
            else:
                res['reason'] = '未搜索到认证材料'
            return res
        except:
            return res