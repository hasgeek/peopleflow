from functools import wraps
from flask import url_for

class NavNode():
	url = ""
	title = ""
	parent = None
	objects = []
	urlvars = {}
	objectkeys = []
	titlefunc = None
	urlvarsfunc = None

	def __init__(self, fname, options):
		self.fname = fname
		for option, value in enumerate(options):
			try:
				if isinstance(options['title'], str):
					self.title = options['title']
				else:
					self.titlefunc = options['title']
			except (KeyError):
				pass
			
			self.parent = options['parent']

			try:
				if isinstance(options['urlvars'], dict):
					self.urlvars = options['urlvars']
				else:
					self.urlvarsfunc = options['urlvars']
			except (KeyError):
				pass

			if 'objects' in options:
				self.objectkeys = options['objects']

	def update(self, **dataobjects):
		for key in self.objectkeys:
			if key in dataobjects:
				self.objects.append(dataobjects[key])
		if self.titlefunc:
			self.title = self.titlefunc(dataobjects)
		if self.urlvarsfunc:
			self.urlvars = self.urlvarsfunc(dataobjects)
		self.url = url_for(self.fname, **self.urlvars)


class Nav():

	nodes = {}
	current_node = None

	def init(self, **options):
		def inner(f):
			self.nodes[f.__name__] = NavNode(f.__name__, options)
			@wraps(f)
			def add_parent_dec(*a, **kw):
				self.current_node = f.__name__
				self.make_trail(f.__name__)
				for node in self.trail:
					node.update(**kw)
				return f(*a, **kw)
			return add_parent_dec
		return inner

	def make_trail(self, node):
		self.trail = []
		while node is not None:
			self.trail.insert(0, self.nodes[node])
			node = self.nodes[node].parent

	def init_app(self, app):
		app.jinja_env.globals['nav'] = self

	def get_trail():
		pass