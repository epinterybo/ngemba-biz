/** @odoo-module */
import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { useAsyncLockedMethod } from "@point_of_sale/app/utils/hooks";
import { Component, useState, onWillUnmount, onWillStart } from "@odoo/owl";
import { floatIsZero } from "@web/core/utils/numbers";
import { NumericInput } from "@point_of_sale/app/generic_components/inputs/numeric_input/numeric_input";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { patch } from "@web/core/utils/patch";
import { Navbar } from '@point_of_sale/app/navbar/navbar';
import { AddBankCkeckPopup } from "./add_bank_check_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";


/**
 * Override Cash In & Out List Item Onclick event
 */
patch(Navbar.prototype, {
    async onCashMoveButtonClick() {
        this.pos.showScreen('CashMovePopupExtend');
    }
})

/**
 * Custom Cash In & Out view
 */


class CashMovePopupExtend extends Component {
    static template = "ybo_pos_cash_move.cash_move_popup_extend";
    static components = { NumericInput };

    /**
     * Setup method to initialize component.
     */
    setup() {
        super.setup();
        this.isDestroyed = false;

        this.pos = usePos();
        this.notification = useService("pos_notification");
        this.popup = useService("popup");
        this.orm = useService("orm");
        this.report = useService("report");
        this.currency = this.pos.currency;
        this.savedBankChecksList = useState({
            value: [

            ]
        });
        this.withdrawBills = this.bankChecks = useState({
            value: null
        });
        this.bankChecks = useState({
            value: []
        });
        this.check_amounts = useState({
            value: []
        });
        this.fpos = useState({
            value: []
        });
        this.bankChequeSelected = useState({
            value: null
        });
        this.bankChequeAmount = useState({
            value: null
        });
        this.state = useState({
            operationType: "simple",
            amount: 0,
            reason: "",
            fpos_input: null,
            check_amount_input: null,
            isFinalCount: false,
            moneyDetails: this.props.moneyDetails
                ? { ...this.props.moneyDetails }
                : Object.fromEntries(this.pos.bills.map((bill) => [bill.value, 0])),
            isLocked: false,  // New state to manage locking

        });

        this.confirm = useAsyncLockedMethod(this.confirm);
        onWillUnmount(this.winWillUnmount);
        onWillStart(async () => {
            await this.fetchDataFromModel(this.pos.pos_session.id);
        });
    }


    _closePopUp() {
        this.pos.closeTempScreen();
    }


    /**
     * Filter the bank checks list based on a search word.
     * @param {string} searchWord
     * @returns {array} filtered list of bank checks
     */
    searchBankChecks(searchWord) {
        if (!searchWord) {
            return [];
        }
        return this.savedBankChecksList.value.filter(check => {
            const searchWordLower = searchWord.toLowerCase();
            return [
                check.drawer.toLowerCase().includes(searchWordLower),
                check.bank.toLowerCase().includes(searchWordLower),
                check.cheque_number.toLowerCase().includes(searchWordLower),
                check.account_number.toLowerCase().includes(searchWordLower),
            ].some(match => match);
        });
    }

    winWillUnmount() {
        this.isDestroyed = true;
    }

    /**
     * Default properties for the CustomCashInOutPopup component.
     */
    static defaultProps = {
        closePopup: _t("Discard"),
        confirmTextPart1: _t("Submit "),
        confirmTextPart2: _t(" for approval"),
        opTypeTitle: _t("Operation type:"),
    };

    /**
     * Display confirmation popup before submitting the request.
     */
    async confirmBtn() {
        const { confirmed } = await this.popup.add(ConfirmPopup, {
            title: _t("Attention !"),
            body: _t("Are you sure you wish to perform this operation ?"),
        });
        if (confirmed) {
            if (this.state.isLocked) {
                return;
            }
            this.submitForApproval();
            this._closePopUp();
        }
    }

    async fetchDataFromModel(pos_session_id) {
        let val;
        let enter_cheques = await this.orm.call("ybo_pos_cash_move.pos_cash_report", "enter_cheques", [
            val, pos_session_id
        ]);

        this.savedBankChecksList = {
            ...this.savedBankChecksList,
            value: enter_cheques,
        };

        let last_counted_cheques = await this.orm.call("ybo_pos_cash_move.pos_cash_report", "last_counted_cheques", [
            val, pos_session_id
        ]);

        last_counted_cheques.forEach(check => {
            this.bankChecks.value.push({
                ...check,
            })
        });

        let bills = await this.orm.call("ybo_pos_cash_move.pos_cash_report", "get_withdraw_bill", [
            val, pos_session_id
        ]);
        console.log("Money details", this.state.moneyDetails);

        console.log("Bills From Backend", bills);

        // Object.keys(this.state.moneyDetails).forEach(key => {
        //     if (bills.hasOwnProperty(key)) {
        //         this.state.moneyDetails[key] = bills[key];
        //     }
        // });

        this.withdrawBills.value = bills;

        // this.withdrawBills = [...bills];
    }


