var results = function() {
    'use strict';
    return {
        init: function() {
            initPopovers();
        }
    };
}();

var initPopovers = function() {
    $('[data-toggle="popover"]').popover();
};
