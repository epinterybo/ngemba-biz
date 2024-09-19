/** @odoo-module */

import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {PaymentScreenPaymentLines} from "@point_of_sale/app/screens/payment_screen/payment_lines/payment_lines";
import {patch} from "@web/core/utils/patch";
import {CheckInfoPopup} from "@ybo_pos_cheque_info/js/check_info_popup";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {useService} from "@web/core/utils/hooks";
import {_t} from "@web/core/l10n/translation";
import {Component, useState, onWillUnmount} from "@odoo/owl";

// Shared function to handle the check information
async function handleCheckInfo(popup, pos, selectedPaymentLine = null) {
    var order = pos.get_order();
    let selected_paymentline = selectedPaymentLine || order.selected_paymentline;
    if (selected_paymentline) {
        const check_info = selected_paymentline.getCheckInfo();
        const {confirmed} = await popup.add(CheckInfoPopup, {
            title: 'Check',
            array: check_info,
        });
        if (confirmed) {
            let customer = order.partner;

            let bank_id = parseInt($("#bank_id").val());
            var bank_name = $("#bank_id option:selected").text();
            let check_number = document.getElementById("check_number").value;
            let owner_name = customer?.name || '';
            let bank_account = document.getElementById("bank_account").value;
            let allow_check_info = selected_paymentline.payment_method.allow_check_info;

            selected_paymentline.set_allow_check_info(allow_check_info);
            selected_paymentline.set_check_number(check_number);
            selected_paymentline.set_owner_name(owner_name);
            selected_paymentline.set_bank_account(bank_account);
            selected_paymentline.set_bank_name(bank_id);
            selected_paymentline.set_bank_fullname(bank_name);

            return selected_paymentline;
        }
    }
    return null;
}

patch(PaymentScreenPaymentLines.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
    },
    async _CheckInfoClicked(cid) {
        await handleCheckInfo(this.popup, this.pos);
    },
    getBankAccount(line) {
        return line.bank_account || '';
    },
    getCheckNumber(line) {
        return line.check_number || '';
    },
    getAmount(line) {
        return line.amount || '';
    },
    getBankName(line) {
        return line.bank_fullname || '';
    }
});

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
        this.notification = useService("pos_notification");
        this.state = useState({
            check_number: '',
            bank_account: '',
            owner_name: '',
            bank_name: '',
        });
    },
    async _CheckInfoClicked() {
        await handleCheckInfo(this.popup, this.pos);
    },

    async addNewPaymentLine(paymentMethod) {
        let order = this.pos.get_order();
        let customer = order.partner;
        if (paymentMethod.type === 'bank' && paymentMethod.allow_check_info) {

            // Add the payment line
            const result = this.currentOrder.add_paymentline(paymentMethod);
            if (result) {
                this.numberBuffer.reset();

                // Trigger the check information pop-up
                await this._CheckInfoClicked();

                return true;
            } else {
                this.notification.add(_t("There is already an electronic payment in progress."), 3000);
                return false;
            }
        }

        return super.addNewPaymentLine(...arguments);
    },
    async validateOrder(isForceValidate) {
        for (const line of this.paymentLines) {
            if (line.payment_method.allow_check_info) {
                if (line.payment_method.type === 'bank' && !line.allow_check_info && (!line.check_number || !line.owner_name || !line.bank_account || isNaN(line.bank_name))) {
                    await this._CheckInfoClicked();
                    this.notification.add(_t("All check information fields are required."), 3000);
                    return false;
                }
            }
        }
        return await super.validateOrder(...arguments);

    },
});
