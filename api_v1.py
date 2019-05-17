from flask import Flask, request, jsonify, Response
from flask_restful import Api, Resource
from utils import send_mail,encode
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


class Collection(Resource):  # 论文资源
    def get(self):  # 收藏资源
        try:
            data = request.get_json()
            user_id = data['user_id']
            paper_id = data['paper_id']
            return collect(user_id,paper_id)
        except:
            return {"state":"fail"}

    def delete(self):  # 删除收藏
        try:
            data = request.get_json()
            user_id = data['user_id']
            paper_id = data['paper_id']
            return delete_collect(user_id,paper_id)
        except:
            return {"state":"fail"}

    def post(self):  # 是否收藏
        try:
            data = request.get_json()
            user_id = data['user_id']
            paper_id = data['paper_id']
            return is_collect(user_id,paper_id)
        except:
            return {"state":"fail"}


class Follow(Resource):  # 关注
    def get(self):  # 关注
        try:
            data = request.get_json()
            user_id = data['user_id']
            professor_id = data['paper_id']
            return follow(user_id,professor_id)
        except:
            return {"state":"fail"}

    def delete(self):  # 取消关注
        try:
            data = request.get_json()
            user_id = data['user_id']
            professor_id = data['paper_id']
            return un_follow(user_id,professor_id)
        except:
            return {"state":"fail"}

    def post(self):  # 是否关注
        try:
            data = request.get_json()
            user_id = data['user_id']
            professor_id = data['paper_id']
            return is_follow(user_id,professor_id)
        except:
            return {"state":"fail"}


class Change_info(Resource):  # 修改用户名
    def post(self):
        try:
            data = request.get_json()
            user_id = data['user_id']
            username = data['username']
            return change_info(user_id,username)
        except:
            return {"state":"fail"}


class Change_pswd(Resource):  # 修改密码
    def post(self):
        try:
            data = request.get_json()
            user_id = data['user_id']
            old_password = data['old_password']
            new_password = data['new_password']
            return change_pswd(user_id,old_password,new_password)
        except:
            return {"state":"fail"}


class Change_resource(Resource)  # 增加删除资源
    def post(self):
        try:
            data = request.get_json()
            professor_id = data['professor_id']
            paper_url = data['paper_id']
            return add_resource(professor_id,paper_url)
        except:
            return {"state":"fail"}

    def delete(self):
        try:
            data = request.get_json()
            professor_id = data['professor_id']
            paper_id = data['paper_id']
            return rm_resource(professor_id,paper_id)
        except:
            return {"state":"fail"}


class Deal_request(Resource):  # 管理员处理申请
    def post(self):
        try:
            data = request.get_json()
            apply_id = data['apply_id']
            deal = data['deal']
            return deal_request(apply_id,deal)
        except:
            return {"state":"fail"}


class Comment(Resource):  # 评论资源
    def get(self):
        try:
            data = request.get_json()
            id = data['id']
            paperid = data['replyid']
            content = data['content']
            return comment(id,paperid,content)
        except:
            return {"state": "fail"}


class Reply_Comment(Resource):  # 回复评论
    def get(self):
        try:
            data = request.get_json()
            id = data['id']
            replyid = data['replyid']
            content = data['content']
            return replycomment(id,replyid,content)
        except:
            return {"state": "fail"}


class Delete_Comment(Resource):  # 删除评论
    def get(self):
        try:
            data = request.get_json()
            comment_id = data['comment_id']
            return deletecomment(comment_id)
        except:
            return {"state": "fail"}


class Send_Sysmessage(Resource):  # 发送通知
    def get(self):
        try:
            data = request.get_json()
            content = data['content']
            return sendsysmessage(content)
        except:
            return {"state": "fail"}


class Get_Sysmessage(Resource):  # 获取通知
    def get(self):
        try:
            data = request.get_json()
            id = data['id']
            return getsysmessage(id)
        except:
            return {"state": "fail"}


class Certification(Resource):  # 申请认证
    def get(self):
        try:
            data = request.get_json()
            id = data['id']
            name = data['name']
            ID_num = data['ID_num']
            text = data['text']
            field = data['field']
            return certification(id,name,ID_num,field,text)
        except:
            return {"state":"fail"}


class Common_Name(Resource):  # 同名专家申请认证
    def get(self):
        try:
            data = request.get_json()
            professor_name = data['professor_name']
            return commonname(professor_name)
        except:
            return {"state":"fail"}


class Deal_Certification(Resource):  # 管理员处理认证
    def get(self):
        try:
            data = request.get_json()
            state = data['state']
            return dealcertification(state)
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
api.add_resource(Follow,"/api/v1/follow",endpoint = "follow")
api.add_resource(Follow,"/api/v1/is_follow",endpoint = "is_follow")
api.add_resource(Change_info,"/api/v1/information_change",endpoint = "info_change")
api.add_resource(Change_pswd,"/api/v1/password_change",endpoint = "change_pswd")
api.add_resource(Change_resource,"/api/v1/source_add",endpoint = "source_add")
api.add_resource(Change_resource,"/api/v1/source_delete",endpoint = "source_delete")
api.add_resource(Deal_request,"/api/v1/deal_change_request",endpoint = "deal_request")
api.add_resource(Comment,"/api/v1/comment",endpoint = "comment")
api.add_resource(Reply_Comment,"/api/v1/reply_comment",endpoint = "reply_comment")
api.add_resource(Delete_Comment,"/api/v1/delete_comment",endpoint = "delete_comment")
api.add_resource(Send_Sysmessage,"/api/v1/send_sysmessage",endpoint = "send_sysmessage")
api.add_resource(Get_Sysmessage,"/api/v1/get_sysmessage",endpoint = "get_sysmessage")
api.add_resource(Certification,"/api/v1/certification",endpoint = "certification")
api.add_resource(Common_Name,"/api/v1/common_name",endpoint = "common_name")
api.add_resource(Deal_Certification,"/api/v1/deal_certification",endpoint = "deal_certification")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    # app.response_class = AResponse
