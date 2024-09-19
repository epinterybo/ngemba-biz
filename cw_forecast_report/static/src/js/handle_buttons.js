/** @odoo-module */
// static/src/js/handle_buttons.js
import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { Component, useRef } from "@odoo/owl";
import { makeRPC } from "@web/core/network/rpc_service";
import { useService } from "@web/core/utils/hooks";

class HandleButtons extends Component {
    setup() {
        super.setup();
        this.button1Ref = useRef("button1");
        this.button2Ref = useRef("button2");
        this.rpc = useService('rpc');
        this.orm = useService('orm');
        this.actionService = useService("action");
    }

    copyProductName(productName) {
        navigator.clipboard.writeText(productName).then(() => {
            this.env.services.notification.add("Product name copied to clipboard!", { type: "success" });
        }).catch(err => {
            this.env.services.notification.add("Failed to copy product name.", { type: "danger" });
            console.error('Could not copy text: ', err);
        });
    }

    onButtonClick1(event) {
        const productName = event.target.dataset.productName;
        this.copyProductName(productName);
    }

    /*
    onButtonClick2(event) {
        const productName = event.target.dataset.productName;
        alert('Button 2 clicked for: ' + productName);
    }
    */
    async onButtonClick2(event) {
        const recordId = event.target.dataset.recordId;
        console.log("posted element is " + recordId)
        console.log("Parse id elment is " + parseInt(recordId));
        const action = await this.orm.call('cw.ocm.forecast', 'your_method', [parseInt(recordId)]);
        console.log(action);
        //this.actionService.doAction(action); 
        /*
        try {
            await makeRPC("/web/dataset/call_kw", {
                model: "cw.ocm.forecast",
                method: "your_method",
                args: [[parseInt(recordId)]],
            });
            this.env.services.notification.add("Method called successfully!", { type: "success" });
        } catch (error) {
            this.env.services.notification.add("Failed to call method.", { type: "danger" });
            console.error('RPC Error:', error);
        }
        */

        /*
        
        try {
            await this.rpc({
                model: 'cw.ocm.forecast',
                method: 'your_method',
                args: [[parseInt(recordId)]],
            });
            this.env.services.notification.add("Method called successfully!", { type: "success" });
        } catch (error) {
            this.env.services.notification.add("Failed to call method.", { type: "danger" });
            console.error('RPC Error:', error);
        }
        */
        
    }
}

HandleButtons.template = "cw_forecast_report.HandleButtons";

registry.category("fields").add("handle_buttons", {
    component: HandleButtons,
});
