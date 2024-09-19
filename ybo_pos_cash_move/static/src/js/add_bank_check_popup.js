/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { NumericInput } from "@point_of_sale/app/generic_components/inputs/numeric_input/numeric_input";
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

/**
* This class represents a custom popup in the Point of Sale.
* It extends the AbstractAwaitablePopup class.
*/
export class AddBankCkeckPopup extends AbstractAwaitablePopup {
    static template = "ybo_pos_cash_move.add_bank_check_popup";
    static components = { NumericInput };
    static props = [
        "amount",
        "bank",
        "account_number",
        "drawer",
        "cheque_number",
    ];

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.state = useState(this.getInitialState());

    }

    getInitialState() {
        return {
            amount: this.props.amount,
            bank: this.props.bank,
            account_number: this.props.account_number,
            drawer: this.props.drawer,
            cheque_number: this.props.cheque_number,
        }
    }


    close() {
        this.cancel();
        // this.pos.showScreen("ProductScreen");
    }

    addBankCheck() {
        if (
            this.state.amount === 0 ||
            !this.state.bank ||
            !this.state.account_number ||
            !this.state.drawer ||
            !this.state.cheque_number
        ) {
            this.popup.add(ErrorPopup, {
                title: "Error",
                body: "Please fill all fields and amount should not be 0",
            });
            return;
        }

        this.confirm();
    }

    async getPayload() {
        return this.state;
    }
}

// registry.category("pos_screens").add("SimpleCountPopup", SimpleCountPopup);