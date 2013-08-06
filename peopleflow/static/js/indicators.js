var indicators = function() {
	var indicators = {};
	var list = {};
	var root = null;
	var prefixed = function(name) {
		return 'indicator_' + name;
	};
	var classes = ['red', 'green', 'yellow'];
	var default_class = 0;

	var init = function() {
		$('body').append('<div id="indicators"></div>');
		root = $('#indicators');
	};

	indicators.add = function(name, indicator, options) {
		list[name] = {};
		var item = list[name];
		root.append('<a id="' + prefixed(name) + '" href="javascript:void(0)">' + indicator + '</a>')
		item.node = root.find('#' + prefixed(name));
		if(typeof options === 'undefined') {
			options = {};
		}
		item.options = options;
		item.node.addClass(classes[default_class]);
	};

	indicators.state = function(name, state) {
		for(i in classes) {
			list[name].node.removeClass(classes[i]);
		}
		list[name].node.addClass(state);
	};

	init();

	return indicators;
}();