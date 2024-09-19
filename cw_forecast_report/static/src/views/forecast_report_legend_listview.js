/** @odoo-module **/


import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { ForecastReportLegend } from '@cw_forecast_report/views/forecast_report_legend';
import { ListController } from "@web/views/list/list_controller";
import { Component } from "@odoo/owl";

class ForecastReportController extends ListController {
    setup() {
        super.setup();
        console.log("Setup on button being done here");
        //this.on("click", this.onButtonClick.bind(this), { delegate: ".o_list_button_copy_name" });
        //this._registerEventHandlers();
    }

    _registerEventHandlers() {
        this.el.addEventListener("click", this._onButtonClick.bind(this), true);
    }

    _onButtonClick(event) {
        console.log("Button Clicked at this stage");
        if (event.target.classList.contains("o_list_button_copy_name")) {
            console.log("Button Clicked at this stage 02");
            const recordId = event.target.closest("tr").dataset.id;
            const record = this.model.get(recordId);
            const productName = record.data.product_id.data.display_name;
            navigator.clipboard.writeText(productName).then(() => {
                this.displayNotification({ message: "Product name copied to clipboard!", type: "success" });
            }).catch(err => {
                this.displayNotification({ message: "Failed to copy product name.", type: "danger" });
                console.error('Could not copy text: ', err);
            });
        }
    }

    /*
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
    */
}


class CopyProductName extends Component {
    setup() {
        this.env.bus.on('ACTION_COPY_PRODUCT_NAME', this, this._copyProductName);
        console.log("Setup CopyProductName Action Here");
    }

    _copyProductName(params) {
        const productName = params.product_name;
        navigator.clipboard.writeText(productName).then(() => {
            this.env.services.notification.add("Product name copied to clipboard!", { type: "success" });
        }).catch(err => {
            this.env.services.notification.add("Failed to copy product name.", { type: "danger" });
            console.error('Could not copy text: ', err);
        });
    }
}

/*
ForecastReportController.components = {
    ...ListController.components,
    CopyProductName,
}
*/

export class ForecastReportLegendRenderer extends ListRenderer {};


ForecastReportLegendRenderer.template = 'cw_forecast_report.ForecastReportLegendListView';
ForecastReportLegendRenderer.components= Object.assign({}, ListRenderer.components, {ForecastReportLegend})


export const ForecastReportLegendListView = {
    ...listView,
    Controller: ForecastReportController,
    Renderer: ForecastReportLegendRenderer,
};


registry.category("views").add("forecast_report_legend", ForecastReportLegendListView);
//registry.category("services").add("copy_product_name", CopyProductName);