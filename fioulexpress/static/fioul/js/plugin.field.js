(function($) {
    $.field = function(element) {
        var plugin = this;
        var $element = $(element),
            element = element;

        plugin.init = function() {
            plugin.$input = $element.find('input');
            plugin.$label = $element.find('.field-label');
            plugin.isEmpty = plugin.$input.val() === '';
            if (plugin.isEmpty === false) plugin.active();

            plugin.$input.on('focus', function() {
                plugin.active();
            });
            plugin.$input.on('blur', function() {
                plugin.isEmpty = plugin.$input.val() === '';
                if (plugin.isEmpty === true) plugin.deactive();
            });
            plugin.$input.on('keyup', function() {
                plugin.isEmpty = plugin.$input.val() === '';
            });
        };
        plugin.active = function() {
            plugin.$label.addClass('active');
        };
        plugin.deactive = function() {
            plugin.$label.removeClass('active');
        };
        plugin.check = function() {
            plugin.isEmpty = plugin.$input.val() === '';
            if (plugin.isEmpty) plugin.deactive();
            else plugin.active();
        };

        plugin.init();
    };

    $.fn.field = function() {
        return this.each(function() {
            if ($(this).data('field') === undefined) {
                var plugin = new $.field(this);
                $(this).data('field', plugin);
            }
        });
    };
})(jQuery);