    /**
     * Submit the cash in/out request for approval.
     */
    async submitForApproval() {
        if (this.state.isLocked) {
            return;
        }

        this.state.isLocked = true;  // Lock the component

        const { operationType, moneyDetails, reason } = this.state;
        const amount = this.computeTotal();
        const formattedAmount = this.env.utils.formatCurrency(amount);
        const cash_out_cheques = this.bankChecks.value;
        const cheque_amount_list = this.check_amounts.value;
        const fpos_amount = this.summaryAmountFpos();
        const fpos_list = this.fpos.value;
        const is_final_count = this.state.isFinalCount;

        if (amount <= 0) {
            this.notification.add(_t("Cash in/out value can not be %s.", formattedAmount), 3000);
            this.state.isLocked = false;  // Unlock the component
            return false;
        }


        try {
            if (this.isDestroyed) {
                return;
            }

            if (operationType === "out") {
                await this.saveCashInOutRecords(amount, reason, operationType, moneyDetails, cash_out_cheques, fpos_amount, fpos_list, false);
            } else if (operationType === "simple") {
                await this.saveCashInOutRecords(amount, reason, operationType, moneyDetails, cheque_amount_list, fpos_amount, fpos_list, is_final_count);
            } else {
                await this.saveCashInOutRecords(amount, reason, operationType, moneyDetails, [], 0, [], false);
            }


            if (operationType === "in") {
                await this.submitCashInOutOperationOdoo(amount, reason, operationType, formattedAmount);
            }

            this.notification.add(_t("Requested submitted successfully."), 3000);
            // Redirect to product screen
            this.pos.showScreen("ProductScreen");
        } catch (error) {
            this.notification.add(_t("An error occurred while submitting for approval:"), 3000);
            console.error("", error);
        } finally {
            this.state.isLocked = false;  // Unlock the component after the async call
        }
    }

    async saveCashInOutRecords(amount, reason, operationType, moneyDetails, cheques, fpos_amount, fpos_list, is_final_count) {
        let val;
        if (operationType == "simple") {
            await this.orm.call("ybo_pos_cash_move.pos_simple_count", "submit_cash_count", [
                val, this.pos.pos_session.id,
                this.pos.config.id, amount,
                reason.trim(), moneyDetails,
                cheques, fpos_amount, fpos_list, is_final_count
            ]);

        } else if (operationType == "out") {
            console.log("Cheques", cheques);

            await this.orm.call("ybo_pos_cash_move.pos_cash_report", "submit_cash_count", [
                val, this.pos.pos_session.id,
                this.pos.config.id,
                operationType, amount,
                reason.trim(), moneyDetails,
                operationType === "out" ? cheques : [], fpos_amount, fpos_list
            ]);
        } else {

            await this.orm.call("ybo_pos_cash_move.pos_cash_report", "submit_cash_count", [
                val, this.pos.pos_session.id,
                this.pos.config.id,
                operationType, amount,
                reason.trim(), moneyDetails,
                operationType === "out" ? cheques : []
            ]);
        }

    }

    async submitCashInOutOperationOdoo(amount, reason, operationType, formattedAmount) {
        const translatedType = _t(operationType);
        const extras = { formattedAmount, translatedType };
        await this.orm.call("pos.session", "try_cash_in_out", [
            [this.pos.pos_session.id],
            operationType,
            amount,
            reason.trim(),
            extras,
        ]);
    }

    /**
     * Compute the total amount of money details.
     */
    computeTotal(moneyDetails = this.state.moneyDetails) {
        return this.computeSubTotal() + this.summaryAmountBankCheck() + this.summaryAmountFpos() + this.summaryAmountCheckAmouts();
    }

    computeSubTotal(moneyDetails = this.state.moneyDetails) {
        return Object.entries(moneyDetails).reduce((total, [value, inputQty]) => {
            const quantity = isNaN(inputQty) ? 0 : inputQty;
            return total + parseFloat(value) * quantity;
        }, 0);
    }

    /**
     * Format the counted bills into a string.
     */
    formatCountedBills(moneyDetails) {
        if (floatIsZero(this.computeTotal(), this.currency.decimal_places)) {
            return null;
        }

        return this.pos.bills
            .filter(bill => moneyDetails[bill.value])
            .map(bill => `  - ${moneyDetails[bill.value]} x ${this.env.utils.formatCurrency(bill.value)}\n`)
            .join("");
    }

    /**
     * Format the given value as currency.
     */
    format(value) {
        return this.env.utils.isValidFloat(value)
            ? this.env.utils.formatCurrency(parseFloat(value))
            : "";
    }

    /**
     * Update the reason state when the reason input changes.
     */
    updateReason(event) {
        this.state.reason = event.target.value;
    }

    /**
     * Update the operation type when the radio button changes.
     */
    updateOperationType(event) {
        if (event.target.value == "out") {
            if (this.withdrawBills.value) {
                Object.keys(this.state.moneyDetails).forEach(key => {
                    if (this.withdrawBills.value.hasOwnProperty(key)) {
                        this.state.moneyDetails[key] = this.withdrawBills.value[key];
                    }
                });
            }
        } else {
            this.state.moneyDetails = this.props.moneyDetails
                ? { ...this.props.moneyDetails }
                : Object.fromEntries(this.pos.bills.map((bill) => [bill.value, 0]));
        }
        this.state.operationType = event.target.value;
    }

