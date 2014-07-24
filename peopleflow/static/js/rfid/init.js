var rfid = function() {
    var rfid_obj = {
        'init': function() {
            for( var action_name in this.indicator ) {
                this.actions[action_name] = [];
                this.actions[action_name].push( function(data) {
                    rfid_obj.indicator[action_name](data);
                });
            }
            $(window).on('rfid:action', function(e, data) {
                if( typeof rfid_obj.indicator[data.action] == 'function' ) {
                    var actions = rfid_obj.actions[data.action];
                    for( var action in actions ) {
                        if( typeof actions[action] == 'function' ) {
                            actions[action](data);
                        }
                    }
                }
            });

            $(window).on('rfid:server_inactive', function(e, data) {
                indicators.state('rfid_status', 'black');
            });
            $(window).on('rfid:server_active', function(e, data) {
                indicators.state('rfid_status', 'yellow');
            });
            indicators.add('rfid_status', '&FilledSmallSquare;');
        },
        'actions': {},
        'indicator': {
            'tag_placed': function(data) {
                indicators.state('rfid_status', 'green');
            },
            'tag_removed': function(data) {
                indicators.state('rfid_status', 'yellow');
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