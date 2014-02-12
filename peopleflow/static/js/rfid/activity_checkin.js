rfid.on('tag_placed', function(data){
	var messaging = $('#messaging');
	if(data['tag_id']) {
		$.post('checkin', {nfc_id: data['tag_id'], activity_id: $('#activity_id').val()}, function(response){
			if(response.status) {
				messaging.find('.purchase_list').html(response['purchases']);
				messaging.find('.purchases').show();
			}
			else messaging.find('.purchases').hide();
			messaging.find('.message').html(response['msg']);
			$('#messaging').fadeIn(1000, function() {
				window.setTimeout(function() {console.log('Hello!');$('#messaging').fadeOut(1000);}, 3000);
			});
		});
	}
});