
var userui = function() {
    var ui = {};
    var users, user_matrix, sample;
    var main = $('#contact_exchange');
    var container = $('#contact_exchange .contex_users');
    var len = 0;
    var MAX = {"COLUMNS": 5, "ROWS": 4}; // COLUMNS = ROWS or ROWS + 1
    var last_size = [0,0];
    var options;

    var add = function(user) {
        // Function to add a user card to the UI

        var pos = allocate();
        if(!pos) return false;
        users[user.id] = pos;

        w = Math.round(10000/(pos[0] + 1))/100;
        h = Math.round(10000/(pos[1] + 1))/100;
        len++;

        container.append(sample);
        var last = container.children('.user:last-child');
        user.node = last;
        user_matrix[pos[0]][pos[1]] = user;
        last.attr('id', 'user_' + user.id);
        last.find('.name').html(user.name);
        if(user.twitter) {
            last.find('.twitter').html(user.twitter);
        }
        last.addClass('c' + pos[0]);
        last.addClass('r' + pos[1]);

        size = matrix_size();
        w = Math.round(10000/size[0])/100;
        h = Math.round(10000/size[1])/100;

        if(options.debug) {
            last.on('click', function(){
                ui.process(user);
            });
        }

        last.css({
            'left': (pos[0] * w + 1) + '%',
            'width': (w - 1.5) + '%',
            'top': (pos[1] * h + 1) + '%',
            'height': (h - 5) + '%'
        });

        resize(last);

        return true;
    };

    var resize = function(last) {
        var showing = false;
        var show_last = function() {
            if(last && !showing) {
                showing = true;
                last.animate({opacity: 1}, 500);
            }
        };
        size = matrix_size();
        w = Math.round(10000/size[0])/100;
        h = Math.round(10000/size[1])/100;
        if(len == 0) main.removeClass('users');
        else if(len == 1) main.addClass('users');
        if(size[1]) main.addClass('rows' + size[1]);
        if(last_size[1] && size[1] != last_size[1]) main.removeClass('rows' + last_size[1]);
        
        if(size[0] != last_size[0] && len != 1) {
            for(c = 0; c < size[0]; c++) {
                container.find('.c' + c).animate({
                    'left': (c * w + 1) + '%',
                    'width': (w - 1.5) + '%'
                }, 800, show_last);
            }
        }
        if(size[1] != last_size[1] && len != 1) {
            for(r = 0; r < size[1]; r++) {
                container.find('.r' + r).animate({
                    'top': (r * h + 1) + '%',
                    'height': (h - 5) + '%'
                }, 800, show_last);
            }
        }

        if((size[0] == last_size[0] && size[1] == last_size[1]) || len ==1) {
            show_last();
        }
        last_size = size;
    };

    var allocate = function(c, r) {
        if(typeof c == 'undefined') c = 0;
        if(typeof r == 'undefined') r = 0;
        if(c > r) {
            for(i = 0; i <= r; i++) {
                if(typeof user_matrix[c][i] == 'undefined') return [c,i];
            }
            if(r+1 >= MAX.ROWS) return false;
            return allocate(c, r+1);
        }
        else {
            for(i = 0; i <= c; i++) {
                if(typeof user_matrix[i][r] == 'undefined') return [i,r];
            }
            if(c+1 >= MAX.COLUMNS) return false;
            return allocate(c+1, r);
        }
    };

    var matrix_size = function() {
        var c = null, r = 0;
        for(i = MAX.COLUMNS - 1; i >= 0; i--){
            for(j = MAX.ROWS - 1; j >= 0 && typeof user_matrix[i][j] == 'undefined'; j--) continue;
            if(c == null && j+1 != 0) c = i;
            if(j+1 > r) r = j+1;
        }
        r = r;
        return [c+1, r];
    };

    var clean_matrix = function() {
        var lens = [], empty = 0;

        // Eliminate empty columns
        for(i = 0; i < MAX.COLUMNS; i++) {
            for(j = MAX.ROWS - 1; j >= 0 && typeof user_matrix[i][j] == 'undefined'; j--) continue;
            lens[i] = j+1;
            if(!lens[i]) empty++;
        }
        for(last_non_empty = MAX.COLUMNS; last_non_empty >=0 && !lens[last_non_empty]; last_non_empty--) continue;
        for(i = 0; i < MAX.COLUMNS; i++) {
            if(!lens[i]) {
                for(j = i; j < MAX.COLUMNS; j++) {
                    user_matrix[j] = user_matrix[j+1];
                    lens[j] = lens[j+1];
                    for(k = 0; k < lens[j]; k++) {
                        if(typeof user_matrix[j][k] != "undefined") {
                            node = user_matrix[j][k].node;
                            users[user_matrix[j][k].id] = [j,k];
                            node.removeClass('c' + (j+1));
                            node.addClass('c' + j);
                        }
                    }
                }

            }
            if(i > MAX.COLUMNS - empty - 1) {
                lens[i] = 0;
                user_matrix[i] =[];
            }
        }

        // Eliminate empty rows
        for(i = 0; i < MAX.ROWS - 1; i++) {
            is_empty = true;
            for(j = 0; j < MAX.COLUMNS; j++) is_empty = (is_empty && typeof user_matrix[j][i] == 'undefined');
            
            if(is_empty) {
                for(j = 0; j < MAX.COLUMNS - 1; j++) {
                    if(typeof user_matrix[j][i+1] != 'undefined') {
                        user_matrix[j][i] = user_matrix[j][i+1];
                        user_matrix[j][i+1] = undefined;
                        node = user_matrix[j][i].node;
                        users[user_matrix[j][i].id] = [j,i];
                        node.removeClass('r' + (i+1));
                        node.addClass('r' + i);
                    }
                }
            }
        }
    };

    var remove = function(user_id) {
        var pos = users[user_id];
        var target =$('#user_' + user_id);
        delete(user_matrix[pos[0]][pos[1]]);
        delete(users[user_id]);
        len--;
        target.animate({opacity: 0}, 500, function() {
            target.remove();
            clean_matrix();
            resize(null);
        });
    };

    ui.process = function(user) {
        if( typeof users[user.id] == 'undefined') {
            if(add(user)) toastr.success("", "Added " + user.name + ".");
            else toastr.warning("Upto " + (MAX.COLUMNS * MAX.ROWS) + " members can be connected only.", "Limit reached");
        }
        else {
            remove(user.id);
            toastr.success("", "Removed " + user.name + ".");
        }
    }

    ui.reset = function() {
        users = {};
        user_matrix = [[],[],[],[],[]];
    }

    ui.init = function(opts) {
        options = opts;
        if(MAX.COLUMNS != MAX.ROWS && MAX.COLUMNS != MAX.ROWS + 1){
            console.log("MAX.COLUMNS should be = either MAX.ROWS or MAX.ROWS + 1");
        }
        ui.reset();
        sample = $('#contex_user_sample').html();
        $('#contex_user_sample').remove();
    };

    return ui;
}();

var contex = function(options) {
    var init = function() {
        userui.init(options);
        if(options.debug) {
            toastr.warning("The application is running in debug mode. You can tap the same badge to add multiple people. To remove a person, just click his card in the UI.");
        }
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
                            if(options.debug) {
                                user.id = Math.floor((Math.random()*10000)+1);
                            }
                            userui.process(user);
                        };
                    });
                }
            }
        });
    };

    init();
    return null;
};