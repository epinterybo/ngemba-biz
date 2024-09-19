/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { Component, useState} from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { MembershipCardStore } from "../store/membership_card_store";

export class RewardCardCodeButton extends Component {
    static template = 'cw_reward_card_system.RewardCodeButton';

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.state = useState({
            buttonText: _t("MemberShip Card"),
        });
    }

    async onClick() {
        let { confirmed, payload: code } = await this.popup.add(TextInputPopup, {
            title: _t("Enter Card Number"),
            startingValue: "",
            placeholder: _t("Membership Card Number"),
        });

        if (confirmed) {
            code = code.trim();
            if (code !== "") {
                const order = this.pos.get_order();
                if (order) {
                    MembershipCardStore.code = code;
                    this.state.buttonText = code;
                    this.pos.get_order().set_membership_card_code(code);
                }

                //this.pos.get_order().activateCode(code);
            }
        }
    }

}

ProductScreen.addControlButton({
    component: RewardCardCodeButton,
});