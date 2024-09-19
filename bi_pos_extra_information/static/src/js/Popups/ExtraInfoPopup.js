///** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { onMounted } from "@odoo/owl";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

export class ExtraInfoPopup extends AbstractAwaitablePopup {
    static template = "bi_pos_extra_information.ExtraInfoPopup";
    static defaultProps = {
        confirmText: _t("Save"),
        title: _t(""),
        body: '',
        cancelText: _t("Cancel"),
    };
    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
    }
    onMounted() {
        if (this.pos.get_order().get_extra_info_data()){
            var mounted_data = this.pos.get_order().get_extra_info_data();
            for(var data of mounted_data){
                for (const [key, value] of Object.entries(data)) {
                    $('input#'+key+'').val(value);
                }
            }
        }
    }
    save() {
        var final_list = []
        for(var extra_field of this.props.extra_fields_data){
            var data = $('input#'+extra_field.id+'').val();
            var dict_add = {}
            dict_add[extra_field.id] = data
            final_list.push(dict_add)
        }
        this.props.close({ confirmed: true, payload: final_list });
    }
    cancel() {
        this.props.close({ confirmed: true, payload: null });
    }
}
