/** @odoo-module */

import { Component, onMounted, useRef, useState, useSubEnv } from "@odoo/owl";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ExtraInfoPopup } from "@bi_pos_extra_information/js/Popups/ExtraInfoPopup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

export class ExtraInfoButton extends Component {
    static template = "bi_pos_extra_information.ExtraInfoButton";

    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async onClick() {
        if(this.pos.pos_extra_fields.length > 0){
            const { confirmed, payload } = await this.pos.popup.add(ExtraInfoPopup, {
                title: _t("Add Extra Fields Information"),
                extra_fields_data: this.pos.pos_extra_fields,
            });
            if(confirmed){
                 this.pos.get_order().set_extra_info_data(payload);
            }
        } else{
            this.pos.popup.add(ErrorPopup, {
                title: _t('No Extra Fields Found Error'),
                body: _t("Extra fields is not added, please added first."),
            });
        }
    }

}
ProductScreen.addControlButton({
    component: ExtraInfoButton,
    condition: function() {
            if(this.pos.config.allow_extra_info){
                return true;
            } else {
                return false;
            }
        },
});
