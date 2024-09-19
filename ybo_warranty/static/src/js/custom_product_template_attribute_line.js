/** @odoo-module */
import {patch} from "@web/core/utils/patch";
import {Component, onWillStart, useState, useSubEnv} from "@odoo/owl";
import {
    ProductTemplateAttributeLine
} from "@sale_product_configurator/js/product_template_attribute_line/product_template_attribute_line";


// patch(ProductTemplateAttributeLine.prototype, {
//     async getPTAVSelectName(ptav) {
//
//         console.log('Is warranty product: HELLO');
//         return await super.getPTAVSelectName(...arguments);;
//     }
// });


class CustomProductTemplateAttributeLine extends Component {
    static components = {ProductTemplateAttributeLine}
    setup() {
        super.setup();
        console.log(this.refs.numericInput.props);
    }
}

//

// import {
//     ProductTemplateAttributeLine
// } from "@sale_product_configurator/js/product_template_attribute_line/product_template_attribute_line";
//
// const CustomProductTemplateAttributeLine = {
//     ...ProductTemplateAttributeLine,
//     props: {
//         ...ProductTemplateAttributeLine.props,
//         combinations: {
//             type: Array,
//             element: {
//                 type: Object,
//                 shape: {
//                     id: Number,
//                     name: String,
//                     price_extra: Number,
//                 },
//             },
//         },
//         is_warranty_product: Boolean,
//     },
//     async getPTAVSelectName(ptav) {
//         console.log('Is warranty product:', this.props.archived_combinations);
//         // console.log('Combinations:', this.props.combinations);
//         // return result;
//         return await super.getPTAVSelectName(...arguments);
//     },
// };
//
// patch(ProductTemplateAttributeLine.prototype, CustomProductTemplateAttributeLine);

// const CustomProductTemplateAttributeLine = {
//     ...ProductTemplateAttributeLine,
//     props: {
//         ...ProductTemplateAttributeLine.props,
//         combinations: {
//             type: Array,
//             element: {
//                 type: Object,
//                 shape: {
//                     id: Number,
//                     name: String,
//                     price_extra: Number,
//                 },
//             },
//         },
//         is_warranty_product: Boolean,
//     },
// async getPTAVSelectName(ptav) {
// console.log(`Is warranty product: HELLO`);
// return await super.getPTAVSelectName(...arguments);
/*if (this.props.is_warranty_product) {
    const combination = this.props.combinations.find(combination => combination.id === ptav.id);
    if (combination) {
        const sign = combination.price_extra > 0 ? '+' : '-';
        const price = formatCurrency(
            Math.abs(combination.price_extra), this.env.currencyId
        );
        return ptav.name + " (" + sign + " " + price + ")";
    } else {
        return ptav.name;
    }
} else {
    if (ptav.price_extra) {
        const sign = ptav.price_extra > 0 ? '+' : '-';
        const price = formatCurrency(
            Math.abs(ptav.price_extra), this.env.currencyId
        );
        return ptav.name + " (" + sign + " " + price + ")";
    } else {
        return ptav.name;
    }
}*/
// }
// ,
// };

// patch(ProductTemplateAttributeLine.prototype, CustomProductTemplateAttributeLine);
