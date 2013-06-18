var rfid = function() {
    var rfid_obj = {
        'init': function() {
            for( action_name in this.indicator ) {
                this.actions[action_name] = [];
                this.actions[action_name].push( function(data) {
                    rfid_obj.indicator[action_name](data);
                });
            }
            $(window).on('rfid:action', function(e, data) {
                if( typeof rfid_obj.indicator[data.action] == 'function' ) {
                    var actions = rfid_obj.actions[data.action];
                    for( action in actions ) {
                        if( typeof actions[action] == 'function' ) {
                            actions[action](data);
                        }
                    }
                }
            });

            $(window).on('rfid:server_inactive', function(e, data) {
                $('#rfid_status').removeClass('server_active');
            });
            $(window).on('rfid:server_active', function(e, data) {
                $('#rfid_status').addClass('server_active');
            });
            $('body').append('<a id="rfid_status" href="javascript:void(0)">&bull;</a>');
        },
        'actions': {},
        'indicator': {
            'tag_placed': function(data) {
                $('#rfid_obj_status').addClass('tag_placed');
            },
            'tag_removed': function(data) {
                $('#rfid_obj_status').removeClass('tag_placed');
            }
        },
        'on': function(action_name, fn) {
            if( typeof rfid_obj.indicator[action_name] == 'function' && typeof fn == 'function' ) {
                rfid_obj.actions[action_name].push(fn);
                return true;
            }
            else return false;
        }
    };
    rfid_obj.init();
    return {on: rfid_obj.on};
}();