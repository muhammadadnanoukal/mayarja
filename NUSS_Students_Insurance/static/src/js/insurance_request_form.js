odoo.define('NUSS_Students_Insurance.insurance_request_form', function (require) {
'use strict';
    var core = require('web.core');
    const dom = require('web.dom');

    var _t = core._t;

    var Dialog = require('web.Dialog');
    var publicWidget = require('web.public.widget');
    var currentPage = 1;
    var numPages = 3;
    var ajax = require('web.ajax');
    var qweb = core.qweb;
    var rpc = require('web.rpc');


publicWidget.registry.InsuranceRequestForm = publicWidget.Widget.extend({
        template: 'NUSS_Student_Insurance.s_website_form_status_otp_success, NUSS_Student_Insurance.s_website_form_status_otp_failure',
        selector: '.insurance_request_form, .insurance_payment_operation_form, .insurance_payment_operation_otp_form',
        events: {
            'click #previous-button': '_onClickPreviousButton',
            'click #next-button': '_onClickNextButton',
            'click #submit-button': '_onSubmit',
            'click #payment-submit-button': '_onPaymentSubmit',
            'click #otp-submit-button': '_onOTPSubmit',
            'click #resend-otp-button': '_onResendOTPSubmit',
            'change #university': '_onChangeUniversity',
        },

        _onResendOTPSubmit: function(e){
            var self = this
            e.preventDefault();
            var operationID = $('input[name="payment_operation_id"]').val();
            $.ajax({
                type: 'GET',
                url: '/resend_otp/' + operationID,
                success: function(data) {
                    var $result = self.$('#s_website_form_result, #o_website_form_result');
                        var message = _t("لقد تمت إعادة إرسال الرمز بشكل صحيح!")
                        $result.replaceWith(qweb.render(`NUSS_Student_Insurance.s_website_form_status_otp_success`, {
                            message: message,
                    }))
                },
                error: function (jqXHR, status, err) {
                    var $result = self.$('#s_website_form_result, #o_website_form_result');
                        var message = _t("لم تتم عملية إعادة إرسال الرمز بشكل صحيح!")
                        $result.replaceWith(qweb.render(`NUSS_Student_Insurance.s_website_form_status_otp_failure`, {
                            message: message,
                    }))
                },
            });
        },

        _onOTPSubmit: function(e){
            e.preventDefault();
            const $button = this.$target.find('#otp-submit-button');
            $button.addClass('disabled')
                   .attr('disabled', 'disabled');
            this.restoreBtnLoading = dom.addButtonLoadingEffect($button[0]);

            var self = this;

            self.$target.find('#s_website_form_result, #o_website_form_result').empty();
            if (!self.check_error_fields({})) {
                self.update_status('error', _t("Please fill in the form correctly."));
                return false;
            }
            this.$('form').submit();
        },

        _onPaymentSubmit: function(e){
            e.preventDefault();
            const $button = this.$target.find('#payment-submit-button');
            console.log($button)
            $button.addClass('disabled')
                   .attr('disabled', 'disabled');
            this.restoreBtnLoading = dom.addButtonLoadingEffect($button[0]);

            var self = this;

            self.$target.find('#s_website_form_result, #o_website_form_result').empty();
            if (!self.check_error_fields({})) {
                self.update_status('error', _t("Please fill in the form correctly."));
                return false;
            }
            this.$('form').submit();
        },

        _onSubmit: function(e) {
            e.preventDefault();
            const $button = this.$target.find('#submit-button');
            console.log($button)
            $button.addClass('disabled')
                   .attr('disabled', 'disabled');
            this.restoreBtnLoading = dom.addButtonLoadingEffect($button[0]);

            var self = this;

            self.$target.find('#s_website_form_result, #o_website_form_result').empty();
            if (!self.check_error_fields({})) {
                self.update_status('error', _t("Please fill in the form correctly."));
                return false;
            }
            this.$('form').submit();
        },

        check_error_fields_current_page: function (error_fields, div_name) {
            var self = this;
            var form_valid = true;
            this.$target.find(div_name).each(function (k, field) { // !compatibility
                var $field = $(field);
                var field_name = $field.find('.col-form-label').attr('for');
                var inputs = $field.find('.s_website_form_input, .o_website_form_input').not('#editable_select'); // !compatibility
                var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
                    if (input.required && input.type === 'checkbox') {
                        var checkboxes = _.filter(inputs, function (input) {
                            return input.required && input.type === 'checkbox';
                        });
                        return !_.any(checkboxes, checkbox => checkbox.checkValidity());
                    }
                    return !input.checkValidity();
                });
                const $controls = $field.find('.form-control, .form-select, .form-check-input, .form-control-file');
                $field.removeClass('o_has_error');
                $controls.removeClass('is-invalid');
                if (invalid_inputs.length || error_fields[field_name]) {
                    $field.addClass('o_has_error');
                    $controls.addClass('is-invalid');
                    if (_.isString(error_fields[field_name])) {
                        $field.popover({content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top'});
                        $field.data("bs.popover").config.content = error_fields[field_name];
                        $field.popover('show');
                    }
                    form_valid = false;
                }
            });
            return form_valid;
        },

        check_error_fields: function (error_fields) {
            var self = this;
            var form_valid = true;
            this.$target.find('.form-field, .s_website_form_field').each(function (k, field) { // !compatibility
                var $field = $(field);
                var field_name = $field.find('.col-form-label').attr('for');
                var inputs = $field.find('.s_website_form_input, .o_website_form_input').not('#editable_select'); // !compatibility
                var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
                    if (input.required && input.type === 'checkbox') {
                        var checkboxes = _.filter(inputs, function (input) {
                            return input.required && input.type === 'checkbox';
                        });
                        return !_.any(checkboxes, checkbox => checkbox.checkValidity());
                    }

                    return !input.checkValidity();
                });
                const $controls = $field.find('.form-control, .form-select, .form-check-input, .form-control-file');
                $field.removeClass('o_has_error');
                $controls.removeClass('is-invalid');
                if (invalid_inputs.length || error_fields[field_name]) {
                    $field.addClass('o_has_error');
                    $controls.addClass('is-invalid');
                    if (_.isString(error_fields[field_name])) {
                        $field.popover({content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top'});
                        $field.data("bs.popover").config.content = error_fields[field_name];
                        $field.popover('show');
                    }
                    form_valid = false;
                }
            });
            return form_valid;
        },

        update_status: function (status, message) {
            if (status === 'otp_error'){
                var $result = this.$('#s_website_form_result, #o_website_form_result');
                if (status === 'error' && !message) {
                    message = _t("An error has occured, the form has not been sent.");
                }
                $result.replaceWith(qweb.render(`website.s_website_form_status_${status}`, {
                    message: message,
                }))
            }
            if (status !== 'success') {
                this.$target.find('.submitButton')
                    .removeAttr('disabled')
                    .removeClass('disabled');
                this.restoreBtnLoading();
            }
            var $result = this.$('#s_website_form_result, #o_website_form_result');
            if (status === 'error' && !message) {
                message = _t("An error has occured, the form has not been sent.");
            }
            $result.replaceWith(qweb.render(`website.s_website_form_status_${status}`, {
                message: message,
            }))
        },

        init: function (){
            this.__started = new Promise(resolve => this.__startResolve = resolve);
        },

        start: async function () {
            $('#previous-button').hide();
            $('#next-button').show();
            $('#submit-button').hide();
            $('.page').hide();
            $('#page-' + currentPage).show();
            return this._super.apply(this, arguments);
        },

        _onClickPreviousButton: function() {
            if (currentPage > 1) {
                $('#previous-button').show();
                $('#submit-button').hide();
                $('#next-button').show();
                currentPage--;
                if (currentPage === 1){
                   $('#previous-button').hide();
                }
                $('.page').hide();
                $('#page-' + currentPage).show();
            }
            else{
                $('#previous-button').hide();
            }
        },

        _onClickNextButton: function() {
            if (currentPage < numPages) {
            if (!this.check_error_fields_current_page({}, '#page-' + currentPage)) {
                    alert('يرجى ملئ الحقول بشكل صحيح')
                    return false
                }
                $('#previous-button').show();
                $('#submit-button').hide();
                currentPage++;
                if (currentPage === numPages){
                    $('#next-button').hide();
                    $('#submit-button').show();
                }
                $('.page').hide();
                $('#page-' + currentPage).show();
            }
        },

        _getCollagesOptions: async function(universityID){
            let collages = null;
            await rpc.query({
                    model: 'in.university',
                    method : 'get_related_collages',
                    args: [universityID],
            }).then((result) => {
                collages = result;
            });

            if(collages){
                return collages;
            }
            console.log(collages)
            return null;
        },

        _onChangeUniversity: async function(){
            const universitySelected = this.$('#university').find(":selected").val();
            const $collage = this.$('#collage').empty();
            const collagesOptions = await this._getCollagesOptions(universitySelected);
            for (var i = 0 ; i < collagesOptions.length ; i++) {
                $collage.append($('<option/>', {
                    value: collagesOptions[i][0],
                    text: collagesOptions[i][1],
                }));
            }
        },

    })
});