/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { MoneyDetailsPopup } from "@point_of_sale/app/utils/money_details_popup/money_details_popup";
import { useState, onWillStart } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Input } from "@point_of_sale/app/generic_components/inputs/input/input";
import { parseFloat } from "@web/views/fields/parsers";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    //@override
    openCashControl() {
        if (this.shouldShowCashControl()) {
            this.popup.add(CashOpeningPopupExtend, { keepBehind: true });
        }
    }
});

export class CashOpeningPopupExtend extends AbstractAwaitablePopup {
    static template = "ybo_pos_cash_opening_popup.CashOpeningPopupExtend";
    static components = { Input };
    static defaultProps = { cancelKey: false };

    setup() {
        super.setup();
        this.moneyDetails = null;
        this.pos = usePos();
        this.state = useState({
            notes: "",
            openingCash: this.env.utils.formatCurrency(
                this.pos.pos_session.cash_register_balance_start || 0,
                false
            ),
        });
        this.popup = useService("popup");
        this.orm = useService("orm");
        this.hardwareProxy = useService("hardware_proxy");
        onWillStart(async () => {
            await this.fetchDataFromModel(this.pos.config.id);
        });
    }

    async fetchDataFromModel(sessionId) {
        var val;
        const last_session_bill = await this.orm.call("ybo_pos_cash_move.pos_cash_report", "get_last_session_bill", [
            val, sessionId
        ]);
        if (last_session_bill) {
            this.moneyDetails = last_session_bill;
        }
    }





    //@override
    async confirm() {
        this.pos.pos_session.state = "opened";
        this.orm.call("pos.session", "set_cashbox_pos", [
            this.pos.pos_session.id,
            parseFloat(this.state.openingCash),
            this.state.notes,
        ]);
        super.confirm();
    }
    async openDetailsPopup() {
        // var val;
        // const last_session_bill = await this.orm.call("ybo_pos_cash_move.pos_cash_report", "get_last_session_bill", [
        //     val, this.pos.config.id
        // ]);

        // console.log(last_session_bill);

        // return;
        const action = _t("Cash control - opening");
        this.hardwareProxy.openCashbox(action);
        const { confirmed, payload } = await this.popup.add(MoneyDetailsPopup, {
            moneyDetails: this.moneyDetails,
            action: action,
        });
        if (confirmed) {
            const { total, moneyDetails, moneyDetailsNotes } = payload;
            this.state.openingCash = this.env.utils.formatCurrency(total, false);
            if (moneyDetailsNotes) {
                this.state.notes = moneyDetailsNotes;
            }
            this.moneyDetails = moneyDetails;
        }
    }
    handleInputChange() {
        if (!this.env.utils.isValidFloat(this.state.openingCash)) {
            return;
        }
        this.state.notes = "";
    }
}
