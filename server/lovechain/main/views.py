#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import main
from ..models import User, UserRelationship, Transaction


@main.route('/')
def index():
    User.query.all()
    return '200'
