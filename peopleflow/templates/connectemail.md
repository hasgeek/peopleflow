Hello {{ name }},

This email brings you the contact information of people you met at {{ event.title }}.
Hope you had a good time!

{% for p in participants %}
		Name: {{ p.name }}
		Company: {{ p.company }}
		Twitter: {{ p.twitter }}

{% endfor %}

ContactPoint is a HasGeek service. Write to us at info@hasgeek.in if you have suggestions or questions on this service.

Regards  
The non-sentient HasGeek email robot
