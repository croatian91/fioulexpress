(function($) {
    $.popin = function(element, options) {
        var plugin = this;
        var $element = $(element),
            element = element;

        plugin.init = function() {
            plugin.$container = $('<div>', {class: 'popin-wrapper fade'}).appendTo('body');
            plugin.$overlay = $('<div>', {class: 'popin-overlay'}).appendTo(plugin.$container);
            plugin.$btnClose = $('<div>', {class: 'popin-btn-close close'}).appendTo($element);
            $element.appendTo(plugin.$container).show();

            if (options.trigger !== undefined) $(options.trigger).on('click', function() { plugin.open(); });
            if (options.url !== undefined) {
                plugin.isLoaded = false;
                plugin.shouldBeOpened = false;
                loadPopinContent();
            }
            if (options.onLoad !== undefined && options.url === undefined) { onLoadCallback(); }

            plugin.$container.on('click', '.popin-btn-close, .popin-overlay', function() { plugin.close(); });
        };

        plugin.open = function() {
            if (options.url !== undefined && plugin.isLoaded === false) {
                if (options.trigger !== undefined) $(options.trigger).addClass('is-loading');
                plugin.shouldBeOpened = true;
            } else {
                showPopin();
            }
        };
        plugin.close = function() {
            plugin.$container.scrollTop(0);
            hidePopin();
        };

        var showPopin = function() {
            plugin.$container.addClass('in');
            $('body').addClass('no-scroll');
            if ($element.data('determined-position') === undefined) determinePosition();
        };
        var hidePopin = function() {
            plugin.$container.removeClass('in');
            $('body').removeClass('no-scroll');
        };
        var loadPopinContent = function() {
            $.ajax({
                url: options.url,
                success: function(data) {
                    var popinContent = $('<div>', { html: data });
                    if (options.block !== undefined) popinContent = popinContent.find(options.block);
                    popinContent.appendTo($element);
                    if (options.onLoad !== undefined) onLoadCallback();
                    plugin.isLoaded = true;
                    if (plugin.shouldBeOpened === true) {
                        if (options.trigger !== undefined) $(options.trigger).removeClass('is-loading');
                        showPopin();
                    }
                },
                error: function() {
                    console.error('popin : ajax error');
                }
            });
        };
        var determinePosition = function() {
            $element.data('determined-position', true);
            var popinHeight = $element.outerHeight();
            var bodyHeight = $('body').height();
            if (popinHeight < bodyHeight) $element.css('top', '50%').css('margin-top', -(popinHeight / 2));
        };
        var onLoadCallback = function() {
            var onLoad = window[options.onLoad];
            if (typeof onLoad === 'function') onLoad($element);
        };

        plugin.init();
    };

    $.fn.popin = function() {
        return this.each(function() {
            if ($(this).data('popin') === undefined) {
                var options = {
                    'trigger': $(this).data('trigger'),
                    'url': $(this).data('url'),
                    'block': $(this).data('block'),
                    'onLoad': $(this).data('onload')
                };
                var plugin = new $.popin(this, options);
                $(this).data('popin', plugin);
            }
        });
    };
})(jQuery);