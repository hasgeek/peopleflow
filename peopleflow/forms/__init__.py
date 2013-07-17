from .event import *
from .participant import *
from .kiosk import *

import flask.ext.wtf as wtf

class ConfirmSignoutForm(Form):
    """
    Confirm a delete operation
    """
    # The labels on these widgets are not used. See delete.html.
    delete = wtf.SubmitField(u"Sign out")
    cancel = wtf.SubmitField(u"Cancel")