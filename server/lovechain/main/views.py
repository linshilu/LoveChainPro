# ! /usr/bin/env python
# -*- coding: utf-8 -*-
import random
from datetime import datetime

import requests
from flask import request, jsonify, session, current_app, json, abort
from flask_login import current_user, login_user

from . import main
from .. import db
from ..models import User, PairApplication, UnpairApplication, UserRelationship, Transaction, Message, QueryApplication


@main.route('/', methods=['GET', 'POST'])
def index():
    return 'success'


@main.route('/register/', methods=['POST'])
def register():
    name = request.form.get('name')
    gender = request.form.get('gender')
    id_number = request.form.get('id_number')
    phone = request.form.get('phone')
    code = request.form.get('code')

    if (name and gender and id_number and phone and code) is None:
        return jsonify(status='fail', msg='参数缺失，注册失败')

    try:
        response = requests.get(url='https://api.weixin.qq.com/sns/jscode2session',
                                params={'appid': current_app.config['APP_ID'],
                                        'secret': current_app.config['APP_SECRET'],
                                        'js_code': code,
                                        'grant_type': 'authorization_code'}, timeout=10)
        response.raise_for_status()
        result = response.json()
    except requests.RequestException:
        return jsonify(status='fail', msg='无法连接微信服务器')

    if result.get('errcode'):
        return jsonify(status='fail', msg='微信登陆错误')

    open_id = result.get('openid')
    session_key = result.get('session_key')
    session['session_key'] = session_key

    curr_user = User(name, gender == '1', id_number, phone, open_id)
    curr_user.last_login_time = datetime.now()
    db.session.add(curr_user)
    db.session.commit()
    login_user(curr_user)
    love_status_map = {
        User.LOVE_STATUS_SINGLE: '单身中',
        User.LOVE_STATUS_LOVER: '恋爱中',
        User.LOVER_STATUS_COUPLE: '婚姻中'
    }
    data = {
        'status': 'success',
        'name': curr_user.name,
        'gender': '女' if curr_user.gender else '男',
        'love_status': love_status_map.get(curr_user.love_status),
        'balance': curr_user.balance
    }
    return jsonify(status='success', user=data, msg='注册成功')


@main.route('/login/', methods=['POST'])
def login():
    code = request.form.get('code')
    if not code:
        return jsonify(status='fail', msg='参数缺失')
    try:
        response = requests.get(url='https://api.weixin.qq.com/sns/jscode2session',
                                params={'appid': current_app.config['APP_ID'],
                                        'secret': current_app.config['APP_SECRET'],
                                        'js_code': code,
                                        'grant_type': 'authorization_code'}, timeout=10)
        response.raise_for_status()
        result = response.json()
    except requests.RequestException:
        return jsonify(status='fail', msg='无法连接微信服务器')

    if result.get('errcode'):
        return jsonify(status='fail', msg='微信登陆错误')

    open_id = result.get('openid')
    session_key = result.get('session_key')
    session['session_key'] = session_key

    curr_user = User.query.filter_by(open_id=open_id).first()
    if not curr_user:
        return jsonify(status='fail', msg='未注册')
    login_user(curr_user)
    curr_user.last_login_time = datetime.now()
    db.session.commit()

    # for test
    # curr_user = User.query.filter_by(id=2).first()
    # login_user(curr_user)

    love_status_map = {
        User.LOVE_STATUS_SINGLE: '单身中',
        User.LOVE_STATUS_LOVER: '恋爱中',
        User.LOVER_STATUS_COUPLE: '婚姻中'
    }
    data = {
        'status': 'success',
        'name': curr_user.name,
        'gender': '女' if curr_user.gender else '男',
        'love_status': love_status_map.get(curr_user.love_status),
        'balance': curr_user.balance
    }
    return jsonify(status='success', user=data, msg='登陆成功')


@main.route('/user/data/', methods=['POST'])
def user_data():
    love_status_map = {
        User.LOVE_STATUS_SINGLE: '单身中',
        User.LOVE_STATUS_LOVER: '恋爱中',
        User.LOVER_STATUS_COUPLE: '婚姻中'
    }

    data = {
        'status': 'success',
        'name': current_user.name,
        'gender': '女' if current_user.gender else '男',
        'love_status': love_status_map.get(current_user.love_status),
        'balance': current_user.balance
    }
    return jsonify(data)


