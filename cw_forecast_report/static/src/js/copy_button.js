/** @odoo-module */

import { registry } from "@web/core/registry";
import { ListController } from "@web/views/list/list_controller";

class CustomListController extends ListController {
    setup() {
        super.setup();
        console.log("Setup on button being done here");
        this.on("click", this.onButtonClick.bind(this), { delegate: ".o_list_button_copy_name" });
    }

    onButtonClick(event) {
        console.log("Button Clicked at this stage");
        const record = this.model.get(event.currentTarget.dataset.id);
        const productName = record.data.product_id.data.display_name;
        navigator.clipboard.writeText(productName).then(() => {
            this.displayNotification({ message: "Product name copied to clipboard!", type: "success" });
        }).catch(err => {
            this.displayNotification({ message: "Failed to copy product name.", type: "danger" });
            console.error('Could not copy text: ', err);
        });
    }
}

registry.category("controllers").add("custom_list", CustomListController);