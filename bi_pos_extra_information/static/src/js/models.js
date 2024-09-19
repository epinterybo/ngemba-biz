/** @odoo-module */

import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.extra_info = this.get_extra_info_data() || false;
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.extra_info = json.extra_info;
    },
    set_extra_info_data(extra_info) {
        this.extra_info = extra_info;
    },
    get_extra_info_data() {
        return this.extra_info;
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.extra_info = this.extra_info;
        return json;
    },
    export_for_printing() {
        const json = super.export_for_printing(...arguments);
//            var list_data = []
//            for (var data of this.get_extra_info_data()){
//                console.log("data", data)
//                list_data.push(data)
//            }
//            console.log("list_data", list_data)
        json.extra_info = this.get_extra_info_data();
        return json;
    }

});
