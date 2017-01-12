/**
 * author: minhld
 */

odoo.define('cnf_point_of_sale.screen', function (require) {
"use strict";
    var core = require('web.core');
    // var QWeb = core.qweb;
    // var _t = core._t;
    var gui = require('point_of_sale.gui');
    // var Model = require('web.DataModel');

    var screens_req = require('point_of_sale.screens');
    // var _super_ReceiptScreen = screens_req.ReceiptScreenWidget.prototype;


    screens_req.ReceiptScreenWidget.include({
        show: function(){
            this._super();
            // var self = this;

            // this.render_change();
            // this.render_receipt();

            // if (this.should_auto_print()) {
            //     this.print();
            //     if (this.should_close_immediately()){
            //         this.click_next();
            //     }
            // } else {
            //     this.lock_screen(false);
            // }

            this.print();
            this.$('.next').click();

        },
        print: function() {
            var self = this;

            if (!this.pos.config.iface_print_via_proxy) { // browser (html) printing

                // The problem is that in chrome the print() is asynchronous and doesn't
                // execute until all rpc are finished. So it conflicts with the rpc used
                // to send the orders to the backend, and the user is able to go to the next
                // screen before the printing dialog is opened. The problem is that what's
                // printed is whatever is in the page when the dialog is opened and not when it's called,
                // and so you end up printing the product list instead of the receipt...
                //
                // Fixing this would need a re-architecturing
                // of the code to postpone sending of orders after printing.
                //
                // But since the print dialog also blocks the other asynchronous calls, the
                // button enabling in the setTimeout() is blocked until the printing dialog is
                // closed. But the timeout has to be big enough or else it doesn't work
                // 1 seconds is the same as the default timeout for sending orders and so the dialog
                // should have appeared before the timeout... so yeah that's not ultra reliable.

                // this.lock_screen(true);
                //
                // setTimeout(function(){
                //     self.lock_screen(false);
                // }, 1000);

                this.print_web();
            } else {    // proxy (xml) printing
                this.print_xml();
                this.lock_screen(false);
            }
        },
    });
});
