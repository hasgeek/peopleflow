from .event import *
from .participant import *
from .kiosk import *
from .venue import *
from .activity import *
from .product import *
from .ticket import *

import wtforms
import wtforms.fields.html5

class ConfirmSignoutForm(Form):
    """
    Confirm a delete operation
    """
    # The labels on these widgets are not used. See delete.html.
    delete = wtforms.SubmitField(u"Sign out")
    cancel = wtforms.SubmitField(u"Cancel")