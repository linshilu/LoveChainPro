# ! /usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from time import sleep

import requests
from flask import request, jsonify, session
from flask_login import current_user, login_user

from . import main
from .. import db
from ..models import User, PairApplication, UnpairApplication, UserRelationship, Transaction, Message



@main.route('/index/', methods=['POST'])
def index():
    user = current_user
    # user = User.query.filter_by(id=2).first()
    data = {
        'name': user.name,
        'gender': '女' if user.gender else '男',
        'love_status': user.love_status,
        'balance': user.balance
    }
    return jsonify(data)


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
                                params={'appid': '',
                                        'secret': '',
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

    curr_user = User(name, gender, id_number, phone, open_id)
    login_user(curr_user)
    curr_user.last_login_time = datetime.now()
    db.session.commit()
    return jsonify(status='success')


@main.route('/login/', methods=['POST'])
def login():
    code = request.form.get('code')
    if not code:
        return jsonify(status='fail', msg='参数缺失')
    try:
        response = requests.get(url='https://api.weixin.qq.com/sns/jscode2session',
                                params={'appid': '',
                                        'secret': '',
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
    return jsonify(status='success')


@main.route('/pair/lock/apply/', methods=['POST'])
def pair_lock_apply():
    src_open_id = request.form.get('src_open_id')
    dst_open_id = request.form.get('dst_open_id')
    relationship = request.form.get('relationship')

    src_user = User.query.filter_by(open_id=src_open_id)
    dst_user = User.query.filter_by(open_id=dst_open_id)
    pa = PairApplication(src_user, dst_user, relationship)
    db.session.add(pa)
    db.session.commit()

    # todo 使用模板消息发送通知到用户b
    msg = Message()
    msg.type = Message.TYPE_PAIR
    msg.source = src_user
    msg.destination = dst_user
    msg.content = '%s向您发起了配对请求' % src_user.name
    db.session.add(msg)
    db.session.commit()

    data = {'status': 'success'}
    return jsonify(data)


@main.route('/pair/lock/confirm/', methods=['POST'])
def pair_lock_confirm():
    pa_id = request.form.get('pa_id')
    confirm = request.form.get('confirm')

    pa = PairApplication.query.filter_by(id=pa_id).first()
    pa.status = confirm
    pa.confirm_time = datetime.now()

    if pa.status == PairApplication.STATUS_APPROVE:
        pa.source.balance += 1
        pa.destination.balance += 1
        pa.source.love_status = pa.relationship
        pa.destination.love_status = pa.relationship

        ur = UserRelationship(pa.source, pa.destination, pa.relationship)
        db.session.add(ur)

        system_user = User.query.filter_by(id=1).first()
        t1 = Transaction(system_user, pa.source, 1)
        t2 = Transaction(system_user, pa.destination, 1)
        db.session.add(t1)
        db.session.add(t2)

    db.session.commit()

    # todo 使用模板消息发送通知到用户a
    msg = Message()
    msg.type = Message.TYPE_PAIR
    msg.source = pa.destination
    msg.destination = pa.source
    msg.content = '%s%s了您的配对请求' % (pa.destination.name, '同意' if pa.status == PairApplication.STATUS_APPROVE else '拒绝')
    db.session.add(msg)
    db.session.commit()

    data = {'status': 'success'}
    return jsonify(data)


@main.route('/pair/unlock/check/', methods=['POST'])
def pair_unlock_check():

    src_user = current_user
    #dest_user = src_user.relationship_source.first or src_user.relationship_destination.first

    phone_number = src_user.phone

    # TODO 发送手机验证码

    data = {'status': 'success'}
    return jsonify(data)

@main.route('/pair/unlock/process/', methods=['POST'])
def pair_unlock_process():

    src_user = current_user
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

    data = {'status': 'success'}
    return jsonify(data)

@main.route('/person/info/', methods=['GET'])
def person_info_get():
    #user = current_user
    #dest_user = user.relationship_source.first.destination.destination \
     #           or user.relationship_destination.first.source

    data = {
        'name':'1',#user.name,
        'gender':'1',#user.gender,
        'phone': 1,#user.phone,
        'IDCard': 1,#user.id_number,
        'loveStatus': '1',#user.love_status,
        'balance': 1,#user.balance,
        'mateName': '1',#dest_user.name
    }



    #print(data)

    return jsonify(data)

@main.route('/person/info', methods=['POST'])
def person_info_save():
    '''
current_user.name = request.form.get('userName')
    current_user.gender = request.form.get('userGender')
    current_user.phone = request.form.get('userPhone')
    current_user.id_number = request.form.get('userIDCard')
    current_user.love_status = request.form.get('userLoveStatus')
    current_user.name = request.form.get('userName')

    db.session.commit()
    '''
    a=request.form.get('name')
    print(a)

    data = {'status': 'success'}
    return jsonify(data)

@main.route('/message/list/', methods=['POST'])
def pair_lock_list():
    open_id = request.form.get('open_id')

    user = User.query.filter_by(open_id=open_id).first()
    msg_list = user.message_destination

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
    msg = {'id': msg_id, 'type': msg.type, 'content': msg.content, 'time': str(msg.time), 'source_name': msg.source.name}
    return jsonify(status='success', msg=msg)


#用户A提交查询表单
@main.route('/pair/query/apply/', methods = ['POST'])
def pair_query_apply():
    data = {}

    src_open_id = request.form.get('src_open_id')
    dst_open_id = request.form.get('dst_open_id')
    src_user = User.query.filter_by(open_id=src_open_id).first()
    dst_user = User.query.filter_by(open_id=dst_open_id).first()

    #qa是最近一次A对B的查询
    qa = QueryApplication.query.filter_by(source_id=src_user.id, destination_id=dst_user.id).order_by(QueryApplication.id.desc()).first()
    
    if qa == None or qa.status == QueryApplication.STATUS_DISAPPROVE:
        src_user.balance -= 1
        qa = QueryApplication(src_user, dst_user)
        db.session.add(qa)
        db.session.commit()
        data['state'] = 'sent request'
        # todo 使用模板消息发送通知到用户b
        msg = Message()
        msg.type = Message.TYPE_QUERY
        msg.source = src_user
        msg.destination = dst_user
        msg.content = '%s想要查询您的过往配对记录' % src_user.name
        db.session.add(msg)
        db.session.commit()
    elif qa.status == QueryApplication.STATUS_WAITING:
        data['state'] = 'waiting'
    elif qa.status == QueryApplication.STATUS_APPROVE:
        data['state'] = 'approve'

        #查看用户B的解锁记录
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

        #查看用户B的配对记录
        pa_list = PairApplication.query.filter((PairApplication.source_id==dst_user.id) | (PairApplication.destination_id==dst_user.id))
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


#用户B对某个查询需求进行确认
@main.route('/pair/query/confirm/', methods = ['POST'])
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
    qa.confirm_time=datetime.now()

    db.session.add(qa)
    db.session.commit()

    # todo 使用模板消息发送通知到用户a
    msg = Message()
    msg.type = Message.TYPE_PAIR
    msg.source = pa.destination
    msg.destination = pa.source
    msg.content = '%s%s了您的过往配对查询请求' % (qa.destination.name, '同意' if qa.status == PairApplication.STATUS_APPROVE else '拒绝')
    db.session.add(msg)

    data['status'] = 'success'
    return jsonify(data)


#用户查看自己历史的查询信息与被查询信息
@main.route('/pair/query/history/', methods = ['POST'])
def pair_query_histoy():
    data = {}
    qa_list_source = []
    qa_list_destination = []
    src_open_id = request.form.get('src_open_id')
    user = User.query.filter_by(open_id = src_open_id).first()
    for qa in user.query_source.all():
        qa_list_source.append({'source_open_id':qa.source_open_id, 
                               'destination_open_id':qa.destination_open_id,
                               'status':qa.status,
                               'apply_time':qa.apply_time,
                               'confirm_time':qa.confirm_time})
    for qa in user.query_destination.all():
        qa_list_destination.append({'source_open_id':qa.source_open_id, 
                                    'destination_open_id':qa.destination_open_id,
                                    'status':qa.status,
                                    'apply_time':qa.apply_time,
                                    'confirm_time':qa.confirm_time})
    data['query_list_source'] = qa_list_source
    data['query_list_destination'] = qa_list_destination
    data['status'] = 'success'
    return jsonify(data)

# 用户A发起对用户B的查询
@main.route('/searchuser',methods=['POST'])
def searchuser():
    name = request.values.get('name')
    phone = request.values.get('phone')
    identitycard = request.values.get('identitycard')
    print(name)
    print(phone)
    print(identitycard)

    # todo
    # 支付爱情币

    return 'ok'