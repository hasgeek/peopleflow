var contex = function(options) {
    var users = {};
    var init = function() {
        rfid.on( 'tag_placed', function(data) {
            if (data['tag_id']) {
                if (data['tag_id']) {
                    url = "/event/" + options.eventid + "/participant/"+data['tag_id'];

                    $.getJSON(url, function(user){
                        if(user.error){
                            toastr.error(
                                "This badge is not connected to any user. If you registered and this badge doesn't work, please contact one of the organisers.",
                                "The badge you tapped is not valid."
                            );
                        }
                        else{
                            if( typeof users[user.id] == 'undefined') {
                                users[user.id] = user;
                                toastr.success("", "Added " + user.name + ".");
                            }
                            else {
                                delete(users[user.id]);
                                toastr.success("", "Removed " + user.name + ".");
                            }
                        };
                    });
                }
            }
        });
    };

    init();
    return null;
};