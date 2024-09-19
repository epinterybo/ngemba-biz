/** @odoo-module */
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
patch(Order.prototype, {
   export_for_printing() {
       const result = super.export_for_printing(...arguments);
        const company = this.pos.company;
       if (company) {
            result.company_tax_id = company.vat; // Add the company's tax ID to the header data
        }
       return result;
   },
});