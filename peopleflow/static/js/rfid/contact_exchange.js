var timer = function() {
    var timer = {};
    var handler = null;
    var TOTAL_TIME = 20; //Time before the automatic submission happens
    var ALERT_TIME = 10; //Time before the automatic submission, when the timer needs to be shown
    var cooldown = null, timer_content;
    var DEBUG_TOTAL_TIME = 6;
    var DEBUG_ALERT_TIME = 5;

    timer.start = function() {
        timer.reset();
        handler = window.setTimeout(timer.show, (TOTAL_TIME - ALERT_TIME) * 1000);
    };

    timer.reset = function() {
        if(handler) {
            window.clearTimeout(handler);
            handler = null;
        }
        if(cooldown) {
            cooldown.stop();
            timer_content.css({opacity: 0});
        }
    };

    timer.show = function() {
        timer_content.css({opacity: 1});
        cooldown.start(ALERT_TIME);
    };

    timer.init = function(options) {
        if(options.debug && options.ui_test) {
            TOTAL_TIME = DEBUG_TOTAL_TIME;
            ALERT_TIME = DEBUG_ALERT_TIME;
        }
        $('body').append('<div id="cooldown" class="overlay contact_exchange"></div>');
        timer_content = $('#cooldown');
        timer_content.append('<div class="timer"><div class="elem"></div></div>');
        timer_content.find('.timer').append('<div class="seconds">seconds</div>');
        timer_content.find('.timer').append('<div class="message">for automatic <span class="auto_action">cancellation</span></div>');
        timer_content.append('<div class="instructions">The following people will be connected<br>Tap again to add or remove a person</div>');
        cooldown = $('#cooldown .timer .elem').cooldown({
            tickFrequency: 1000,
            arcWidth: 20,
            toFixed: 0,
            introDuration: 0,
            countdownCss: {
                fontSize: '3.5em',
                color: '#FFF',
                fontWeight: 'bolder'
            },
            completeFn: function() {
                userui.exchange();
            }
        });
    };

    timer.update = function() {
        if(userui.len() == 1) {
            timer_content.find('.timer .message .auto_action').html('cancellation');
        }
        else {
            timer_content.find('.timer .message .auto_action').html('submission');
        }
    };

    return timer;
}();

var exchange = function() {
    var exchange = {};
    
    exchange.now = function(users) {
        $.post('contact_exchange', users, function(response) {
            if(response.success) {
                toastr.success('Your contacts have been exchanged');
            }
            else {
                toastr.error('There was an issue submitting your contacts. Please try again.');
            }
            userui.reset();
        }, 'json');
    };

    return exchange;
}();

var userui = function() {
    var ui = {};
    var users, user_matrix, sample;
    var main = $('#contact_exchange');
    var container = $('#contact_exchange .contex_users');
    var len = 0;
    var MAX = {"COLUMNS": 5, "ROWS": 4}; // COLUMNS = ROWS or ROWS + 1
    var last_size = [0,0];
    var options;
    var disabled = false;

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
        var name_array = user.name.split(" ");
        var display_name = name_array[0];
        if(display_name.length <= 2 && typeof name_array[1] != undefined)
            display_name += " " + name_array[1];
        last.find('.name').html(display_name);
        if(user.twitter) {
            last.find('.twitter').html('@' + user.twitter);
        }
        last.addClass('c' + pos[0]);
        last.addClass('r' + pos[1]);

        size = matrix_size();
        w = 100/size[0];
        h = 100/size[1];
        if(w > h) fontfactor = h;
        else fontfactor = w;

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

        last.find('.name').css({"font-size": (fontfactor * 7.2/100) + 'em'});
        last.find('.twitter').css({"font-size": (fontfactor * 6/100) + 'em'});

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
        w = 100/size[0];
        h = 100/size[1];
        if(w > h) fontfactor = h;
        else fontfactor = w;

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

        container.find('.user .name').css({"font-size": (fontfactor * 7.2/100) + 'em'});
        container.find('.user .twitter').css({"font-size": (fontfactor * 6/100) + 'em'});

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
        if(!disabled) {
            timer.start();

            if( typeof users[user.id] == 'undefined') {
                if(add(user)) toastr.success("", "Added " + user.name + ".");
                else toastr.warning("Upto " + (MAX.COLUMNS * MAX.ROWS) + " members can be connected only.", "Limit reached");
            }
            else {
                remove(user.id);
                toastr.success("", "Removed " + user.name + ".");
            }
            timer.update();
        }
    }

    ui.reset = function() {
        if(typeof user_matrix != 'undefined') {
            for(i = 0; i < user_matrix.length; i++) {
                for(j = 0; j< user_matrix[i].length; j++) {
                    remove(user_matrix[i][j].id);
                }
            }
        }
        users = {};
        user_matrix = [[],[],[],[],[]];
        timer.reset();
        ui.enable();
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

    ui.disable = function() {
        disabled = true;
    };

    ui.enable = function() {
        disabled = false;
    };

    ui.exchange = function() {
        if(len == 1) {
            ui.reset()
        }
        else {
            ui.disable();
            var user_list = {'ids': []};
            for(i = 0; i < user_matrix.length; i++) {
                for(j = 0; j < user_matrix[i].length; j++) {
                    user_list.ids.push(user_matrix[i][j].nfc_id);
                }
            }
            exchange.now(user_list);
        }
    };

    ui.len = function() {
        return len;
    };

    return ui;
}();

var contex = function(options) {
    var init = function() {
        userui.init(options);
        timer.init(options);
        if(options.debug) {
            toastr.warning("The application is running in debug mode. You can tap the same badge to add multiple cards. To remove a card, just click the card. In debug mode, some options like timer duration are optimised for smoother testing.");
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