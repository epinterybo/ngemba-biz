/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { debounce } from "@web/core/utils/timing";
import { useService, useAutofocus } from "@web/core/utils/hooks";
import { useAsyncLockedMethod } from "@point_of_sale/app/utils/hooks";
import { session } from "@web/session";

import { BonusEmployeeLine } from "@cw_bonus_system/js/Screens/BonusEmployeeLine/BonusEmployeeLine";
import { bonusEmployeeStore } from "@cw_bonus_system/js/store/bonus_employee_store";
import { eventBus } from "@cw_bonus_system/js/store/event_bus";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, onWillUnmount, onMounted, useRef, useState } from "@odoo/owl";


export class BonusEmployeeScreen extends Component {
    static components = { BonusEmployeeLine };
    static template = "cw_bonus_system.EmployeeBonusScreen"

    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.orm = useService("orm");
        this.notification = useService("pos_notification");
        this.searchWordInputRef = useRef("search-word-input-bonus-employee");
        useAutofocus({refName: 'search-word-input-bonus-employee'})

        this.bonus_employees = this.props.bonus_employees || [];
        console.log("Bonus Employee are " + this.bonus_employees);

        this.state = useState({
            query: null,
            selectedBonusEmployee: this.props.bonus_employee,
            previousQuery: "",
            currentOffset: 0,
        });
        this.updateBonusEmployeeList = debounce(this.updateBonusEmployeeList, 70);
        this.saveChanges = useAsyncLockedMethod(this.saveChanges);
        onWillUnmount(this.updateBonusEmployeeList.cancel);

        onMounted(() => {
            eventBus.addEventListener("new-order", this.resetBonusEmployee.bind(this));
        });

        onWillUnmount(() => {
            eventBus.removeEventListener("new-order", this.resetBonusEmployee.bind(this));
        });
    }

    resetBonusEmployee() {
        console.log("resetting the Sale Staff here");
        this.bonus_employees = [];
        bonusEmployeeStore.bonus_employee_name = null;
        eventBus.trigger("bonus_employee_selected");
    }

    back(force = false) {
        this.props.resolve({ confirmed: false, payload: false });
        this.pos.closeTempScreen();
    }

    _closePopUp() {
        this.pos.closeTempScreen();
    }


    confirm() {
        this.props.resolve({ confirmed: true, payload: this.state.selectedBonusEmployee });
        this.pos.closeTempScreen();
    }

    get currentOrder() {
        return this.pos.get_order();
    }

    /** 
    get bonus_employees() {
        let res;

        if(this.state.query && this.state.query.trim() !== "") {
            res = this.pos.db.search_bonus_employee(this.state.query.trim());
        } else {
            res = this.pos.db.get_bonus_employee_sorted(1000);
        }
        res.sort(function (a, b) {
            return (a.name || "").localeCompare(b.name || "");
        });

        //the selected employee (if any) is displayed at the top of the list
        if(this.state.selectedBonusEmployee) {
            const indexOfSelectedBonusEmployee = res.findIndex(
                (bonus_employee) => bonus_employee.id === this.state.selectedBonusEmployee.id
            );
            if(indexOfSelectedBonusEmployee !== 1) {
                res.splice(indexOfSelectedBonusEmployee, 1);
            }
            res.unshift(this.state.selectedBonusEmployee);
        }

        return res;
    }
    */

    async _onPressEnterKey() {
        console.log("OnpresseEnterKeY Pass Param=" + this.searchWordInputRef);
        console.log("OnpresseEnterKeY Pass Query=" + this.state.query);

        /*
        if (!this.state.query) {
            this.bonus_employees = this.props.bonus_employees || [];
            return;
        }
        */

        console.log("OnpresseEnterKeY 002 Pass Query=" + this.state.query);

        const result = await this.searchBonusEmployee();

        if(result.length > 0) {
            this.notification.add(
                _t('%s employee(s) found for "%s"', result.length, this.state.query), 3000);
        } else {
            this.notification.add(_t('No employee found for "%s".', this.state.query), 3000);
        }
    }

    _clearSearch() {
        this.searchWordInputRef.el.value = "";
        this.state.query = "";
    }

    async updateBonusEmployeeList(event) {
        this.state.query = event.target.value;
    }

    clickBonusEmployee(bonus_employee) {
        if(this.state.selectedBonusEmployee && this.state.selectedBonusEmployee.id === bonus_employee.id) {
            this.state.selectedBonusEmployee = null;
        } else {
            const currentPosOrder = this.pos.get_order();
            console.log("bonus Employee id is " + bonus_employee.id + " and name is " + bonus_employee.name);
            // Update the store
            bonusEmployeeStore.bonus_employee_name = bonus_employee.name;
            currentPosOrder.set_bonus_employee_id(bonus_employee.id);
            currentPosOrder.set_bonus_employee_name(bonus_employee.name);
            this.state.selectedBonusEmployee = bonus_employee;
            this.notification.add(bonus_employee.name + " has been selected for this order", 3000);
            eventBus.trigger("bonus_employee_selected");
        }

        this.confirm();
    }

    async searchBonusEmployee() {
        if(this.state.previousQuery != this.state.query) {
            this.state.currentOffset = 0;
        }

        console.log("searchBonusEmployee 001 Pass Query=" + this.state.query);

        const result = await this.getNewBonusEmployees();
        this.bonus_employees = result;
        //this.pos.addBonusEmployees(result);
        console.log("searchBonusEmployee 001 Pass Query=" + this.state.query);
        console.log("The Result I'm getting are this: " + result);

        if(this.state.previousQuery == this.state.query) {
            this.state.currentOffset += result.length;
        } else {
            this.state.previousQuery = this.state.query;
            this.state.currentOffset = result.length;
        }
        return result;
    }

    async getNewBonusEmployees() {
        console.log("getNewBonusEmployees 001 Pass Query=" + this.state.query);
        let domain = [];
        const limit = 30;
        if(this.state.query) {
            const search_fields = ["name"];
            domain = [
                ...Array(search_fields.length - 1).fill('|'),
                ...search_fields.map(field => [field, "ilike", this.state.query + "%"])
            ];
        }

        const result = await this.orm.silent.call(
            "cw.bonus.employee",
            "get_pos_ui_employee_bonus_by_params",
            [[odoo.pos_session_id], { domain, limit: limit, offset: this.state.currentOffset }]
        );
        return result;
    }
}

registry.category("pos_screens").add("BonusEmployeeScreen", BonusEmployeeScreen);