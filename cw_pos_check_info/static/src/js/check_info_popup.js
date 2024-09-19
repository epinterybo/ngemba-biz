//** @odoo-module */

import {AbstractAwaitablePopup} from "@point_of_sale/app/popup/abstract_awaitable_popup";
import {_t} from "@web/core/l10n/translation";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {useService} from "@web/core/utils/hooks";
import {useState} from "@odoo/owl";


export class CheckInfoPopup extends AbstractAwaitablePopup {
    static template = "cw_pos_check_info.CheckInfoPopup";
    static defaultProps = {
        confirmText: _t("Apply"),
        title: _t(""),
        body: '',
        cancelText: _t("Cancel"),
    };

    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
        // this.state = useState({ array: this._initialize(this.props.array) });
        this.state = useState({
            check_number: '',
            bank_account: '',
            owner_name: '',
            bank_name: '',
        })
    }

    mounted() {
        $('#del_date').datetimepicker({
            format: 'YYYY-MM-DD HH:mm:ss',
            inline: true,
            sideBySide: true
        });
    }

    async select() {
        this.props.close({confirmed: true, payload: null});
    }

    confirm() {
        // var owner_name = document.getElementById("owner_name").value;
        var check_number = document.getElementById("check_number").value;
        var bank_account = document.getElementById("bank_account").value;
        if (!check_number || !bank_account) {
            alert("Please Fill Check Details !!")
        } else {
            return super.confirm();
        }
    }

    cancel() {
        this.props.close({confirmed: false, payload: null});
    }

    getPayload() {
        return {
            newArray: this.state.array
//                    .filter((item) => item.text.trim() !== '')
//                    .map((item) => Object.assign({}, item)),
        };
    }
}
