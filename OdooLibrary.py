# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Clear ICT Solutions <info@clearict.com>.
#    All Rights Reserved.
#    @author: Michael Telahun Makonnen <miket@clearict.com>
#
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import erppeek


class OdooLibrary(object):

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, url, db=None, user=None, password=None):

        self.client = None
        self._url = None
        self._db = None
        self._user = None
        self._password = None
        self.connect(url, db=db, user=user, password=password)

    def connect(self, url, db=None, user=None, password=None):
        """Make a connection to an Odoo instance."""

        if db is not None:
            self.client = erppeek.Client(url, db=db, user=user,
                                         password=password)
            self._db = db
            self._user = user
            self._password = password
        else:
            self.client = erppeek.Client(url)
        self._url = url

    def reset_connection(self):
        """Reconnect to initial URL and connection parameters."""

        self.client.reset()
        self.connect(self._url, db=self._db, user=self._user,
                     password=self._password)

    def login(self, user, password, db=None):
        """Log into an Odoo database. You must be connected to an
           Odoo server first. If you are already logged in and no
           database is specified this method can be used to switch
           users."""

        self.client.login(user, password=password, database=db)

    def create_database(self, super_pwd, db_name, demo=False, drop=False):
        """Create a new database with name db_name and verifies its
           existance."""

        if drop and db_name in self.client.db.list():
            self.drop_database(super_pwd, db_name)
        self.client.create_database(super_pwd, db_name, demo=demo)
        assert db_name in self.client.db.list(), \
            "The database %s was not created!" % (db_name)

    def drop_database(self, super_pwd, db_name):
        """Drop database db_name."""

        self.client.db.drop(super_pwd, db_name)

    def database_exists(self, db_name):
        """Returns true if database db_name already exists, false otherwise."""

        assert db_name in self.client.db.list(), \
            "The database %s does not exist!" % (db_name)

    def installed_modules(self):
        """Returns a list of all installed modules."""

        obj = self.client.model('ir.module.module')
        modules = obj.browse([('state', '=', 'installed')])
        res = [m.name for m in modules]
        return res

    def modules_are_installed(self, check_list):
        """Checks that all modules listed in check_list are installed in
           the database"""

        installed_modules = self.installed_modules()
        for modname in check_list:
            assert modname in installed_modules, \
                "Module %s is not installed" % (modname)

    def install_modules(self, module_names):
        """Install all modules listed in module_names."""

        self.client.install(module_names)

    def uninstall_modules(self, module_names):
        """Un-install all modules listed in module_names."""

        self.client.uninstall(module_names)

    def count_records(self, model, domain):
        """Filter all records for model according to domain and
        return the number of matching records."""

        assert erppeek.issearchdomain(domain), "Invalid domain argument!"
        res = self.client.count(model, domain)
        return res

    def search_records(self, model, domain, offset=0, limit=None, order=None,
                       context=None):
        """Filter all the records for model according to domain and
           return the ids of matching records."""

        assert erppeek.issearchdomain(domain), "Invalid domain argument!"
        res_ids = self.client.search(
            model, domain, offset=offset, limit=limit, order=order,
            context=context
        )
        return res_ids

    def ids_should_contain_value(self, ids, value):
        """Returns true if value is in the list of ids"""

        value = int(value)
        assert value in ids, "The list does not contain the value %s" % (value)

    def read_record_field_value_from_id(self, model, _id, field_name,
                                        offset=0, limit=None, order=None):
        """Read the value of a field from `model` record `_id`. It returns
        a single value.

        The first argument is the model name (example: ``"res.partner"``)

        The second argument, `_id`, is a single id ``42.``

        The third argument, `field_name`, accepts:
         - a single field: ``'first_name'``
         - a format spec: ``'%(street)s %(city)s'``

        If `fields` is omitted, all fields are read.

        The optional keyword arguments `offset`, `limit` and `order` are
        used to restrict the search.  The `order` is also used to order the
        results returned.
        """

        _id = int(_id)
        return self.client.read(
            model, _id, field_name, offset=offset, limit=limit, order=order)

    def read_record_fields_dictionary_from_id(self, model, _id, field_list,
                                              offset=0, limit=None,
                                              order=None):
        """Read the value of a field from `model` record `_id`. It returns
        a single value.

        The first argument is the model name (example: ``"res.partner"``)

        The second argument, `_id`, is a single id ``42.``

        The third argument, `fields`, accepts:
         - a tuple of fields: ``('street', 'city')``
         - a space separated string: ``'street city'``
         - a format spec: ``'%(street)s %(city)s'``

        If `fields` is omitted, all fields are read.

        The optional keyword arguments `offset`, `limit` and `order` are
        used to restrict the search.  The `order` is also used to order the
        results returned.
        """

        _id = int(_id)
        return self.client.read(
            model, _id, field_list, offset=offset, limit=limit, order=order)

    def field_value_should_be_equal(self, model, ids, field_name, value):
        """The value of field_name for all records of model with id in
        ids should be equal to value."""

        assert isinstance(ids, (list, tuple)), \
            "The argument ids is of type %s. It should be a list type." \
            % (type(ids))
        datas = self.client.read(model, ids, field_name)
        if len(ids) == 1:
            assert datas[0] == value, "Value %s = %s does not match" \
                % (datas[0], value)
        else:
            for d in datas:
                assert d[field_name] == value, "Value %s = %s does not match" \
                    % (d[field_name], value)

    def field_value_should_not_be_equal(self, model, ids, field_name, value):
        """The value of field_name for all records of model with id in
        ids should *NOT* be equal to value."""

        assert isinstance(ids, (list, tuple)), \
            "The argument ids is of type %s. It should be a list type." \
            % (type(ids))
        datas = self.client.read(model, ids, field_name)
        if len(ids) == 1:
            assert datas[0] != value, "Value %s = %s matches" \
                % (datas[0], value)
        else:
            for d in datas:
                assert d.get(field_name) != value, "Value %s = %s matches" \
                    % (d.get(field_name), value)
