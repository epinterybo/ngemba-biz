odoo.define('cw_forecast_report.remove_create_button', function (require) {
    "use strict";

    var ListView = require('web.ListView');

    ListView.include({
        render_buttons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.find('.o_list_button_add').remove(); // Remove the Create button
            }
        }
    });
});