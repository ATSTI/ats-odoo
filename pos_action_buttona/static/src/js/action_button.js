// odoo.define('pos_action_button.ActionButton', function (require) {
// "use strict";

// //require pos screens
// const pos_screens = require('point_of_sale.screens');

// // create a new button by extending the base ActionButtonMidget
// const DashboardButton = pos_screens.ActionButtonWidget.extend({
//     template: "DashBoardButton",
//     button_click: function(){
//         alert("Dashboard button clicked");
//     },
// });


// // define the dashboard button
// pos_screens.define_action_button({
//     'name': 'Dashboard',
//     'widget': DashboardButton,
//     'condition': function(){return this.pos;},
// });

// });
odoo.define('pos_custom_buttons.PaymentScreenButton', function(require) {
    'use strict';
       const { Gui } = require('point_of_sale.Gui');
       const PosComponent = require('point_of_sale.PosComponent');
       const { posbus } = require('point_of_sale.utils');
       const ProductScreen = require('point_of_sale.ProductScreen');
       const { useListener } = require('web.custom_hooks');
       const Registries = require('point_of_sale.Registries');
       const PaymentScreen = require('point_of_sale.PaymentScreen');
        const CustomButtonPaymentScreen = (PaymentScreen) =>
           class extends PaymentScreen {
               constructor() {
                   super(...arguments);
               }
               IsCustomButton() {
                   // click_invoice
                    Gui.showPopup("ErrorPopup", {
                           title: this.env._t('Payment Screen Custom Button Clicked'),
                           body: this.env._t('Welcome to OWL'),
                       });
               }
           };
       Registries.Component.extend(PaymentScreen, CustomButtonPaymentScreen);
       return CustomButtonPaymentScreen;
    });