@main.route('/pair/lock/apply/', methods=['POST'])
def pair_lock_apply():
    name = request.form.get('name')
    id_number = request.form.get('id_number')
    phone = request.form.get('phone')
    relationship = request.form.get('relationship')

    if not ((id_number or phone) and name and relationship):
        return jsonify(status='fail', msg='参数缺失')

    if id_number:
        dst_user = User.query.filter_by(name=name).filter_by(id_number=id_number).first()
    else:
        dst_user = User.query.filter_by(name=name).filter_by(phone=phone).first()

    pa = PairApplication(current_user, dst_user, relationship)
    db.session.add(pa)
    db.session.commit()

    msg = Message()
    msg.type = Message.TYPE_PAIR
    msg.associated_id = pa.id
    msg.source = current_user
    msg.destination = dst_user
    msg.content = '%s向您发起了配对请求' % current_user.name
    db.session.add(msg)
    db.session.commit()

    return jsonify(status='success')


@main.route('/pair/lock/confirm/', methods=['POST'])
def pair_lock_confirm():
    msg_id = request.form.get('msg_id')
    msg = Message.query.filter_by(id=msg_id).first()
    pa_id = msg.associated_id
    confirm = request.form.get('confirm')

    pa = PairApplication.query.filter_by(id=pa_id).first()
    pa.status = int(confirm)
    pa.confirm_time = datetime.now()

    if pa.status == PairApplication.STATUS_APPROVE:
        pa.source.balance += 1
        pa.destination.balance += 1
        pa.source.love_status = pa.relationship + 1
        pa.destination.love_status = pa.relationship + 1

        ur = UserRelationship(pa.source, pa.destination, pa.relationship)
        db.session.add(ur)

        system_user = User.query.filter_by(id=1).first()
        t1 = Transaction(system_user, pa.source, 1)
        t2 = Transaction(system_user, pa.destination, 1)
        db.session.add(t1)
        db.session.add(t2)
        db.session.commit()

    # todo fix bug
    a = pa.source

    msg = Message()
    msg.type = Message.TYPE_CONFIRM
    msg.associated_id = pa.id
    msg.source = pa.destination
    msg.destination = pa.source
    msg.content = '%s%s了您的配对请求' % (pa.destination.name, '同意' if pa.status == PairApplication.STATUS_APPROVE else '拒绝')
    db.session.add(msg)
    db.session.commit()

    return jsonify(status='success', msg='')


@main.route('/pair/unlock/check/', methods=['POST'])
def pair_unlock_check():
    src_user = current_user

    # dest_user = src_user.relationship_source.first or src_user.relationship_destination.first

    # phone_number = src_user.phone

    # 生成验证码并保存
    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    x = random.choice(chars), random.choice(chars), random.choice(chars), random.choice(chars)

    verify_code = "".join(x)
    current_app.verify_code = {1: verify_code}  # {src_user.id : verifyCode}

    # 发送验证码
    resp = requests.post("http://sms-api.luosimao.com/v1/send.json",
                         auth=("api", "key-4e30423e090f54262b19ed7430e725d8"),
                         data={
                             "mobile": '18819461670',  # phone_number,
                             "message": '您的手机验证码为' + verify_code + "，有效时间为10分钟，请勿泄露【元启科技】"
                         }, timeout=5, verify=False
                         )

    result = json.loads(resp.content)
    print(result)
    data = {
        'status': 'success',
        'msg': result["msg"],
        "errorCode": result["error"]
    }

    return jsonify(data)


@main.route('/pair/unlock/process/', methods=['POST'])
def pair_unlock_process():
    src_user = current_user
    target_relationship = src_user.relationship_source.first or src_user.relationship_destination.first
    dest_user = src_user.relationship_source.first.destination.destination or src_user.relationship_destination.first.source

    verify_code = request.form.get('verifyCode')

    src_user = current_user

    if int(verify_code) == current_app.verify_code[src_user.id]:
        target_relationship = src_user.relationship_source.first \
                              or src_user.relationship_destination.first

        dest_user = src_user.relationship_source.first.destination.destination \
                    or src_user.relationship_destination.first.source

        un_pa = UnpairApplication()
        un_pa.source = src_user
        un_pa.destination = dest_user
        un_pa.relationship = 'single'
        un_pa.status = 'approve'
        db.session.add(un_pa)

        db.session.delete(target_relationship)

        db.session.commit()

        data = {
            'status': 'success',
            'msg': '解除配对成功'
        }

    else:
        data = {
            'status': 'success',
            'msg': '验证失败'
        }

    return jsonify(data)


