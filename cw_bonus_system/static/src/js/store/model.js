/** @odoo-module */

import {Order} from "@point_of_sale/app/store/models";
import {patch} from "@web/core/utils/patch";
import { eventBus } from "@cw_bonus_system/js/store/event_bus";
import { bonusEmployeeStore } from "@cw_bonus_system/js/store/bonus_employee_store";


patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.bonus_employee_id = this.get_bonus_employee_id() || false;
        this.bonus_employee_name = this.get_bonus_employee_name() || false;
        console.log("Passing through Setup 001");
        eventBus.trigger("new-order");
    },
    initialize(attributes, options) {
        console.log("Passing through Initialize");
        this._super(attributes, options);
        eventBus.trigger("new-order");
        this.resetBonusEmployee();
    },
    export_for_printing() {
        console.log("Passing through export_for_printing");
        const json = super.export_for_printing(...arguments);
        this.resetBonusEmployee();
        eventBus.trigger("new-order");
        return json;
    },
    resetBonusEmployee() {
        console.log("Passing through resetBonusEmployee from Order.Prototype");
        this.bonus_employee_id = false;
        this.bonus_employee_name = false;
        bonusEmployeeStore.bonus_employee_name = null;
        eventBus.trigger("bonus_employee_selected");
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.bonus_employee_id = json.bonus_employee_id;
    },
    set_bonus_employee_id(bonus_employee_id) {
        this.bonus_employee_id = bonus_employee_id;
    },
    get_bonus_employee_id() {
        return this.bonus_employee_id;
    },
    set_bonus_employee_name(bonus_employee_name) {
        this.bonus_employee_name = bonus_employee_name;
    },
    get_bonus_employee_name() {
        return this.bonus_employee_name;
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.bonus_employee_id = this.bonus_employee_id;
        return json;
    },
})