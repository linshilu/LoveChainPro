# ! /usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import requests
from flask import request, jsonify, session
from flask_login import current_user, login_user

from . import main
from .. import db
from ..models import User, PairApplication, UserRelationship, Transaction, Message


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


@main.route('/pair/unlock/')
def pair_unlock():
    pass


@main.route('/pair/query/')
def pair_query():
    pass


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