@main.route('/person/info/', methods=['GET'])
def person_info_get():
    # user = current_user
    # dest_user = user.relationship_source.first.destination.destination \
    #           or user.relationship_destination.first.source

    data = {
        'name': '1',  # user.name,
        'gender': '1',  # user.gender,
        'phone': 1,  # user.phone,
        'IDCard': 1,  # user.id_number,
        'loveStatus': '1',  # user.love_status,
        'balance': 1,  # user.balance,
        'mateName': '1',  # dest_user.name
    }

    # print(data)

    return jsonify(data)


@main.route('/person/info', methods=['POST'])
def person_info_save():
    # current_user.name = request.form.get('userName')
    # current_user.gender = request.form.get('userGender')
    # current_user.phone = request.form.get('userPhone')
    # current_user.id_number = request.form.get('userIDCard')
    # current_user.love_status = request.form.get('userLoveStatus')
    # current_user.name = request.form.get('userName')
    #
    # db.session.commit()

    a = request.form.get('name')
    print(a)

    data = {'status': 'success'}
    return jsonify(data)


@main.route('/message/list/', methods=['POST'])
def pair_lock_list():
    msg_list = current_user.message_destination.order_by(Message.time.desc()).all()

    msg_type_map = {
        Message.TYPE_PAIR: '配对请求',
        Message.TYPE_UNPAIR: '解除配对通知',
        Message.TYPE_QUERY: '查询配对请求',
        Message.TYPE_TRANSACTION: '交易通知'
    }
    msg_data = []
    for msg in msg_list:
        tmp = {
            'id': msg.id,
            'type': msg.type,
            'title': msg_type_map.get(msg.type),
            'content': msg.content,
            'time': msg.time,
            'associated_id': msg.associated_id
        }
        msg_data.append(tmp)

    data = {'status': 'success', 'data': msg_data}
    return jsonify(data)


@main.route('/message/detail/', methods=['POST'])
def message_detail():
    msg_id = request.form.get('msg_id')

    if not msg_id:
        return jsonify(status='fail', msg='参数缺失')

    msg = Message.query.filter_by(id=msg_id).first()
    msg.status = 2
    db.session.commit()
    msg = {'id': msg_id, 'type': msg.type, 'content': msg.content, 'time': str(msg.time),
           'source_name': msg.source.name}
    return jsonify(status='success', msg=msg)


# 用户A提交查询表单
@main.route('/pair_query/apply/', methods=['POST'])
def pair_query_apply():
    data = {}

    # 获取当前登陆的用户
    # src_user = current_user
    src_open_id = request.form.get('src_open_id')
    dst_open_id = request.form.get('dst_open_id')

    src_user = User.query.filter_by(open_id=src_open_id).first()
    dst_user = User.query.filter_by(open_id=dst_open_id).first()

    if dst_user is None:
        data['state'] = 'This user does not exist.'
        return jsonify(data)
    if src_open_id == dst_open_id:
        data['state'] = 'cannot search yourself.'
        return jsonify(data)
    # qa是最近一次A对B的查询
    qa = QueryApplication.query.filter_by(source_id=src_user.id, destination_id=dst_user.id).order_by(
        QueryApplication.id.desc()).first()

    if qa is None or qa.status == QueryApplication.STATUS_DISAPPROVE:
        qa = QueryApplication(src_user, dst_user, QueryApplication.STATUS_WAITING)
        db.session.add(qa)
        db.session.commit()
        data['state'] = 'sent request'
        src_user.balance -= 1
        # todo 使用模板消息发送通知到用户b
        msg = Message()
        msg.type = Message.TYPE_QUERY
        msg.source = src_user
        msg.destination = dst_user
        msg.content = u'%s想要查询您的过往配对记录' % src_user.name
        db.session.add(msg)
        db.session.commit()
    elif qa.status == QueryApplication.STATUS_WAITING:
        data['state'] = 'waiting'
    elif qa.status == QueryApplication.STATUS_APPROVE:
        data['state'] = 'approve'

    return jsonify(data)


