/** @odoo-module */

import { Component } from "@odoo/owl";

export class BonusEmployeeLine extends Component {
    static template = "cw_bonus_system.BonusEmployeeLine"

    get highlight() {
        return this._isBonusEmployeeSelected ? "highlight active" : "";
    }

    get _isBonusEmployeeSelected() {
        return this.props.bonus_employee === this.props.selectedBonusEmployee;
    }
}