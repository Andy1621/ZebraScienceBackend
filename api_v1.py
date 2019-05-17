from flask import Flask, request, jsonify, Response
from flask_restful import Api, Resource

app = Flask(__name__)


class EmailVerify(Resource):  # 邮箱绑定请求验证码
    def get(self):
        return {"state": "fail"}

    def post(self):
        try:
            data = request.get_json()
            email = data['email']
            res = generate_email_code(email)  # 此时生成邮箱验证码+时间戳
            if res["state"] == "success":
                code = res["email_code"]
                send_email(email, code)
                return {"state": "success"}
            else:
                # 被占用则返回fail
                return {"state": "fail"}
        except:
            return {"state": "fail"}


class Register(Resource):  # 注册请求
    def get(self):
        return {"state": "fail"}

    def post(self):
        data = request.get_json()
        password = data['password']
        password = encode(password)
        email = data['email']
        username = data['username']
        avatar = data['avatar']
        email_code = data['email_code']
        return create_user(password, email, username, avatar, email_code)


class Login(Resource):  # 登录请求
    def get(self):
        return {"state": "fail"}

    def post(self):
        data = request.get_json()
        password = data['password']
        password = encode(password)
        email = data['email']
        try:
            return compare_password(password, email)
        except:
            return {"state": "fail"}


class Search(Resource):  # 登录请求
    def get(self, professor_name=None, title=None, organization_name=None):
        try:
            if professor_name:  # 通过专家名检索
                return search_professor(professor_name)
            elif title:  # 通过文章名检索
                return search_paper(title)
            elif organization_name:  # 通过机构名检索
                return search_organization(organization_name)
            else: # 非法搜索
                return {"state": "fail"}
        except:
            return {"state": "fail"}


class GetDetail(Resource):  # 登录请求
    def get(self, professor_id=None, organization_id=None, user_id=None):
        try:
            if professor_id:  # 获取专家信息
                return get_professor_details(professor_id)
            elif organization_id:  # 获取组织信息
                return get_organization_details(organization_id)
            elif user_id:  # 获取普通用户信息
                return get_user_details(user_id)
            else:  # 非法搜索
                return {"state": "fail"}
        except:
            return {"state": "fail"}


class Collection(Resource):  # 收藏取消资源
    def get(self):  #
        try:
            data = request.get_json()
            user_id = data['user_id']
            paper_id = data['paper_id']
            return collect(user_id,paper_id)
        except:
            return {"state":"fail"}
    def delete(self):
        try:
            data = request.get_json()
            user_id = data['user_id']
            paper_id = data['paper_id']
            return delete_collect(user_id,paper_id)
        except:
            return {"state":"fail"}
    def post(self):
        try:
            data = request.get_json()
            user_id = data['user_id']
            paper_id = data['paper_id']
            return is_collect(user_id,paper_id)
        except:
            return {"state":"fail"}



# 添加api资源
api = Api(app)
api.add_resource(EmailVerify, "/api/v1/email_code", endpoint="email_code")
api.add_resource(Register, "/api/v1/register", endpoint="register")
api.add_resource(Login, "/api/v1/login", endpoint="login")
api.add_resource(Search, "/api/v1/search_professor/<string:professor_name>", endpoint="search_professor")
api.add_resource(Search, "/api/v1/search_paper/<string:title>", endpoint="search_paper")
api.add_resource(Search, "/api/v1/search_organization/<string:organization_name>", endpoint="search_organization")
api.add_resource(GetDetail, "/api/v1/professor_detail/<string:professor_id>", endpoint="professor_detail")
api.add_resource(GetDetail, "/api/v1/user_detail/<string:user_id>", endpoint="user_detail")
api.add_resource(GetDetail, "/api/v1/organization_detail/<string:organization_id>", endpoint="organization_detail")
api.add_resource(Collection,"/api/v1/collect",endpoint = "collect")
api.add_resource(Collection,"/api/v1/is_collect",endpoint = "is_collect")



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    # app.response_class = AResponse
