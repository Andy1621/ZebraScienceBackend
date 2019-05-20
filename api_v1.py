from flask import Flask, request
from flask_restful import Api, Resource
from utils import send_email, encode
from DBClass import DbOperate
from flask_cors import *

app = Flask(__name__)
CORS(app, resources=r'/*')
db = DbOperate()


class EmailVerify(Resource):  # 邮箱绑定请求验证码
    def post(self):
        try:
            data = request.get_json()
            email = data['email']
            res = db.generate_email_code(email)  # 此时生成邮箱验证码+时间戳
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
        return db.create_user(password, email, username, avatar, email_code)


class Login(Resource):  # 登录请求
    def post(self):
        data = request.get_json()
        password = data['password']
        password = encode(password)
        email = data['email']
        try:
            return db.compare_password(password, email)
        except:
            return {"state": "fail"}


class Search(Resource):  # 登录请求
    def get(self, professor_name=None, title=None, organization_name=None):
        try:
            if professor_name:  # 通过专家名检索
                return db.search_professor(professor_name)
            elif title:  # 通过文章名检索
                return db.search_paper(title)
            elif organization_name:  # 通过机构名检索
                return db.search_organization(organization_name)
            else:  # 非法搜索
                return {"state": "fail"}
        except:
            return {"state": "fail"}


class GetDetail(Resource):  # 登录请求
    def get(self, professor_id=None, organization_id=None, user_id=None):
        try:
            if professor_id:  # 获取专家信息
                return db.get_professor_details(professor_id)
            elif organization_id:  # 获取组织信息
                return db.get_organization_details(organization_id)
            elif user_id:  # 获取普通用户信息
                return db.get_user_details(user_id)
            else:  # 非法搜索
                return {"state": "fail"}
        except:
            return {"state": "fail"}


class Collection(Resource):  # 论文资源
    def get(self):  # 收藏资源
        try:
            data = request.args
            user_id = data['user_id']
            paper_id = data['paper_id']
            return db.collect(user_id, paper_id)
        except:
            return {"state": "fail"}

    def delete(self):  # 删除收藏
        try:
            data = request.args
            user_id = data['user_id']
            paper_id = data['paper_id']
            return db.delete_collect(user_id, paper_id)
        except:
            return {"state": "fail"}

    def post(self):  # 是否收藏
        try:
            data = request.get_json()
            user_id = data['user_id']
            paper_id = data['paper_id']
            return db.is_collect(user_id, paper_id)
        except:
            return {"state": "fail"}


class Follow(Resource):  # 关注
    def get(self):  # 关注
        try:
            data = request.args
            user_id = data['user_id']
            professor_id = data['professor_id']
            return db.follow(user_id, professor_id)
        except:
            return {"state": "fail"}

    def delete(self):  # 取消关注
        try:
            data = request.args
            user_id = data['user_id']
            professor_id = data['professor_id']
            return db.un_follow(user_id, professor_id)
        except:
            return {"state": "fail"}

    def post(self):  # 是否关注
        try:
            data = request.get_json()
            user_id = data['user_id']
            professor_id = data['professor_id']
            return db.is_follow(user_id, professor_id)
        except:
            return {"state": "fail"}


class ChangeInfo(Resource):  # 修改用户名
    def post(self):
        try:
            data = request.get_json()
            user_id = data['user_id']
            username = None
            avatar = None
            if data['username']:
                username = data['username']
            if data['avatar']:
                avatar = data['avatar']
            return db.change_info(user_id, username, avatar)
        except:
            return {"state": "fail"}


class ChangePwd(Resource):  # 修改密码
    def post(self):
        try:
            data = request.get_json()
            user_id = data['user_id']
            old_password = data['old_password']
            new_password = data['new_password']
            return db.change_pwd(user_id, old_password, new_password)
        except:
            return {"state": "fail"}


class ChangeResource(Resource):  # 增加删除资源
    def post(self):
        try:
            data = request.get_json()
            professor_id = data['professor_id']
            paper_url = data['paper_url']
            return db.add_resource(professor_id, paper_url)
        except:
            return {"state": "fail"}

    def delete(self):
        try:
            data = request.args
            professor_id = data['professor_id']
            paper_id = data['paper_id']
            return db.rm_resource(professor_id, paper_id)
        except:
            return {"state": "fail"}


class DealRequest(Resource):  # 管理员处理申请
    def post(self):
        try:
            data = request.get_json()
            apply_id = data['apply_id']
            deal = data['deal']
            return db.deal_request(apply_id, deal)
        except:
            return {"state": "fail"}


class Comment(Resource):  # 评论资源
    def get(self):
        try:
            data = request.args
            id = data['id']
            paperid = data['paperid']
            toid = data['toid']
            content = data['content']
            if(db.comment(id,paperid,content)['state'] == 'success'):
                return db.sendmessage(id, toid, COMMENT, '您发布的资源:'+paperid+'收到来自用户：'+id+'的评论')
        except:
            return {"state": "fail"}


class ReplyComment(Resource):  # 回复评论
    def get(self):
        try:
            data = request.args
            id = data['id']
            toid = data['toid']
            replyid = data['replyid']
            content = data['content']
            if (db.replycomment(id,replyid,content)['state'] == 'success'):
                return db.sendmessage(id, toid, REPLY, '您发布的评论:' + replyid + '收到来自用户：' + id + '的回复')

        except:
            return {"state": "fail"}


class DeleteComment(Resource):  # 删除评论
    def get(self):
        try:
            data = request.args
            toid = data['toid']
            comment_id = data['comment_id']
            if (db.deletecomment(comment_id)['state'] == 'success'):
                return db.send_sys_sendmessage_toone(toid,DELETECOMMENT,'您的评论：'+comment_id+'已被删除')
        except:
            return {"state": "fail"}


class SendSysmessage(Resource):  # 发送通知
    def get(self):
        try:
            data = request.args
            content = data['content']
            return db.send_sys_message_toall(content)
        except:
            return {"state": "fail"}


class GetSysmessage(Resource):  # 获取通知
    def get(self):
        try:
            data = request.args
            id = data['id']
            return db.getsysmessage(id)
        except:
            return {"state": "fail"}


class Certification(Resource):  # 申请认证
    def get(self):
        try:
            data = request.args
            id = data['id']
            name = data['name']
            ID_num = data['ID_num']
            text = data['text']
            field = data['field']
            if(db.certification(id,name,ID_num,field,text)['state'] == 'success'):
                return db.send_sys_sendmessage_toadmin(APPLY, '收到来自：' + id + '的认证申请，请及时处理')
        except:
            return {"state":"fail"}


class CommonName(Resource):  # 同名专家申请认证
    def get(self):
        try:
            data = request.args
            professor_name = data['professor_name']
            return db.commonname(professor_name)
        except:
            return {"state":"fail"}


class DealCertification(Resource):  # 管理员处理认证
    def get(self):
        try:
            data = request.args
            deal = data['deal']
            apply_id = data['apply_id']
            if(db.deal_certification(apply_id, deal)['state'] == 'success'):
                return db.send_sys_sendmessage_toone(apply_id,APPLYRESULT,'您申请认证的结果是：'+deal)
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
