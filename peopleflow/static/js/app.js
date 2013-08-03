(function(){
	indicators.add('server_connectivity', '&rlhar;');
	var test_connection = function(){
		$.ajax({
			url: '/ping',
			timeout: 5000,
			success: function() {
				indicators.state('server_connectivity', 'green');
			},
			error: function() {
				indicators.state('server_connectivity', 'red');
			}
		});
	};
	test_connection();
	window.setInterval(test_connection, 10000);
}());