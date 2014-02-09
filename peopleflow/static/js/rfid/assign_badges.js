var MESSAGE_TIME = 5000;
var messaging_handler = null;

var stats = function() {
	var stats = {};
	var url = null;
	var counters = $('#badge_counters');
	var messaging = $('#messaging');
	var refresh_time;
	var counts;

	update_counters = function() {
		for(i in counts){
			counters.find('#' + i + ' .counter').html(counts[i]);
		}
	}

	stats.message_determine = function() {
		if(counts.unassigned > 0) {
			messaging.addClass('tap').removeClass('none').removeClass('response');
		}
		else {
			messaging.removeClass('tap').addClass('none').removeClass('response');
		}
	}

	stats.refresh = function() {
		$.get(url, {type: $('#badge_type').val()}, function(data){
			counts = data;
			update_counters();
			if(!messaging_handler) {
				stats.message_determine();
			}
		});
	};

	stats.init = function(stats_url, ref_time) {
		if(typeof stats_url == "undefined") {
			console.log('No URL provided');
			return false;
		}
		url = stats_url;
		if(typeof ref_time == "undefined") {
			refresh_time = 1000;
		}
		else {
			refresh_time = ref_time;
		}
		window.setInterval(stats.refresh, refresh_time);
	};

	return stats;
}();

rfid.on('tag_placed', function(data){
	var messaging = $('#messaging');
	if(data['tag_id']) {
		$.post('assign_badges', {nfc_id: data['tag_id'], type: $('#badge_type').val()}, function(response){
			if(messaging_handler) {
				window.clearTimeout(messaging_handler);
			}
			messaging.removeClass('tap').removeClass('none').addClass('response');
			$('#response').html(response.message);
			messaging_handler = window.setTimeout('stats.message_determine()', MESSAGE_TIME);
		});
	}
});