#! /usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from flask import request, jsonify
from flask_login import current_user

from . import main
from .. import db
from ..models import User, PairApplication, UserRelationship, Transaction


@main.route('/index/', methods=['POST'])
def index():
    # user = current_user
    user = User.query.filter_by(id=2).first()
    data = {
        'name': user.name,
        'gender': '女' if user.gender else '男',
        'love_status': user.love_status,
        'balance': user.balance
    }
    return jsonify(data)


@main.route('/register/')
def register():
    pass


@main.route('/pair/lock/list/', methods=['POST'])
def pair_lock_list():
    open_id = request.form.get('open_id')

    user = User.query.filter_by(open_id=open_id)
    pa_list = PairApplication.query.filter_by(destination_id=user.id)

    data = {'status': 'success'}
    pa_data = []
    for pa in pa_list:
        tmp = {
            'id': pa.id,
            'source': pa.source.name,
            'destination': pa.destination.name,
            'status': pa.status,
            'apply_time': pa.apply_time,
            'confirm_time': pa.confirm_time
        }
        pa_data.append(tmp)
    data['data'] = pa_data
    return jsonify(data)


@main.route('/pair/lock/apply/', methods=['POST'])
def pair_lock_apply():
    src_open_id = request.form.get('src_open_id')
    dst_open_id = request.form.get('dst_open_id')
    relationship = request.form.get('relationship')

    src_user = User.query.filter_by(open_id=src_open_id)
    dst_user = User.query.filter_by(open_id=dst_open_id)
    pa = PairApplication()
    pa.source = src_user
    pa.destination = dst_user
    pa.relationship = relationship
    pa.status = 'waiting'
    db.session.add(pa)
    db.session.commit()

    # todo 使用模板消息发送通知到用户b
    data = {'status': 'success'}
    return jsonify(data)


@main.route('/pair/lock/confirm/', methods=['POST'])
def pair_lock_confirm():
    pa_id = request.form.get('pa_id')
    confirm = request.form.get('confirm')

    pa = PairApplication.query.filter_by(id=pa_id)
    pa.status = confirm
    pa.confirm_time = datetime.now()

    if pa.status == 'approve':
        pa.source.balance += 1
        pa.destination.balance += 1
        pa.source.love_status = pa.relationship
        pa.destination.love_status = pa.relationship

        ur = UserRelationship()
        ur.source = pa.source
        ur.destination = pa.destination
        ur.relationship = pa.relationship
        db.session.add(ur)

        t1 = Transaction()
        t1.source_id = 0  # system
        t1.destination = pa.source
        t1.value = 1

        t2 = Transaction()
        t2.source_id = 0  # system
        t2.destination = pa.destination
        t2.value = 1

        db.session.add(t1)
        db.session.add(t2)

    db.session.commit()

    # todo 使用模板消息发送通知到用户a
    data = {'status': 'success'}
    return jsonify(data)


@main.route('/pair/unlock/')
def pair_unlock():
    pass


@main.route('/pair/query/')
def pair_query():
    pass
