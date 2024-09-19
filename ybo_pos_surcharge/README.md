# POS International Card Button Module

This Odoo 17 module adds a button labeled "INT" for international card payments in the POS interface. The button applies a percentage surcharge to the total amount of items selected in the POS. The percentage value is configurable by the admin in the POS settings.

## Features

- Adds an "INT" button for international card payments in the POS.
- Applies a configurable percentage surcharge to the total amount when the "INT" button is clicked.
- The percentage value can be modified by the admin in the POS settings.
- Ensures the surcharge amount is added as a separate line item in the order.

## Installation

1. Clone the module into your Odoo addons directory:
    ```bash
    git clone <repository_url> pos_int_card
    ```

2. Update the Odoo module list:
    ```bash
    ./odoo-bin -u all
    ```

3. Install the "POS International Card Button" module from the Apps menu in Odoo.

## Configuration

1. Go to the **Point of Sale** application.

2. Navigate to **Configuration > Point of Sale**.

3. Open the POS configuration where you want to add the "INT" button.

4. In the configuration form, find the new fields:
    - **International Card Percentage**: Set the percentage surcharge for international card payments.
    - **International Card Surcharge Product**: Select the product to be used for adding the surcharge amount.

## Usage

1. Open a POS session.

2. Add items to the order.

3. Click the "INT" button in the POS interface. This will add a surcharge to the order based on the configured percentage.

4. The surcharge amount will appear as a separate line item in the order.

## Files Structure

- **models/pos_config.py**: Adds the new fields to the POS configuration model.
- **views/pos_config_view.xml**: Updates the POS configuration form view to include the new fields.
- **static/src/js/int_card_button.js**: JavaScript file to handle the logic for the "INT" button.
- **static/src/xml/int_card_button.xml**: XML template for the "INT" button.
- **data/pos_data.xml**: Ensures the product for the surcharge exists.

## Customization

You can modify the surcharge percentage and the product used for the surcharge in the POS settings.

## Example

Assume the following configuration:
- **International Card Percentage**: 5%
- **International Card Surcharge Product**: "International Card Surcharge"

When the "INT" button is clicked on a $100 order, a 5% surcharge ($5) will be added as a separate line item, resulting in a total order amount of $105.

## License

This module is distributed under the GNU Affero General Public License (AGPL-3.0). See the LICENSE file for more details.

## Support

For any issues or questions regarding the module, please contact the support team at [odoo@cybrosys.com](mailto:odoo@cybrosys.com).

## Author

Developed by YBO Service. (Author: Mubarak)

## Acknowledgements

Special thanks to the Odoo community for their continuous support and contributions.

---

By following these instructions, you should be able to successfully install, configure, and use the "POS International Card Button" module in your Odoo 17 environment.
