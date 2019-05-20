from flask import Flask, request
from flask_restful import Api, Resource
from utils import send_email, encode
from DBClass import DbOperate
from flask_cors import *
from json import dumps

app = Flask(__name__)
CORS(app, resources=r'/*')
db = DbOperate()


class EmailVerify(Resource):  # 邮箱绑定请求验证码
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            t_res = db.generate_email_code(email)  # 此时生成邮箱验证码+时间戳x
            if t_res.get("state") == "success":
                code = t_res.get("email_code")
                send_email(email, code)
                res = {"state": "success"}
            else:
                # 被占用则返回fail
                res = t_res
            return dumps(res, ensure_ascii=False)
        except:
            res = {"state": "fail"}
            return dumps(res, ensure_ascii=False)

class Register(Resource):  # 注册请求
    def post(self):
        data = request.get_json()
        password = data.get('password')
        password = encode(password)
        email = data.get('email')
        username = data.get('username')
        email_code = data.get('email_code')
        res = db.create_user(password, email, username, email_code)
        return dumps(res, ensure_ascii=False)


class Login(Resource):  # 登录请求
    def post(self):
        data = request.get_json()
        password = data.get('password')
        password = encode(password)
        email = data.get('email')
        res = {"state": "fail"}
        try:
            res = db.compare_password(password, email)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class Search(Resource):  # 登录请求
    def get(self, professor_name=None, title=None, organization_name=None):
        res = {"state": "fail"}
        try:
            if professor_name:  # 通过专家名检索
                res = db.search_professor(professor_name)
            elif title:  # 通过文章名检索
                res = db.search_paper(title)
            elif organization_name:  # 通过机构名检索
                res = db.search_organization(organization_name)
            # 非法搜索
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class GetDetail(Resource):  # 登录请求
    def get(self, professor_id=None, organization_id=None, user_id=None):
        res = {"state": "fail"}
        try:
            if professor_id:  # 获取专家信息
                res = db.get_professor_details(professor_id)
            elif organization_id:  # 获取组织信息
                res = db.get_organization_details(organization_id)
            elif user_id:  # 获取普通用户信息
                res = db.get_user_details(user_id)
            # 非法搜索
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class Collection(Resource):  # 论文资源
    def get(self):  # 收藏资源
        res = {"state": "fail"}
        try:
            data = request.args
            user_id = data.get('user_id')
            paper_id = data.get('paper_id')
            res = db.collect(user_id, paper_id)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)

    def delete(self):  # 删除收藏
        res = {"state": "fail"}
        try:
            data = request.args
            user_id = data.get('user_id')
            paper_id = data.get('paper_id')
            res = db.collect(user_id, paper_id)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)

    def post(self):  # 是否收藏
        res = {"state": "fail"}
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            paper_id = data.get('paper_id')
            res = db.is_collect(user_id, paper_id)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class Follow(Resource):  # 关注
    def get(self):  # 关注
        res = {"state": "fail"}
        try:
            data = request.args
            user_id = data.get('user_id')
            professor_id = data.get('professor_id')
            res = db.follow(user_id, professor_id)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)

    def delete(self):  # 取消关注
        res = {"state": "fail"}
        try:
            data = request.args
            user_id = data.get('user_id')
            professor_id = data.get('professor_id')
            res = db.follow(user_id, professor_id)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)

    def post(self):  # 是否关注
        res = {"state": "fail"}
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            professor_id = data.get('professor_id')
            res = db.is_follow(user_id, professor_id)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class ChangeInfo(Resource):  # 修改用户名
    def post(self):
        res = {"state": "fail"}
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            username = None
            avatar = None
            if data.get('username'):
                username = data.get('username')
            if data.get('avatar'):
                avatar = data.get('avatar')
            res = db.change_info(user_id, username, avatar)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class ChangePwd(Resource):  # 修改密码
    def post(self):
        res = {"state": "fail"}
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            res = db.change_pwd(user_id, old_password, new_password)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class ChangeResource(Resource):  # 增加删除资源
    def post(self):
        res = {"state": "fail"}
        try:
            data = request.get_json()
            professor_id = data.get('professor_id')
            paper_url = data.get('paper_url')
            res = db.add_resource(professor_id, paper_url)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)

    def delete(self):
        res = {"state": "fail"}
        try:
            data = request.args
            professor_id = data.get('professor_id')
            paper_id = data.get('paper_id')
            res = db.rm_resource(professor_id, paper_id)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class DealRequest(Resource):  # 管理员处理申请
    def post(self):
        res = {"state": "fail"}
        try:
            data = request.get_json()
            apply_id = data.get('apply_id')
            deal = data.get('deal')
            res = db.deal_request(apply_id, deal)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class Comment(Resource):  # 评论资源
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            id = data.get('id')
            paper_id = data.get('paper_id')
            to_id = data.get('to_id')
            content = data.get('content')
            res = db.comment(id, paper_id, content)
            if res['state'] == 'success':
                res = db.send_message(id, to_id, 'COMMENT', '您的资源:' + paper_id + '收到来自用户：' + id + '的评论')
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class ReplyComment(Resource):  # 回复评论
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            id = data.get('id')
            to_id = data.get('to_id')
            reply_id = data.get('reply_id')
            content = data.get('content')
            res = db.replycomment(id, reply_id, content)
            if res['state'] == 'success':
                res = db.send_sys_sendmessage_to_one(to_id, 'REPLY', '您发布的评论:' + reply_id + '收到来自用户：' + id + '的回复')
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class DeleteComment(Resource):  # 删除评论
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            to_id = data.get('to_id')
            comment_id = data.get('comment_id')
            res = db.deletecomment(comment_id)
            if res['state'] == 'success':
                res = db.send_sys_sendmessage_to_one(to_id, 'DELETECOMMENT', '您的评论：' + comment_id + '已被删除')
                return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class SendSysmessage(Resource):  # 发送通知
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            content = data.get('content')
            res = db.send_sys_message_to_all(content)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class GetSysmessage(Resource):  # 获取通知
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            id = data.get('id')
            res = db.get_sys_message(id)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class Certification(Resource):  # 申请认证
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            id = data.get('id')
            name = data.get('name')
            ID_num = data.get('ID_num')
            text = data.get('text')
            field = data.get('field')
            res = db.certification(id, name, ID_num, field, text)
            if res['state'] == 'success':
                res = db.send_sys_sendmessage_to_admin('APPLY', '收到来自：' + id + '的认证申请，请及时处理')
                return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class CommonName(Resource):  # 同名专家申请认证
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            professor_name = data.get('professor_name')
            res = db.commonname(professor_name)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class DealCertification(Resource):  # 管理员处理认证
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            deal = data.get('deal')
            apply_id = data.get('apply_id')
            res = db.deal_certification(apply_id, deal)
            if res['state'] == 'success':
                res = db.send_sys_sendmessage_to_one(apply_id, 'APPLYRESULT', '您申请认证的结果是：'+deal)
                return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)

        
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
api.add_resource(Collection, "/api/v1/collect", endpoint="collect")
api.add_resource(Collection, "/api/v1/is_collect", endpoint="is_collect")
api.add_resource(Follow, "/api/v1/follow", endpoint="follow")
api.add_resource(Follow, "/api/v1/is_follow", endpoint="is_follow")
api.add_resource(ChangeInfo, "/api/v1/information_change", endpoint="info_change")
api.add_resource(ChangePwd, "/api/v1/password_change", endpoint="change_pwd")
api.add_resource(ChangeResource, "/api/v1/source_add", endpoint="source_add")
api.add_resource(ChangeResource, "/api/v1/source_delete", endpoint="source_delete")
api.add_resource(DealRequest, "/api/v1/deal_request", endpoint="deal_request")
api.add_resource(Comment, "/api/v1/comment", endpoint="comment")
api.add_resource(ReplyComment, "/api/v1/reply_comment", endpoint="reply_comment")
api.add_resource(DeleteComment, "/api/v1/delete_comment", endpoint="delete_comment")
api.add_resource(SendSysmessage, "/api/v1/send_sys_message", endpoint="send_sys_message")
api.add_resource(GetSysmessage, "/api/v1/get_sys_message", endpoint="get_sys_message")
api.add_resource(Certification, "/api/v1/certification", endpoint="certification")
api.add_resource(CommonName, "/api/v1/common_name", endpoint="common_name")
api.add_resource(DealCertification, "/api/v1/deal_certification", endpoint="deal_certification")

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
    # app.response_class = AResponse