# 配对查询的结果列表
@main.route('/pair_query/result/list/', methods=['POST'])
def pair_query_result_list():
    data = {}

    qa_list_source = []

    src_open_id = request.form.get('src_open_id')
    user = User.query.filter_by(open_id=src_open_id).first()
    for qa in user.query_source.all():
        qa_list_source.append({'source_open_id': qa.source.open_id,
                               'destination_open_id': qa.destination.open_id,
                               'status': qa.status,
                               'apply_time': qa.apply_time,
                               'confirm_time': qa.confirm_time})
    data['qa_list_source'] = qa_list_source

    return jsonify(data)


# 配对查询的结果详细情况，若对方已经授权，则可以看到其过往的配对信息
@main.route('/pair_query/result/detail/', methods=['POST'])
def pair_query_result_detail():
    data = {}

    src_open_id = request.form.get('src_open_id')
    src_open_id = 1
    dst_open_id = request.form.get('dst_open_id')
    dst_user = User.query.filter_by(open_id=dst_open_id).first()

    # 查看用户B的解锁记录
    '''
    ua_list = UnpairApplication.query.filter((UnpairApplication.source_id==dst_user.id) | (UnpairApplication.destination_id==dst_user.id))
    ua_data = []
    for ua in ua_list:
        tmp = {
            'confirm_time': ua.time,
            'source': '****',
            'destination': '****'
        }
        if ua.source.id == dst_user.id:
            tmp['source'] = ua.source.open_id
        else:
            tmp['destination'] = ua.destination.open_id
        ua_data.append(tmp)
    data['unlock_history'] = ua_data
    '''

    # 查看用户B的配对记录
    pa_list = PairApplication.query.filter(
        (PairApplication.source_id == dst_user.id) | (PairApplication.destination_id == dst_user.id))
    pa_data = []
    for pa in pa_list:
        tmp = {
            'confirm_time': pa.confirm_time,
            'source': '****',
            'destination': '****'
        }
        if pa.source.id == dst_user.id:
            tmp['source'] = pa.source.open_id
        else:
            tmp['destination'] = pa.destination.open_id
        pa_data.append(tmp)
    data['lock_history'] = pa_data
    data['status'] = 'success'

    return jsonify(data)


# 用户B对某个查询需求进行确认
@main.route('/pair/query/confirm/', methods=['POST'])
def pair_query_confirm():
    data = {}
    qa_id = request.form.get('qa_id')
    confirm = int(request.form.get('confirm'))

    if confirm == QueryApplication.STATUS_APPROVE:
        data['state'] = 'approve'
    else:
        data['state'] = 'disapprove'

    qa = QueryApplication.query.filter_by(id=qa_id).order_by(QueryApplication.id.desc()).first()
    qa.status = confirm
    qa.confirm_time = datetime.now()

    db.session.add(qa)
    db.session.commit()

    # todo 使用模板消息发送通知到用户a
    msg = Message()
    msg.type = Message.TYPE_QUERY
    msg.source = qa.destination
    msg.destination = qa.source
    msg.content = '%s%s了您的过往配对查询请求' % (
        qa.destination.name, '同意' if qa.status == PairApplication.STATUS_APPROVE else '拒绝')
    db.session.add(msg)

    data['status'] = 'success'
    return jsonify(data)


# 用户查看自己历史的查询信息与被查询信息
@main.route('/pair/query/history/', methods=['POST'])
def pair_query_history():
    data = {}
    qa_list_source = []
    qa_list_destination = []
    src_open_id = request.form.get('src_open_id')
    user = User.query.filter_by(open_id=src_open_id).first()
    for qa in user.query_source.all():
        qa_list_source.append({'source_open_id': qa.source_open_id,
                               'destination_open_id': qa.destination_open_id,
                               'status': qa.status,
                               'apply_time': qa.apply_time,
                               'confirm_time': qa.confirm_time})
    for qa in user.query_destination.all():
        qa_list_destination.append({'source_open_id': qa.source_open_id,
                                    'destination_open_id': qa.destination_open_id,
                                    'status': qa.status,
                                    'apply_time': qa.apply_time,
                                    'confirm_time': qa.confirm_time})
    data['query_list_source'] = qa_list_source
    data['query_list_destination'] = qa_list_destination
    data['status'] = 'success'
    return jsonify(data)


@main.route('/close/', methods=['POST'])
def close():
    current_user.close = True
    db.session.commit()
    data = {'status': 'success'}
    return jsonify(data)
