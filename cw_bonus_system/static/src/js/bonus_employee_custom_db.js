/** @odoo-module */

import { PosDB } from "@point_of_sale/app/store/db";

export class BonusEmployeeCustomPosDB extends PosDB {
    constructor() {
        super();
        // Your custom initialization code here

        this.bonus_employee_sorted = [];
        this.bonus_employee_by_id = {};
        this.bonus_employee_search_strings = {};
    }

    get_bonus_employee_by_id(id) {
        return this.bonus_employee_by_id[id];
    }

    get_bonus_employee_sorted(max_count) {
        max_count = max_count
            ? Math.min(this.bonus_employee_sorted.length, max_count)
            : this.bonus_employee_sorted.length;
        var bonus_employees = [];
        for (var i = 0; i < max_count; i++) {
            bonus_employees.push(this.bonus_employee_by_id[this.bonus_employee_sorted[i]]);
        }
        return bonus_employees;
    }

    search_bonus_employee(query) {
        try {
            // eslint-disable-next-line no-useless-escape
            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g, ".");
            query = query.replace(/ /g, ".+");
            var re = RegExp("([0-9]+):.*?" + unaccent(query), "gi");
        } catch {
            return [];
        }
        var results = [];
        const searchStrings = Object.values(this.bonus_employee_search_strings).reverse();
        let searchString = searchStrings.pop();
        while (searchString && results.length < this.limit) {
            var r = re.exec(searchString);
            if (r) {
                var id = Number(r[1]);
                results.push(this.bonus_employee_by_id(id));
            } else {
                searchString = searchStrings.pop();
            }
        }
        return results;
    }
}