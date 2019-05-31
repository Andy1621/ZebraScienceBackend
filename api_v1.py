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
                page_num = 1
                if request.args.get('page_num'):
                    page_num = request.args.get('page_num')
                res = db.search_paper(title, int(page_num))
            elif organization_name:  # 通过机构名检索
                page_num = 1
                if request.args.get('page_num'):
                    page_num = request.args.get('page_num')
                res = db.search_organization(organization_name, int(page_num))
            # 非法搜索
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class GetDetail(Resource):  # 登录请求
    def get(self, professor_id=None, organization_name=None, user_id=None, paper_id=None):
        res = {"state": "fail"}
        try:
            if professor_id:  # 获取专家信息
                res = db.get_professor_details(professor_id)
            elif organization_name:  # 获取组织信息
                res = db.get_organization_details(organization_name)
            elif user_id:  # 获取普通用户信息
                res = db.get_user_details(user_id)
            elif paper_id:  # 获取论文信息
                res = db.get_paper_details(paper_id)
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
            username = ''
            avatar = ''
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
            old_password = encode(old_password)
            new_password = encode(new_password)
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
            if res['state'] == 'success':
                res = db.send_sys_message_to_admin('ADDRESOURCE', '收到来自：' + res['name']
                                                   + '的增加论文请求，请求链接为：' + paper_url + ',请及时处理')
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
            if res['state'] == 'success':
                res = db.send_sys_message_to_admin('DELETERESOURCE', '收到来自：' + res['name']
                                                   + '的删除论文请求，删除论文题目为《' + res['paper_name'] + '》请及时处理')
                return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class DealRequest(Resource):  # 管理员处理申请
    def post(self):
        res = {"state": "fail"}
        try:
            data = request.args
            deal = data.get('deal')
            apply_id = data.get('apply_id')
            res = db.deal_request(apply_id, deal)
            if res['state'] == 'success':
                if res['type'] == 'ADD':
                    content = res['name'] + ",恭喜您申请增加论文成功"
                    if not deal:
                        content = res['name'] + ",很抱歉您申请增加论文失败"
                    res = db.send_sys_message_to_one('RESOURCERESULT', content, res['email'])
                elif res['type'] == 'DELETE':
                    content = res['name'] + ",恭喜您申请认证成功"
                    if not deal:
                        content = res['name'] + ",很抱歉您申请失败"
                    res = db.send_sys_message_to_one('RESOURCERESULT', content, res['email'])
                return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class Comment(Resource):  # 评论资源
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            paper_id = data.get('paper_id')
            res = db.get_comment(paper_id)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)

    def post(self):
        res = {"state": "fail"}
        try:
            data = request.get_json()
            from_email = data.get('from_email')
            paper_id = data.get('paper_id')
            content = data.get('content')
            res = db.comment(from_email, paper_id, content)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class ReplyComment(Resource):  # 回复评论
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            from_email = data.get('from_email')
            to_email = data.get('to_email')
            comment_id = data.get('reply_id')
            content = data.get('content')
            comment = data.get('comment')
            from_name = data.get('from_name')
            res = db.reply_comment(comment_id, from_email, content)
            if res['state'] == 'success':
                res = db.send_sys_message_to_one('REPLY', '您发布的评论: "' + comment + '"收到来自用户：'
                                                 + from_name + '的回复', to_email)
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
            content = data.get('content')
            res = db.delete_comment(comment_id)
            if res['state'] == 'success':
                res = db.send_sys_message_to_one(to_id, 'DELETECOMMENT', '您的评论："' + content + '"已被删除')
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class SendSysMessage(Resource):  # 发送通知
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            content = data.get('content')
            res = db.send_sys_message_to_all('SYSTEM', content)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class GetSysMessage(Resource):  # 获取通知
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            email = data.get('email')
            res = db.get_sys_message(email)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class Certification(Resource):  # 申请认证
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            print(data)
            email = data.get('email')
            name = data.get('name')
            ID_num = data.get('ID_num')
            text = data.get('text')
            field = data.get('field')
            scid = data.get('scid')
            res = db.certification(email, name, ID_num, field, text, scid)
            print(res)
            if res['state'] == 'success':
                res = db.send_sys_message_to_admin('APPLY', '收到来自：' + name + '的认证申请，请及时处理')
                print(res)
            return dumps(res, ensure_ascii=False)
        except:
            print(2)
            return dumps(res, ensure_ascii=False)


class CommonName(Resource):  # 同名专家申请认证
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            professor_name = data.get('professor_name')
            res = db.common_name(professor_name)
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
                content = res['name'] + ",恭喜您申请认证成功"
                if not deal:
                    content = res['name'] + ",很抱歉您的申请认证被拒绝"
                res = db.send_sys_message_to_one('APPLYRESULT', content, res['email'])
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class DeleteMessage(Resource):  # 删除消息
    def post(self):
        res = {"state": "fail"}
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            message_id = ''
            message_type = ''
            if data.get('message_type'):
                message_type = data.get('message_type')
                res = db.delete_message_onetype(user_id, message_type)
            else:
                message_type = data.get('message_type')
                res = db.delete_message_onepiece(user_id, message_id)
            return dumps(res, ensure_ascii=False)
        except:
            return dumps(res, ensure_ascii=False)


class GetApply(Resource):  # 获取认证信息
    def get(self):
        res = {"state": "fail"}
        try:
            data = request.args
            apply_id = data.get('apply_id')
            res = db.get_apply(apply_id)
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
api.add_resource(GetDetail, "/api/v1/organization_detail/<string:organization_name>", endpoint="organization_detail")
api.add_resource(GetDetail, "/api/v1/paper_detail/<string:paper_id>", endpoint="paper_id")
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
api.add_resource(SendSysMessage, "/api/v1/send_sys_message", endpoint="send_sys_message")
api.add_resource(GetSysMessage, "/api/v1/get_sys_message", endpoint="get_sys_message")
api.add_resource(Certification, "/api/v1/certification", endpoint="certification")
api.add_resource(CommonName, "/api/v1/common_name", endpoint="common_name")
api.add_resource(DealCertification, "/api/v1/deal_certification", endpoint="deal_certification")
api.add_resource(DeleteMessage, "/api/v1/delete_message", endpoint="delete_message")
api.add_resource(GetApply, "/api/v1/get_apply", endpoint="get_apply")

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
    # app.response_class = AResponse
