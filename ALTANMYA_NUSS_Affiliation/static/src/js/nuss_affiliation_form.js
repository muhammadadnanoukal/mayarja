odoo.define('ALTANMYA_NUSS_Affiliation.nuss_affiliation_form', function (require) {
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


publicWidget.registry.NUSSAffiliationForm = publicWidget.Widget.extend({
        template: 'auth_signup.signup, ALTANMYA_NUSS_Affiliation.nuss_signup_fields',
        selector: '.affiliation_form, .nuss_affiliation_form',
        events: {
            'change #NGO_affiliated': '_onChangeNGO',
            'change #party_affiliated': '_onChangePartyAffiliated',
            'change #university_id': '_onChangeUniversity',
            'change #college_id': '_onChangeCollege',
        },

        _onChangePartyAffiliated: function(){
            var input = document.getElementById("party_name");
            const partyNameLabel = document.querySelector('label[for="party_name"]');
            if (input.style.display === "none") {
              input.style.display = "block";
              partyNameLabel.style.display = "block";
              input.setAttribute('required', '');
            }
            else {
              input.value = '';
              input.style.display = "none";
              partyNameLabel.style.display = "none";
              input.removeAttribute('required');
            }

        },

        _onChangeNGO: function(){
            var input = document.getElementById("NGO_name");
            const NGONameLabel = document.querySelector('label[for="NGO_name"]');
            if (input.style.display === "none") {
              input.style.display = "block";
              NGONameLabel.style.display = "block";
              input.setAttribute('required', '');
            } else {
              input.value = '';
              input.style.display = "none";
              NGONameLabel.style.display = "none";
              input.removeAttribute('required');
            }
        },

        _getCollegesOptions: async function(universityID){
            let colleges = null;
            await rpc.query({
                    route: 'get_related_collages',
                    params: {
                        university_id: universityID,
                    },
            }).then((result) => {
                colleges = result;
            });

            if(colleges){
                return colleges;
            }
            return null;
        },

        _getDepartmentsOptions: async function(collegeID){
            console.log(collegeID)
            let departments = null;
            await rpc.query({
                    route : 'get_related_departments',
                    params: {
                        college_id: collegeID,
                    },
            }).then((result) => {
                departments = result;
            });

            if(departments){
                return departments;
            }
            return null;
        },

        _onChangeUniversity: async function(){
            const universitySelected = this.$('#university_id').find(":selected").val();
            const $college_id = this.$('#college_id').empty();
            const collegesOptions = await this._getCollegesOptions(universitySelected);
            $college_id.append('<option selected="selected" disabled="disabled" value="">Select a Collage / Institute</option>')
            for (var i = 0 ; i < collegesOptions.length ; i++) {
                $college_id.append($('<option/>', {
                    value: collegesOptions[i][0],
                    text: collegesOptions[i][1],
                }));
            }
        },

        _onChangeCollege: async function(){
            const collegeSelected = this.$('#college_id').find(":selected").val();
            const department_id = this.$('#department_id').empty();
            const departmentsOptions = await this._getDepartmentsOptions(collegeSelected);
            department_id.append('<option selected="selected" disabled="disabled" value="">Select a Department</option>')
            for (var i = 0 ; i < departmentsOptions.length ; i++) {
                department_id.append($('<option/>', {
                    value: departmentsOptions[i][0],
                    text: departmentsOptions[i][1],
                }));
            }
        },
    })
});