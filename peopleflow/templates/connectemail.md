Hello from {{ event.title }},

Hope you had a good time! Here are your new friends:

{% for user in users %}
* {{ user.name }}{% if user.company %}, {{ user.company }}{% endif %}, [{{ user.email }}](mailto:{{ user.email }}){% if user.twitter %}, [@{{ user.twitter }}](https://twitter.com/{{ user.twitter }}){% endif %}{% endfor %}

To continue your conversation, reply to all (and remove us!).

ContactExchange is a service from HasGeek. Got questions? We are at info@hasgeek.com.

Regards,  
The non-sentient HasGeek email robot
