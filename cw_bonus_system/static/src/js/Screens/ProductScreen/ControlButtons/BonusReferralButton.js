/** @odoo-module */
import { Component, onMounted, onWillUnmount, useRef, useState, useSubEnv, useEffect } from "@odoo/owl";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { bonusEmployeeStore } from "@cw_bonus_system/js/store/bonus_employee_store";
import { eventBus } from "@cw_bonus_system/js/store/event_bus";

export class CwBonusReferralButton extends Component {
    static template = "cw_bonus_system.BonusReferralButton";

    setup() {
        this.pos = usePos();
        this.state = useState({
            buttonText: "Staff Referral",
        });

        //this.watch(bonusEmployeeStore, 'bonus_employee_name', this.updateButtonText.bind(this));
        // Use an effect to update the button text when bonusEmployeeStore changes
        /*
        useEffect(
            () => {
                this.updateButtonText();
            }, 
            () => [bonusEmployeeStore.bonus_employee_name]
        );
        */

        // Bind the correct context to the method
        this.updateButtonText = this.updateButtonText.bind(this);

        onMounted(() => {
            eventBus.addEventListener("bonus_employee_selected", this.updateButtonText);
        });

        onWillUnmount(() => {
            eventBus.removeEventListener("bonus_employee_selected", this.updateButtonText);
        });

        // Initial call to set the button text
        this.updateButtonText();
    }

    async updateButtonText() {
        const order = this.pos.get_order();
        console.log("updateButtonText 001")
        if (order) {
            //const bonus_employee_name = order.get_bonus_employee_name();
            const bonus_employee_name = bonusEmployeeStore.bonus_employee_name;
            console.log("updateButtonText 002 " +  bonus_employee_name);
            this.state.buttonText = bonus_employee_name ? bonus_employee_name : "Staff Referral";
        }
    }
    /*
    async onClick() {
        var self = this;
        this.pos.showScreen('BonusEmployeeScreen');
    }
    */

    async onClick() {
        var self = this;
        const bonus_employees = await this.env.services.orm.silent.call(
            'cw.bonus.employee', 'search_read', 
            [[], ['id', 'name', 'code_employee']]
        );

        //this.pos.showScreen('BonusEmployeeScreen', { bonus_employees });
        this.pos.showTempScreen('BonusEmployeeScreen', { bonus_employees });

        //this.updateButtonText();
    }
}

ProductScreen.addControlButton({
    component: CwBonusReferralButton,
});