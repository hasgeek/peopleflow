Hello,

This email brings you the contact information of people you met at {{ event.title }}, {{ event.from_date.year }}.
Hope you had a good time!

Given below is a list of your fellow participants:
{% for user in users %}
* {{ user.name }}{% if user.company %} - {{ user.company }}{% endif %} [e-mail](mailto:{{ user.email }}){% if user.twitter %} [@{{ user.twitter }} on twitter](https://twitter.com/{{ user.twitter }}){% endif %}{% endfor %}

All of the above are marked on this email, so you can continue with your conversation(s) on this thread!

You can also use the attached contact cards to store the contact details in your address books.

ContactExchange is a HasGeek service. Please do write to us at info@hasgeek.com if you have suggestions or questions on this service.

Regards,  
The non-sentient HasGeek email robot