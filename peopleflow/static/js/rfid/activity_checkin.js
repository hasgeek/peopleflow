rfid.on('tag_placed', function(data){
	var messaging = $('#messaging');
	if(data['tag_id']) {
		$.post('checkin', {nfc_id: data['tag_id'], activity_id: $('#activity_id').val()}, function(response){
			messaging.find('.image img').attr('src', null);
			messaging.removeClass('has_image');
			if(response.status) {
				messaging.find('.message').removeClass('error');
				if(response.already) messaging.find('.message').addClass('already');
				else messaging.find('.message').removeClass('already');
				if(response.image) {
					messaging.find('.image img').attr('src', response.image);
					messaging.addClass('has_image');
				}
				messaging.find('.purchase_list').html(response['purchases']);
				messaging.find('.purchases').show();
			}
			else {
				messaging.find('.message').removeClass('already').addClass('error');
				messaging.find('.purchases').hide();
			}
			messaging.find('.message').html(response['msg']);
			messaging.fadeIn(1000, function() {
				window.setTimeout(function() {messaging.fadeOut(1000);}, 3000);
			});
		});
	}
});

function loop_in() {
	$('.top .welcome').toggle('slide', {direction: 'up'}, 1000);
	$('.top .event').toggle('slide', {direction: 'up'}, 2000);
	$('.top .activity').toggle('slide', {direction: 'left'}, 4000);
	$('.top .venue').toggle('slide', {direction: 'right'}, 4000, function() {
		$('.bottom').toggle('slide', {direction: 'down'}, 1500);
		window.setTimeout(loop_out, 15000)
	});
}

function loop_out() {
	$('.top .welcome').toggle('slide', {direction: 'left'}, 250);
	$('.top .event').toggle('slide', {direction: 'right'}, 500);
	$('.top .activity').toggle('slide', {direction: 'left'}, 1000);
	$('.top .venue').toggle('slide', {direction: 'right'}, 1000);
	$('.bottom').toggle('slide', {direction: 'down'}, 1500, function() {
		window.setTimeout(loop_in, 1000);
	});
}

loop_out();