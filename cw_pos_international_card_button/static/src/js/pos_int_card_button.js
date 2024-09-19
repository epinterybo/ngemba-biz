/** @odoo-module */

import {Component} from "@odoo/owl";
import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {useService} from "@web/core/utils/hooks";

class PosIntCardButton extends Component {
    static template = "cw_pos_international_card_button.PosIntCardButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.notification = useService("pos_notification");
    }

    async onClick() {
        const config = this.pos.config;
        const order = this.pos.get_order();
        const percentage = config.int_card_percentage;
        const currentTotal = order.get_total_without_tax();

        // console.log(config.pos_cw_surcharge_product_id[0],config.pos_cw_surcharge_product_id);

        const surchargeProduct = this.pos.db.get_product_by_id(config.pos_cw_surcharge_product_id[0]);
        // console.log(surchargeProduct);

        if (!surchargeProduct) {
            this.notification.add('Surcharge product is not defined. Please select the product in Settings > Point of Sale >Bills & Receipts to set it', 4000);
            return false;
        }
        const existingOrderLine = order.orderlines.find(line => line.product.id === surchargeProduct.id );

        if (existingOrderLine) {
            this.notification.add('Surcharge product can olny be added once', 4000);
            return false;
        }
        const surchargeAmount = (percentage / 100) * currentTotal;

        order.add_product(surchargeProduct, {
            price: surchargeAmount,
            extras: {surcharge: true},
        });
    }

    async _getProductByDefaultCode(defaultCode) {
        try {
            const domain = [['default_code', '=', defaultCode]];
            const fields = ['id', 'display_name', 'default_code'];
            const products = await this.env.services.orm.searchRead('product.product', domain, fields, {limit: 1});
            return products.length > 0 ? this.pos.db.get_product_by_id(products[0].id) : null;
        } catch (error) {
            console.error('Error fetching product by default code:', error);
            return null;
        }
    }
}

ProductScreen
    .addControlButton({
            component: PosIntCardButton,
            position: ['after', 'SaveButton'],
            condition:

                () =>
                    true
            ,
        }
    )
;
