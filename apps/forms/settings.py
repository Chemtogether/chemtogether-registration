from __future__ import unicode_literals

from django.conf import settings

# The maximum allowed length for field values.
FIELD_MAX_LENGTH = 10000

# The maximum allowed length for field labels.
LABEL_MAX_LENGTH = 200

# The absolute path where files will be uploaded to.
UPLOAD_ROOT = None

# Boolean controlling whether HTML5 form fields are used.
USE_HTML5 = True

# Char to start a quoted choice with.
CHOICES_QUOTE = '"'

# Char to end a quoted choice with.
CHOICES_UNQUOTE = '"'

# Char to use as a field delimiter when exporting form responses as CSV.
CSV_DELIMITER = ","

# The maximum allowed length for field help text
HELPTEXT_MAX_LENGTH = 300

# The maximum allowed length for field choices
CHOICES_MAX_LENGTH = 1000
