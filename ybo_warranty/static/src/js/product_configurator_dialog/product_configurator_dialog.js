/** @odoo-module */
import {patch} from "@web/core/utils/patch";
import {useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {
    ProductConfiguratorDialog
} from "@sale_product_configurator/js/product_configurator_dialog/product_configurator_dialog";

patch(ProductConfiguratorDialog.prototype, {
    setup() {
        super.setup.apply(this, arguments);
        this.rpc = useService("rpc");
        this.state = useState({
            optionalProductIds: null
        })
    },

    async _addProduct(productTmplId) {
        console.log(`Added Optional Product: ${productTmplId}`);
        // Ensure optionalProductIds is an array
        if (!Array.isArray(this.state.optionalProductIds)) {
            this.state.optionalProductIds = [];
        }
        // Add the productTmplId if it's not already in the array
        if (!this.state.optionalProductIds.includes(productTmplId)) {
            this.state.optionalProductIds.push(productTmplId);
        }
        return await super._addProduct(...arguments);
    },

    async _removeProduct(productTmplId) {
        // Ensure optionalProductIds is an array
        if (!Array.isArray(this.state.optionalProductIds)) {
            this.state.optionalProductIds = [];
        }
        // Remove the productTmplId from the array
        this.state.optionalProductIds = this.state.optionalProductIds.filter(id => id !== productTmplId);

        return await super._removeProduct(...arguments);
    },

    async onConfirm() {
        // const filteredProducts = this.state.products.filter(item => item.product_tmpl_id && item.parent_product_tmpl_ids.length > 0);
        // const result = filteredProducts.reduce((acc, item) => {
        //     acc[item.product_tmpl_id] = item.parent_product_tmpl_ids;
        //     return acc;
        // }, {});
        // try {
        //     const senddata = await this.rpc('/sale_product_configurator/save_data_to_session', {
        //         data: result,
        //     });
        //
        //     console.log("Data saved to session:", senddata);
        // } catch (error) {
        //     console.error("Error saving data:", error);
        // }

        console.log(`Products: ${JSON.stringify(this.state.products)}`);
        return await super.onConfirm(...arguments);
    }

})