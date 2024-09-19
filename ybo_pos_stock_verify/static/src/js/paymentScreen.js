/** @odoo-module */
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {useService} from "@web/core/utils/hooks";
import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {ConfirmPopup} from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.popup = useService("popup");
        this.pos = usePos();
    },

    async validateOrder(isForceValidate) {
        let is_allow_multi_step_delivery = this.pos.config.allow_multi_step_delivery;
        let order = this.pos.get_order();

        // If multi-step delivery is allowed and no partner is selected
        if (is_allow_multi_step_delivery && order.partner === null) {
            // Show confirmation popup
            const {confirmed} = await this.popup.add(ConfirmPopup, {
                title: _t("Attention no Customer Selected!"),
                confirmText: _t("Proceed anyway"),
                body: _t("This POS is configured for 2-step verification. Do you still wish to proceed without the client?"),
            });

            // If confirmed, proceed with order validation
            if (confirmed) {
                return await super.validateOrder(...arguments);
            }
        } else {
            // If no multi-step delivery or a partner is selected, proceed with order validation
            return await super.validateOrder(...arguments);
        }
    }

})