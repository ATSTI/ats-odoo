odoo.define('pdv_barcode_search.ProductsWidgetBarcode', function (require) {
    'use strict';

    const ProductsWidget = require('point_of_sale.ProductsWidget');
    const Registries = require('point_of_sale.Registries');

    const ProductsWidgetBarcode = (ProductsWidget) =>
        class extends ProductsWidget {
            _tryAddProduct(event) {
                const searchWord = this.searchWord;

                if (searchWord) {
                    const parsedBarcode =
                        this.env.pos.barcode_reader.barcode_parser.parse_barcode(searchWord);

                    if (parsedBarcode.type !== 'error') {
                        this.env.pos.barcode_reader.scan(searchWord);

                        const { searchWordInput } = event.detail;
                        searchWordInput.el.value = '';
                        this._clearSearch();

                        return;
                    }
                }

                return super._tryAddProduct(event);
            }
        };

    Registries.Component.extend(ProductsWidget, ProductsWidgetBarcode);

    return ProductsWidgetBarcode;
});