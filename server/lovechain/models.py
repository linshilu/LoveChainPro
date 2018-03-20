#! /usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from flask_login import UserMixin

from . import db, login_manager


class User(UserMixin, db.Model):
    def __init__(self, name, gender, id_number, phone, open_id):
        self.name = name
        self.gender = gender
        self.id_number = id_number
        self.phone = phone
        self.open_id = open_id

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.Boolean, default=True)  # false: male true: female
    phone = db.Column(db.String(64), nullable=False)
    id_number = db.Column(db.String(64), nullable=False)
    love_status = db.Column(db.Integer, nullable=False)  # 1.single 2. lover 3.couple
    balance = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now)
    last_login_time = db.Column(db.DateTime(), default=datetime.now)

    open_id = db.Column(db.String(64), default=None)

    LOVE_STATUS_SINGLE = 1
    LOVE_STATUS_LOVER = 2
    LOVER_STATUS_COUPLE = 3


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UserRelationship(db.Model):
    __tablename__ = 'user_relationship'
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    destination_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    relationship = db.Column(db.String(64), nullable=False)
    time = db.Column(db.DateTime(), default=datetime.now)

    source = db.relationship('User', foreign_keys=[source_id],
                             backref=db.backref('relationship_source', lazy='dynamic'))
    destination = db.relationship('User', foreign_keys=[destination_id],
                                  backref=db.backref('relationship_destination', lazy='dynamic'))


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    destination_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime(), default=datetime.now)

    source = db.relationship('User', foreign_keys=[source_id], backref=db.backref('transaction_source', lazy='dynamic'))
    destination = db.relationship('User', foreign_keys=[destination_id],
                                  backref=db.backref('transaction_destination', lazy='dynamic'))


class PairApplication(db.Model):
    __tablename__ = 'pair_application'
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    destination_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    type = db.Column(db.Integer, nullable=False)  # 1.lover 2.couple
    status = db.Column(db.Integer, nullable=False)  # 1.waiting 2.approve 3.disapprove
    apply_time = db.Column(db.DateTime(), default=datetime.now)
    confirm_time = db.Column(db.DateTime(), default=None)

    source = db.relationship('User', foreign_keys=[source_id], backref=db.backref('pair_source', lazy='dynamic'))
    destination = db.relationship('User', foreign_keys=[destination_id],
                                  backref=db.backref('pair_destination', lazy='dynamic'))

    TYPE_LOVER = 1
    TYPE_COUPLE = 2
    STATUS_WAITING = 1
    STATUS_APPROVE = 2
    STATUS_DISAPPROVE = 3


class QueryApplication(db.Model):
    __tablename__ = 'query_application'
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    destination_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    status = db.Column(db.Integer, nullable=False)  # 1.waiting 2.approve 3.disapprove
    apply_time = db.Column(db.DateTime(), default=datetime.now)
    confirm_time = db.Column(db.DateTime(), default=None)

    source = db.relationship('User', foreign_keys=[source_id], backref=db.backref('query_source', lazy='dynamic'))
    destination = db.relationship('User', foreign_keys=[destination_id],
                                  backref=db.backref('query_destination', lazy='dynamic'))

    STATUS_WAITING = 1
    STATUS_APPROVE = 2
    STATUS_DISAPPROVE = 3
