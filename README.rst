Overview
========

It can often be more convenient to use the ORM's ``get_or_create`` and
``update_or_create`` methods to load data than traditional fixtures, which
include hard coded primary keys or require models that support natural keys, and
don't support dynamic or conditional data.

This app provides a management command that loads the named "ORM fixtures" for
each installed app. If no fixtures are named, the labels for all installed apps
will be used as a default.

You can take advantage of that fact to conditionally load data for one app, only
when another app is installed.


Installation
============

Just add ``orm_fixtures`` to your `INSTALLED_APPS` setting, define your fixtures
and run the ``orm_fixtures`` management command.


Fixture definition
==================

An ORM fixture is just a function located in the ``orm_fixtures`` module of an
installed app.

Fixture function signatures should accept ``**kwargs``, as the arguments sent to
fixtures might change in the future. At the moment, the only argument that gets
passed is ``verbosity``, with a default value of ``1``.

Use the ``require_fixtures`` decorator to ensure that one fixture is loaded
before another::

	from __future__ import absolute_import
	from orm_fixtures.decorators import require_fixtures

	@require_fixtures('app.foo', 'app.bar')
	def myapp(**kwargs):
		pass

If you want a fixture to load automatically when the ``orm_fixtures`` management
command is run, give it the same name as an installed app label.


Usage
=====

Load all fixtures with a name matching any installed app::

	./manage.py orm_fixtures

Load all fixtures named ``initial_data``::

	./manage.py orm_fixtures initial_data

Load all fixtures named ``initial_data`` and the ``test_data`` fixture for the
``foo`` app::

	./manage.py orm_fixtures initial_data foo.test_data

