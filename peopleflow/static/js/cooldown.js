;(function($) {
  var defaults = {
    tickFrequency: 50,
    arcWidth: 10,
    arcColor: "#27ae60",
    arcBackgroundColor: "#d7d8d9",
    toFixed: 1,
    introDuration: 500,
    countdownCss: {
      width: "100%",
      height: "100%",
      margin: 0,
      padding: 0,
      textAlign: "center",
      fontSize: "16px"
    },
    countdownFn: null,
    completeFn: null
  };
  var STATE = {
    PLAYING: "playing",
    PAUSED: "paused",
    STOPPED: "stopped"
  };
  var SVG_SUPPORT = false;
  try {
    // For some reason the svg animation only works in Chrome
    // TODO: Consider using canvas for everything
    if (navigator.userAgent.toLowerCase().indexOf("chrome") > -1) {
      SVG_SUPPORT = true;
    }
  } catch (e) {}

  $.fn.cooldown = function(options) {
    if (this.length > 1) {
      var elements = [];
      for (var i = 0; i < this.length; i++) {
        elements.push(this.eq(i).cooldown(options));
      }
      return elements;
    }

    var _this = this;
    $.extend(true, this, {
      // Private methods, chainable
      _init: function() {
        // TODO: Validate options
        this.sideLength = Math.min(this.width(), this.height());

        return this;
      },
      _tick: function() {
        // Note: This will fail during DST and other freak of nature time rewinds
        this.remainingTime = this.duration * (1 - this.buffer) - (new Date() - this.timePing) / 1000;
        if (this.remainingTime <= 0) {
          this.state = STATE.STOPPED;
          clearInterval(this.interval);
          this.remainingTime = 0;
          if (this.completeFn) {
            this.completeFn();
          }
        }
        this.remainingTimeElement.html(this.countdownFn ?
            this.countdownFn(this.remainingTime) : this.remainingTime.toFixed(this.toFixed));

        if (!SVG_SUPPORT) {
          var angle = Math.PI / -2 + (1 - this.remainingTime / this.duration) * 2 * Math.PI;
          var arcDescription = [this.sideLength / 2, this.sideLength / 2,
              this.sideLength / 2 - this.arcWidth / 2];

          this.canvasElement.width = this.canvasElement.width;
          this.context.lineWidth = this.arcWidth;
          this.context.strokeStyle = this.arcColor;
          this.context.beginPath();
          this.context.arc.apply(this.context, arcDescription.concat([Math.PI / -2, angle]));
          this.context.stroke();
          this.context.strokeStyle = this.arcBackgroundColor;
          this.context.beginPath();
          this.context.arc.apply(this.context, arcDescription.concat([angle, Math.PI * 3 / 2]));
          this.context.stroke();
        }

        return this;
      },
      _setActive: function(active) {
        if (active) {
          this.interval = setInterval(function() {
            _this._tick.apply(_this);
          }, this.tickFrequency);
          if (this.svgElement) {
            this.svgElement.unpauseAnimations();
          }
        } else {
          clearInterval(this.interval);
          if (this.svgElement) {
            this.svgElement.pauseAnimations();
          }
        }

        return this;
      },
      // Public methods, not chainable
      start: function(duration) {
        this.stop();
        this.duration = this.remainingTime = duration;
        this.buffer = 0;

        if (!(typeof this.duration === "number" && this.duration >= 0)) {
          throw new SyntaxError("Invalid [duration]");
        }

        if (SVG_SUPPORT) {
          var radius = this.sideLength / 2 - this.arcWidth / 2;
          var pathDescription = ["M", this.sideLength / 2, this.arcWidth / 2,
              "a", radius, radius, 0, 1, 0, 0.01, 0].join(" ");
          var circumference = Math.ceil(Math.PI * (this.sideLength - this.arcWidth));

          this.html([
            "<svg style='position: absolute; top: 0; left: 0;'",
                "width='", this.sideLength, "' height='", this.sideLength, "'>",
              "<path fill='none' stroke-dashoffset='", circumference, "' ",
                  "stroke-dasharray='", circumference, "' ",
                  "stroke='", this.arcBackgroundColor, "' ",
                  "stroke-width='", this.arcWidth, "' ",
                  "d='", pathDescription, "'>",
                "<animate attributeName='stroke-dashoffset' from='", -circumference, "' to='0' ",
                    "dur='", this.introDuration / 1000, "' />",
                "<animate attributeName='stroke-dashoffset' from='0' to='", circumference, "' ",
                    "begin='", this.introDuration / 1000, "' dur='", this.duration, "' />",
              "</path>",
              "<path fill='none' stroke-opacity='0' ",
                  "stroke-dasharray='", circumference, "' ",
                  "stroke='", this.arcColor, "' ",
                  "stroke-width='", this.arcWidth, "' ",
                  "d='", pathDescription, "'>",
                "<animate attributeName='stroke-dashoffset' from='", -circumference, "' to='0' ",
                    "begin='", this.introDuration / 1000, "' dur='", this.duration, "' />",
                "<animate attributeName='stroke-opacity' from='1' to='1' ",
                    "begin='", this.introDuration / 1000, "' dur='indefinite' />",
              "</path>",
            "</svg>"
          ].join(""));
          this.svgElement = this.find("svg")[0];
        } else {
          this.html([
            "<canvas style='position: absolute; top: 0; left: 0;' ",
                "width='", this.sideLength, "' height='", this.sideLength, "'></canvas>"
          ].join(""));
          this.canvasElement = this.find("canvas")[0];
          this.context = this.canvasElement.getContext("2d");

          var introTimePing = new Date();
          var introInterval = setInterval(function() {
            var progress = (new Date() - introTimePing) / _this.introDuration;
            if (progress > 1) {
              clearInterval(introInterval);
              return;
            }
            _this.canvasElement.width = _this.canvasElement.width;
            _this.context.lineWidth = _this.arcWidth;
            _this.context.strokeStyle = _this.arcBackgroundColor;
            _this.context.beginPath();
            _this.context.arc(_this.sideLength / 2, _this.sideLength / 2,
                _this.sideLength / 2 - _this.arcWidth / 2, Math.PI / -2, Math.PI / -2 + 2 * Math.PI * progress);
            _this.context.stroke();
          }, this.tickFrequency);
        }

        this.css("position", "relative").append([
          "<div class='remaining-time' style='line-height: ", this.sideLength, "px;'></div>"
        ].join(""));
        this.remainingTimeElement = this.find(".remaining-time").css(this.countdownCss);

        setTimeout(function() {
          _this.state = STATE.PAUSED;
          _this.remainingTimeElement.html(_this.duration.toFixed(_this.toFixed));
          _this.resume.apply(_this);
        }, this.introDuration);
      },
      stop: function() {
        this.state = STATE.STOPPED;
        this._setActive(false).empty();
      },
      pause: function() {
        if (this.state !== STATE.PLAYING) {
          return;
        }
        this.state = STATE.PAUSED;
        this._setActive(false)._tick();
        this.buffer = 1 - this.remainingTime / this.duration;
      },
      resume: function() {
        if (this.state !== STATE.PAUSED) {
          return;
        }
        this.state = STATE.PLAYING;
        this.timePing = new Date();
        this._setActive(true);
      }
    }, defaults, options);
    this._init();

    return {
      start: function() { return _this.start.apply(_this, arguments); },
      stop: function() { return _this.stop.apply(_this); },
      pause: function() { return _this.pause.apply(_this); },
      resume: function() { return _this.resume.apply(_this); }
    };
  };
})(jQuery);