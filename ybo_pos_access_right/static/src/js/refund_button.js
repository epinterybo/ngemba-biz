/** @odoo-module */
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";
import {_t} from "@web/core/l10n/translation";
import {RefundButton} from "@point_of_sale/app/screens/product_screen/control_buttons/refund_button/refund_button";

patch(RefundButton.prototype, {
    setup() {
        super.setup();
        this.notification = useService("pos_notification");
    },
    async click() {
        if (this.pos.cashier?.disable_refund_button) {
            this.notification.add(_t("You lack privilege to perform this operation"), 3000);
            return false
        } else {
            return super.click(...arguments);
        }
    },
    disable_refund_button_fn() {
        if (this.pos.cashier?.disable_refund_button) {
            return true;
        } else {
            return false;
        }
    },


})