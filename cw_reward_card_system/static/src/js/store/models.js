/** @odoo-module */

import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.membership_card_code = this.get_membership_card_code() || false;
    },
    initialize(attributes, options) {
        console.log("Passing through Initialize");
        this._super(attributes, options);
        this.resetMembershipCardCode();
    },
    resetMembershipCardCode() {
        console.log("Passing through resetMembershipCardCode from Order.Prototype");
        this.membership_card_code = false;
    },
    export_for_printing() {
        console.log("Passing through export_for_printing From Membership");
        const json = super.export_for_printing(...arguments);
        this.resetMembershipCardCode();
        return json;
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.membership_card_code = json.membership_card_code;
    },
    set_membership_card_code(membership_card_code) {
        this.membership_card_code = membership_card_code;
    },
    get_membership_card_code() {
        return this.membership_card_code;
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.membership_card_code = this.membership_card_code;
        return json;
    },

})