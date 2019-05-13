

import time
from pymongo import MongoClient
from flask import Flask, request, jsonify, Response
from flask_restful import Api, Resource, reqparse
from werkzeug.datastructures import Headers
from conf.config import MongoDBConfig

app = Flask(__name__)



class EmailVerify(Resource): #邮箱绑定请求验证码
    def get(self):
        return {"state": "fail"}
    def post(self):
        ##如果邮箱没被占用：
        email = 解析表单得到参数()
        try:
            if(该邮箱未被使用(email)['state'] == 'success'): ##此时生成邮箱验证码+时间戳
                code = 该邮箱未被使用(email)['email_code']
                text = "balabla" + code
                发送邮件(email,text)
                return {"state": "success"}
        except:
            return {'state':'fail'}
        else:
        ##被占用则返回fail
        return {'state': 'fail'}

class Register(Resource):  # 注册请求

    def get(self):
        return {"state": "fail"}

    def post(self):
        password = 解析表单得到参数()
        password = 转换为密文(password)
        email = 解析表单得到参数()
        username = 解析表单得到参数()
        avatar = 解析表单得到参数()
        email_code = 解析表单得到参数()
        try:
            if(在数据库注册用户(password....email_code) == 'fail'):
                return 'fail'
        except:
            return  'fail'
        else:
            return 'success'

class Login(Resource):  # 登录请求

    def get(self):
        return {"state": "fail"}

    def post(self):
        password = 解析表单得到参数()
        password = 转换为密文(password)
        email = 解析表单得到参数()
        try:
            return 比对密码(password,email)
        except:
            return 'fail'

class Login(Resource):  # 登录请求

    def get(self):
        return {"state": "fail"}

    def post(self):
        password = 解析表单得到参数()
        password = 转换为密文(password)
        email = 解析表单得到参数()
        try:
            return 比对密码(password, email)
        except:
            return 'fail'

class Search(Resource):  # 登录请求

    def get(self,professor_name = None, title = None, orgname = None):
        try:
            if(professor_name): ##通过专家名检索
                return 通过专家名查询(professor_name)
            elif(title): ##通过文章名检索
                return 通过文章名查询(title)
            elif(orgname): ##通过机构名检索
                return 通过机构名查询(orgname)
            else:##非法搜索
                return {"state": "fail"}
        except:
            return {"state": "fail"}

class GetDetail(Resource):  # 登录请求

    def get(self, professor_id=None, organization_id=None, user_id=None):
        try:
            if (professor_id):  ##获取专家信息
                return 获取专家信息(professor_id)
            elif (organization_id):  ##获取组织信息
                return 获取组织信息(organization_id)
            elif (user_id):  ##获取普通用户信息
                return 获取普通用户信息(user_id)
            else:  ##非法搜索
                return {"state": "fail"}
        except:
            return {"state": "fail"}





# 添加api资源
api = Api(app)
api.add_resource(Search, "/api/v1")
api.add_resource(EmailVerify, "/api/v1/email_code", endpoint="email_code")
api.add_resource(Register,    "/api/v1/register", endpoint="register")
api.add_resource(Login,       "/api/v1/login", endpoint="login")
api.add_resource(Search,    "/api/v1/search_professor/<string:professor_name>", endpoint="search_professor")
api.add_resource(Search,    "/api/v1/search_paper/<string:title>", endpoint="search_paper")
api.add_resource(Search,    "/api/v1/search_organization/<string:orgname>", endpoint="search_organization")
api.add_resource(GetDetail, "/api/v1/professor_detail/<string:professor_id>", endpoint="professor_detail")
api.add_resource(GetDetail, "/api/v1/user_detail/<string:user_id>", endpoint="user_detail")
api.add_resource(GetDetail, "/api/v1/organization_detail/<string:organization_id>", endpoint="organization_detail")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    #app.response_class = AResponse