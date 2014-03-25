from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from importlib import import_module

try:
    from django.db.transaction import atomic
except ImportError:
    from django.db.transaction import commit_on_success as atomic

class Command(BaseCommand):
	help = 'Loads the named fixtures, or the default for each installed app.'
	args = "[fixture ...]"

	@atomic
	def handle(self, *fixtures, **options):
		verbosity = int(options.get('verbosity', 1))
		delayed = {}
		loaded = set()

		# Use installed app labels as fixtures if none are given.
		if not fixtures:
			fixtures = [get_app_label(app) for app in settings.INSTALLED_APPS]

		for app_module in settings.INSTALLED_APPS:
			app_label = get_app_label(app_module)

			# Continue if app has no fixtures.
			try:
				orm_fixtures = import_module('%s.orm_fixtures' % app_module)
			except ImportError:
				continue

			for fixture in fixtures:
				if '.' in fixture:
					label, fixture = fixture.split('.')

					# Continue if app label doesn't match this app.
					if label != app_label:
						continue

				func = getattr(orm_fixtures, fixture, None)

				# Continue if `func` isn't callable, is private, or is defined
				# in a module other than `orm_fixtures`.
				if not callable(func) or func.__name__.startswith('_') or \
						func.__module__ != orm_fixtures.__name__:
					continue

				# Ensure fixture has a list of requirements, even if empty.
				if not hasattr(func, 'requires'):
					func._requires = []

				# Get full fixture name.
				fixture = '%s.%s' % (app_label, fixture)

				if loaded.issuperset(func._requires):
					# Execute if required fixtures are loaded.
					load(fixture, func, verbosity)
					loaded.add(fixture)
				else:
					# Delay if required fixtures are not loaded.
					delayed[fixture] = func

		# Execute delayed fixtures.
		while delayed:
			circular = True
			for fixture, func in delayed.items():
				if loaded.issuperset(func._requires):
					load(fixture, func, verbosity)
					loaded.add(fixture)
					circular = False
					delayed.pop(fixture)

			# Exit loop if circular requirement exists.
			if circular:
				raise CommandError(
					'Circular ORM fixture requirements: %s' %
						', '.join(delayed))

def get_app_label(app_module):
	return app_module.split('.')[-1]

def load(fixture, func, verbosity):
	if verbosity:
		print 'Loading ORM fixture: %s' % fixture
	func(verbosity)
