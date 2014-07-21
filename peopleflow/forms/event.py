# -*- coding: utf-8 -*-

import wtforms
import wtforms.fields.html5
import simplejson as json
from baseframe.forms import Form

def set_none(self, field):
    if not field.data:
        field.data = None

def set_integer_or_none(self, field):
    if field.data == "":
        field.data = None
    else:
        field.data = int(field.data)

class BadgeOptions(wtforms.Form):
    name_color = wtforms.TextField('Name Color', validators=[wtforms.validators.Length(max=7)])
    hr_color = wtforms.TextField('Horizonal Rule Color', validators=[wtforms.validators.Length(max=7)])
    company_color = wtforms.TextField('Company & Job Color', validators=[wtforms.validators.Length(max=7)])
    twitter_color = wtforms.TextField('Twitter Color', validators=[wtforms.validators.Length(max=7)])
    topMargin = wtforms.TextField('Top Margin(in mm)')
    leftMargin = wtforms.TextField('Left Margin(in mm)')
    rightMargin = wtforms.TextField('Right Margin(in mm)')
    bottomMargin = wtforms.TextField('Bottom Margin(in mm)')
    validate_name_color = set_none
    validate_company_color = set_none
    validate_twitter_color = set_none
    validate_topMargin = set_integer_or_none
    validate_leftMargin = set_integer_or_none
    validate_rightMargin = set_integer_or_none
    validate_bottomMargin = set_integer_or_none

class Options(BadgeOptions):
    nfc = wtforms.BooleanField('Use NFC')
    template_color1 = wtforms.TextField('Template Color 1', validators=[wtforms.validators.Length(max=7)])
    template_color2 = wtforms.TextField('Template Color 2', validators=[wtforms.validators.Length(max=7)])
    template_color3 = wtforms.TextField('Template Color 3', validators=[wtforms.validators.Length(max=7)])
    validate_template_color_1 = set_none
    validate_template_color_2 = set_none
    validate_template_color_3 = set_none

class LabelMixin:
    label = wtforms.TextField('Label')
    validate_label = set_none

class CrewOptions(BadgeOptions, LabelMixin):
    pass

class SpeakerOptions(BadgeOptions, LabelMixin):
    pass

class EventDataForm():
    title = wtforms.TextField('Title', validators=[wtforms.validators.Required('A title is required')])
    name = wtforms.TextField('Name', validators=[wtforms.validators.Required('A name is required')])
    from_date = wtforms.DateField('From', description="Format: YYYY-MM-DD", validators=[wtforms.validators.Required('Propose a from date')])
    to_date = wtforms.DateField('To', description="Format: YYYY-MM-DD", validators=[wtforms.validators.Required('Propose a to date')])
    funnel_space = wtforms.TextField('Funnel Proposal Space')
    eventframe_sync = wtforms.TextField('Eventframe RSVP JSON URL')
    doattend_id = wtforms.TextField('Doattend Event ID')
    print_type = wtforms.fields.SelectField('Print Type', choices=[(u'badge', 'Badge'), (u'floppy', 'Floppy Stickers'), (u'label', 'Label')], default=u"badge")

class EventLogoForm(Form):
    event_logo = wtforms.TextField('Event Logo', description="Provide the URL for the image for the event logo.", validators=[wtforms.validators.Optional(), wtforms.validators.URL(message="Please provide a valid URL")])

class WelcomeLogoForm(Form):
    welcome_logo = wtforms.TextField('Welcome Screen Sponsor Logo', description="Provide the URL for the image for the logo of the welcome screen sponsor.", validators=[wtforms.validators.Optional(), wtforms.validators.URL(message="Please provide a valid URL")])

class EventOptionsForm():
    options = wtforms.fields.FormField(Options)
    speaker_options = wtforms.fields.FormField(SpeakerOptions)
    crew_options = wtforms.fields.FormField(CrewOptions)

class NewEventForm(EventDataForm, EventLogoForm, WelcomeLogoForm, EventOptionsForm, Form):
    pass

class EditEventForm(EventDataForm, EventOptionsForm, Form):
    pass

class EventSyncForm(Form):
    lastuser_username = wtforms.TextField('LastUser Username')
    lastuser_password = wtforms.PasswordField('LastUser Password')

    def validate_funnel_password(self, field):
        if self.funnel_username.data != "" and field.data == "":
            raise wtforms.ValidationError("If you enter the username, you have to enter the password")
