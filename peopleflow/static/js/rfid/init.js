var rfid = {
    'init': function() {
        for( action_name in this.indicator ) {
            rfid[action_name] = function(data) {
                this.action(action_name, data);
            };
        }
        $(window).on('rfid:action', function(e, data) {
            if( typeof rfid[data.action] == 'function' ) rfid[data.action](data);
        });

        $(window).on('rfid:server_inactive', function(e, data) {
            $('#rfid_status').removeClass('server_active');
        });
        $(window).on('rfid:server_active', function(e, data) {
            $('#rfid_status').addClass('server_active');
        });
        $('body').append('<a id="rfid_status" href="javascript:void(0)">&bull;</a>');
    },
    'action': function(action, data) {
        if( typeof this.indicator[action] == 'function' ) {
            this.indicator[action](data);
        }
    },
    'indicator': {
        'tag_placed': function(data) {
            $('#rfid_status').addClass('tag_placed');
        },
        'tag_removed': function(data) {
            $('#rfid_status').removeClass('tag_placed');
        }
    }
};
rfid.init();