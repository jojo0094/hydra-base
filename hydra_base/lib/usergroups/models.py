#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) Copyright 2013 to 2017 University of Manchester
#
# HydraPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HydraPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with HydraPlatform.  If not, see <http://www.gnu.org/licenses/>
#

from sqlalchemy import Column,\
ForeignKey,\
text,\
Integer,\
String,\
LargeBinary,\
TIMESTAMP,\
BIGINT,\
Float,\
Text, \
DateTime,\
Unicode

from sqlalchemy.orm import relationship, backref

from hydra_base.db.models import AuditMixin, Base, Inspect

class UserGroupType(AuditMixin, Base, Inspect):
    """
        The definition of a type of user group.
        Examples could include: 'organisation', 'department', 'team'
    """

    id = Column(Integer(), primary_key=True, nullable=False)
    name = Column(String(200), primary_key=True, nullable=False)

    def __repr__(self):
        return "User Group {0} (id={1})".format(self.name, self.id)


class UserGroup(AuditMixin, Base, Inspect):
    """
    """
    __tablename__ = 'tUserGroup'

    id = Column(Integer(), primary_key=True, nullable=False)
    name = Column(String(200), primary_key=True, nullable=False)
    type_id = Column(Integer(), primary_key=True, nullable=False)
    parent_id = Column(Integer(), ForeignKey('tUserGroup.id'), nullable=True)

    grouptype = relationship('UserGroupType', lazy='joined',
                             backref=backref("groups",
                                             uselist=True,
                                             order_by="id",
                                             cascade="all, delete-orphan"))

    parent = relationship('UserGroup', lazy='joined', remote_side=[id],
                          backref=backref("groups",
                                          uselist=True,
                                          order_by="id",
                                          cascade="all, delete-orphan"))

    def __repr__(self):
        return "{0}".format(self.name)

class UserGroupMember(AuditMixin, Base, Inspect):
    """
    """

    __tablename__ = 'tUserGroupUser'

    usergroup_id = Column(Integer(), primary_key=True, nullable=False)
    user_id = Column(Integer(), primary_key=True, nullable=False)

    group = relationship('UserGroup', lazy='joined',
                         backref=backref("users",
                                         uselist=True,
                                         order_by="id",
                                         cascade="all, delete-orphan"))

    def __repr__(self):
        return "{0} : {1}".format(self.group_id, self.user_id)

class GroupRoleUser(Base, Inspect):
    """
    This class defines the role of a user within the context of a user group
    """

    __tablename__ = 'tGroupRoleUser'

    user_id = Column(Integer(), ForeignKey('tUser.id'), primary_key=True, nullable=False)
    role_id = Column(Integer(), ForeignKey('tRole.id'), primary_key=True, nullable=False)
    usergroup_id = Column(Integer(), ForeignKey('tUserGroup.id'), primary_key=True, nullable=True)

    user = relationship('User', lazy='joined')
    role = relationship('Role', lazy='joined')
    usergroup = relationship('UserGroup', lazy='joined')

    _parents = ['tRole', 'tUser', 'tUserGroup']
    _children = []

    def __repr__(self):
        return "{0}".format(self.role.name)
