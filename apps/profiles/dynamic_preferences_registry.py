from dynamic_preferences.types import BooleanPreference, StringPreference, DateTimePreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry

import datetime

fair = Section('fair')

@global_preferences_registry.register
class ApplicationsOpen(DateTimePreference):
    section = fair
    name = 'applications_open_date'
    default = datetime.datetime(2020, 1, 14)
    verbose_name = 'Date when company applications open'
    help_text = 'When the application process is open to companies.'