    /**
     * Parse the given value to a float.
     */
    _parseFloat(value) {
        return parseFloat(value);
    }

    /**
     * Opens the AddBankCkeckPopup.
     */
    async openAddBankCheckPopUp() {
        console.log("openAddBankCheckPopUp");

        const { confirmed, payload } = await this.popup.add(AddBankCkeckPopup);

        if (confirmed) {
            this.bankChecks.value.push({
                ...payload,
                id: Math.floor(Math.random() * 10000000000),
            });
        }

    }

    async openUpdateBankCheckPopUp(id) {
        const bankCheck = this.bankChecks.value.find(bankCheck => bankCheck.id == id);
        if (!bankCheck) {
            this.notification.add(_t("Bank check not found."), 3000);
            return
        }
        const { confirmed, payload } = await this.popup.add(AddBankCkeckPopup, {
            amount: bankCheck.amount,
            bank: bankCheck.bank,
            account_number: bankCheck.account_number,
            drawer: bankCheck.drawer,
            cheque_number: bankCheck.cheque_number,
        });

        if (confirmed) {
            const index = this.bankChecks.value.findIndex(bankCheck => bankCheck.id == id);
            this.bankChecks.value[index] = {
                ...payload,
                id: id
            };
        }

    }

    async addBankCheque() {
        if (!this.bankChequeSelected.value || !this.bankChequeAmount.value) {
            this.notification.add(_t("Please select a bank cheque and amount."), 3000);
            return
        }

        var id = this.bankChequeSelected.value.split(' | ')[0];

        var bankChequeInfo = this.savedBankChecksList.value.find(savedBankCheck => savedBankCheck.id == id);
        if (!bankChequeInfo) {
            this.notification.add(_t("Bank cheque not found."), 3000);
            return
        }

        if (this.bankChecks.value.find(check => check.id == bankChequeInfo.id)) {
            this.bankChequeSelected.value = null;
            this.notification.add(_t("Bank cheque already added."), 3000);
            return
        }


        this.bankChecks.value.push({
            ...bankChequeInfo,
            amount: parseFloat(this.bankChequeAmount.value),
        });

        console.log(this.bankChequeSelected.value, this.bankChequeAmount.value);
        this.bankChequeSelected.value = null;
        this.bankChequeAmount.value = null;

    }



    addFpos() {
        if (!this.state.fpos_input || this.state.fpos_input <= 0) {
            this.popup.add(ErrorPopup, {
                title: "Error",
                body: "Please fill all fields and amount should not be 0",
            });
            return;
        }
        this.fpos.value.push({
            id: Math.floor(Math.random() * 10000000000),
            amount: this.state.fpos_input,
        });
        this.state.fpos_input = null;
    }

    addCheckAmount() {
        if (!this.state.check_amount_input || this.state.check_amount_input <= 0) {
            this.popup.add(ErrorPopup, {
                title: "Error",
                body: "Please fill all fields and amount should not be 0",
            });
            return;
        }
        this.check_amounts.value.push({
            id: Math.floor(Math.random() * 10000000000),
            amount: this.state.check_amount_input,
        });
        this.state.check_amount_input = null;
    }

    editCheck(id) {
        const check = this.state.bankChecks.find(check => check.id === id);

        // this.popup.add(AddBankCkeckPopup, {
        //     check
        // });
    }

    deleteFpos(id) {
        this.fpos.value = this.fpos.value.filter(fpos => fpos.id !== id);
    }

    deleteCheckAmount(id) {
        this.check_amounts.value = this.check_amounts.value.filter(check_amount => check_amount.id !== id);
    }

    deleteCheck(id) {
        // console.log(this.bankChecks.value.filter(check => check.id !== id));
        console.log(id);

        // this.bankChecks.value = this.bankChecks.value.filter(check => console.log(check.id !== id));

        this.bankChecks.value = this.bankChecks.value.filter(check => check.id !== id);

    }

    summaryAmountBankCheck() {
        if (this.state.operationType === 'out') {
            return this.bankChecks.value
                .map(check => check.amount)
                .reduce((total, amount) => total + parseFloat(amount), 0);
        } else {
            return 0;
        }

    }

    summaryAmountFpos() {
        if (this.state.operationType === 'simple' || this.state.operationType === 'out') {
            return this.fpos.value
                .map(fpos_item => fpos_item.amount)
                .reduce((total, amount) => total + parseFloat(amount), 0);
        } else {
            return 0
        }

    }

    summaryAmountCheckAmouts() {
        if (this.state.operationType === 'simple') {
            return this.check_amounts.value
                .map(check_amount => check_amount.amount)
                .reduce((total, amount) => total + parseFloat(amount), 0);
        } else {
            return 0
        }

    }
}

registry.category("pos_screens").add("CashMovePopupExtend", CashMovePopupExtend);


