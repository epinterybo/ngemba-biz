from odoo import http
from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController
from odoo.http import request
from pprint import pformat
import logging

_logger = logging.getLogger(__name__)


class CustomProductConfiguratorController(ProductConfiguratorController):


    @http.route('/sale_product_configurator/get_values', type='json', auth='user')
    def get_product_configurator_values(
            self,
            product_template_id,
            quantity,
            currency_id,
            so_date,
            product_uom_id=None,
            company_id=None,
            pricelist_id=None,
            ptav_ids=None,
            only_main_product=False,
    ):
        result = super().get_product_configurator_values(
            product_template_id,
            quantity,
            currency_id,
            so_date,
            product_uom_id,
            company_id,
            pricelist_id,
            ptav_ids,
            only_main_product,
        )

        main_product = request.env['product.template'].browse(product_template_id)

        if not only_main_product:
            for i, optional_product in enumerate(result['optional_products']):
                optional_template = request.env['product.template'].browse(optional_product['product_tmpl_id'])
                if optional_template.ybo_is_warranty_product:
                    all_combinations = self._get_all_combinations(optional_template)
                    duration_variants = self._get_duration_variants(all_combinations)
                    modified_combinations = self._modify_warranty_product_info(
                        optional_product,
                        main_product,
                        duration_variants
                    )
                    result['optional_products'][i]['attribute_lines'][0]['attribute_values'] = modified_combinations

            # _logger.info(f"result: {pformat(result)}")
        return result

    def _get_all_combinations(self, product_template):
        all_combinations = []
        for combination in product_template._get_possible_combinations():
            all_combinations.append(combination)
        return all_combinations

    def _get_duration_variants(self, all_combinations):
        duration_variants = []
        for combination in all_combinations:
            if any(ptav.attribute_id.name == 'Duration' for ptav in combination):
                duration_variants.append(combination)
        return duration_variants

    def extract_numbers_using_join_isdigit(self, string):
        return ''.join([char for char in string if char.isdigit()])

    def _modify_warranty_product_info(self, product_info, main_product, warranty_combination):
        standard_warranty_months = main_product.categ_id.x_studio_cw_standardwarrantyinmonth
        warranty_cost_percent = main_product.categ_id.x_studio_cw_warrantycostforsixmonthpercent
        main_product_price = main_product.list_price

        modified_combinations = []
        for ptav in warranty_combination:
            price_extra = int(''.join(filter(str.isdigit, ptav.name)))
            if price_extra > standard_warranty_months:
                chosen_warranty = price_extra
                billable_duration = chosen_warranty - standard_warranty_months
                number_of_semesters = billable_duration / 6
                warranty_price = int(main_product_price * number_of_semesters * (warranty_cost_percent / 100))

                ptav.price_extra = warranty_price
                modified_combination = {
                    'id': ptav.id,
                    'name': ptav.name,
                    'html_color': False,
                    'image': False,
                    'is_custom': False,
                    'price_extra': ptav.price_extra,
                }

            else:
                modified_combination = {
                    'id': ptav.id,
                    'name': ptav.name,
                    'html_color': False,
                    'image': False,
                    'is_custom': False,
                    'price_extra': 0,
                }
            modified_combinations.append(modified_combination)

        return modified_combinations
