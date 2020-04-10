# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import werkzeug
from datetime import datetime
from math import ceil

from odoo import fields, http, SUPERUSER_ID,_
from odoo.http import request
from odoo.tools import ustr

_logger = logging.getLogger(__name__)


class WebsiteSurvey(http.Controller):


    def _check_bad_cases(self, survey, token=None):
        # In case of bad survey, redirect to surveys list
        if not survey.sudo().exists():
            return werkzeug.utils.redirect("/survey/")

        # In case of auth required, block public user
        if survey.auth_required and request.env.user == request.website.user_id:
            return request.render("survey.auth_required", {'survey': survey, 'token': token})

        # In case of non open surveys
        if survey.stage_id.closed:
            return request.render("survey.notopen")

        # If there is no pages
        if not survey.page_ids:
            return request.render("survey.nopages", {'survey': survey})

        # Everything seems to be ok
        return None

    def _check_deadline(self, user_input):
        '''Prevent opening of the survey if the deadline has turned out

        ! This will NOT disallow access to users who have already partially filled the survey !'''
        deadline = user_input.deadline
        if deadline:
            dt_deadline = fields.Datetime.from_string(deadline)
            dt_now = datetime.now()
            if dt_now > dt_deadline:  # survey is not open anymore
                return request.render("survey.notopen")
        return None

    # Survey start
    @http.route(['/survey/start/po/<model("survey.survey"):survey>/<string:po>' ],
                type='http', auth='public', website=True)
    def start_survey_po(self, survey, po=None , **post):
        context = dict(request.context)
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey, token=None)
        if errpage:
            return errpage

        # Manual surveying
        vals = {'survey_id': survey.id, 'purchase_order_id':int(po)}
        if request.website.user_id != request.env.user:
            vals['partner_id'] = request.env.user.partner_id.id
        user_input = UserInput.create(vals)

        # Do not open expired survey
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = {'survey': survey, 'page': None, 'token': user_input.token, 'po':po}
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s/%s' % (survey.id, user_input.token, po))

    @http.route(['/survey/fill/po/<model("survey.survey"):survey>/<string:token>/<string:po>',
                 '/survey/fill/po/<model("survey.survey"):survey>/<string:token>/<string:prev>'],
                type='http', auth='public', website=True)
    def fill_survey_po(self, survey, token, prev=None, po=None, **post):
        '''Display and validates a survey'''
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']
        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey)
        if errpage:
            return errpage

        # Load the user_input
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        if not user_input:  # Invalid token
            return request.render("website.403")

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page+ 1
        if user_input.state == 'new':  # First page
            print ("/%%%%%%%%%%%%%%%%%%%%%%%%%%%",user_input.user_input_line_ids.value_suggested)
            
            page, page_nr, last = Survey.next_page(user_input, 0, go_back=False)
            print ("<<<<<<<<<<<<<<<<<<if<<<<<<<<<<<<<<",page, page_nr, last)
            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'po':po}
            
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        elif user_input.state == 'done':  # Display success message
            return request.render('survey.sfinished', {'survey': survey,
                                                       'token': token,
                                                       'user_input': user_input,
                                                       'po':po})
            print ("<<<<<<<<<<elif<<<<<<<<<")
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            print ("<<<<<botuser_input, user_input.last_displayed_page_id.id<<<",user_input, user_input.last_displayed_page_id.id)

            page, page_nr, last = Survey.with_context(purchase_survey=True).next_page(user_input, user_input.last_displayed_page_id.id, go_back=flag)
            print ("<<<<<<<<el<<page, page_nr, last<<<<<<<<<",page, page_nr, last)
            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page:
                page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=True)

            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'po':po}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        else:
            return request.render("website.403")
    @http.route(['/survey/submit/po/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit_po(self, survey, **post):
        _logger.debug('Incoming data: %s', post)
        page_id = int(post['page_id'])
        
        po_obj = request.env['purchase.order']
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])

        # Answer validation
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
            except KeyError:  # Invalid token
                return request.render("website.403")
            user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                request.env['survey.user_input_line'].sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)
            go_back = post['button_submit'] == 'previous'
            line_send_mail_ids =[]
            page_continue_ids=[]
            if user_input:
                for x in user_input.user_input_line_ids:
                    if x.page_id.id == page_id:
                        if x.value_suggested.execution_type:
                            if x.value_suggested.execution_type == 'continue':
                                if x.value_suggested.page_question_id:
                                    page_continue_ids.append(x.value_suggested.page_question_id.id)
                            elif x.value_suggested.execution_type == 'send_mail': 
                                print ("^^^^^^^^^send_maile^^^^^^^^^^^^^")
                                line_send_mail_ids.append(x.id)
                                if x.value_suggested.controller_id:
                                    print ("*************************")
                            
            '''answers = [x.value_suggested.execution_type for x in user_input.user_input_line_ids if x.page_id.id == page_id]
                
                if 'send_mail' in  answers:
                    user_input.with_context(purchase=True).write({'execution_type':'send_mail'})
                else :
                    po_brw = po_obj.browse(int(post['po']))
                    po_brw.state = 'check_compliance'''
            '''if page_continue_ids:
                print ("&*************************^^^^^^^^^^",page_continue_ids)
                page_id = page_continue_ids[-1]'''
            next_page, _, last = request.env['survey.survey'].with_context(user_input=user_input).next_page(user_input, page_id, go_back=go_back)
            print ("^%&&&&&&&&&next_page, _, last&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",next_page, _, last)
            vals = {'last_displayed_page_id': page_id}
            if next_page is None and not go_back:
                vals.update({'state': 'done'})
            else:
                vals.update({'state': 'skip'})
            user_input.sudo(user=user_id).write(vals)
           
            ret['redirect'] = '/survey/fill/po/%s/%s/%s' % (survey.id, post['token'], post['po'])
            if go_back:
                ret['redirect'] += '/prev'
        return json.dumps(ret)



    '''@http.route(['/survey/submit/po/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit_po(self, survey, **post):
        _logger.debug('Incoming data: %s', post)
        print ("========================================================",post)
        page_id = int(post['page_id'])
        
        po_obj = request.env['purchase.order']
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])

        # Answer validation
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
            except KeyError:  # Invalid token
                return request.render("website.403")
            user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                request.env['survey.user_input_line'].sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)
            print ("******************************************page_id",page_id)
            go_back = post['button_submit'] == 'previous'
            line_send_mail_ids =[]
            page_continue_ids=[]
            if user_input:
                print ("^^^^^^^^^^^user_input.user_input_line_ids^^^^^^^^^^^",user_input.user_input_line_ids)
                for x in user_input.user_input_line_ids:
                    print ("IIIIIIIIIIIIIIIIIIIIIIASssssssssssssss",x.page_id.id)
                    if x.page_id.id == page_id:
                        if x.value_suggested.execution_type:
                            if x.value_suggested.execution_type == 'continue':
                                print (">>>>>>>>>>>>>>>>>>>>continue>>>>>>>>")
                                if x.value_suggested.page_question_id:
                                    page_continue_ids.append(x.value_suggested.page_question_id.id)
                                    print ("-=========page_id===========continue===========",page_continue_ids)
                            elif x.value_suggested.execution_type == 'send_mail': 
                                print ("^^^^^^^^^send_maile^^^^^^^^^^^^^")
                                line_send_mail_ids.append(x.id)
                                if x.value_suggested.controller_id:
                                    print ("*************************")
                            
            print ("-=========page_id======================",page_id, line_send_mail_ids)      
            print ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",page_continue_ids)
            if page_continue_ids:
                print ("&*************************^^^^^^^^^^",page_continue_ids)
                page_id = page_continue_ids[-1]
            next_page, _, last = request.env['survey.survey'].with_context(purchase_survey=True).next_page(user_input, page_id, go_back=go_back)
            print ("^%&&&&&&&&&next_page, _, last&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",next_page, _, last)
            vals = {'last_displayed_page_id': page_id}
            if line_send_mail_ids:
                next_page = None
                line_send_mail_ids = []
            if next_page is None and not go_back:
                vals.update({'state': 'done'})
            else:
                vals.update({'state': 'skip'})
            user_input.sudo(user=user_id).write(vals)
           
            ret['redirect'] = '/survey/fill/po/%s/%s/%s' % (survey.id, post['token'], post['po'])
            if go_back:
                ret['redirect'] += '/prev'
        return json.dumps(ret)'''
    
        # Survey start
    @http.route(['/survey/start/so/<model("survey.survey"):survey>/<string:so>' ],
                type='http', auth='public', website=True)
    def start_survey_so(self, survey, so=None , **post):
        context = dict(request.context)
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey, token=None)
        if errpage:
            return errpage

        # Manual surveying
        vals = {'survey_id': survey.id, 'sale_order_id':int(so)}
        if request.website.user_id != request.env.user:
            vals['partner_id'] = request.env.user.partner_id.id
        user_input = UserInput.create(vals)

        # Do not open expired survey
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = {'survey': survey, 'page': None, 'token': user_input.token, 'so':so}
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s/%s' % (survey.id, user_input.token, so))

    @http.route(['/survey/fill/so/<model("survey.survey"):survey>/<string:token>/<string:so>',
                 '/survey/fill/so/<model("survey.survey"):survey>/<string:token>/<string:prev>'],
                type='http', auth='public', website=True)
    def fill_survey_so(self, survey, token, prev=None, so=None, **post):
        '''Display and validates a survey'''
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey)
        if errpage:
            return errpage

        # Load the user_input
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        if not user_input:  # Invalid token
            return request.render("website.403")

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # First page
            page, page_nr, last = Survey.next_page(user_input, 0, go_back=False)
            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'so':so}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        elif user_input.state == 'done':  # Display success message
            return request.render('survey.sfinished', {'survey': survey,
                                                       'token': token,
                                                       'user_input': user_input,
                                                       'so':so})
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=flag)

            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page:
                page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=True)

            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'so':so}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        else:
            return request.render("website.403")


    @http.route(['/survey/submit/so/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit_so(self, survey, **post):
        so_obj = request.env['sale.order']
        _logger.debug('Incoming data: %s', post)
        page_id = int(post['page_id'])
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])

        # Answer validation
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
            except KeyError:  # Invalid token
                return request.render("website.403")
            user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                request.env['survey.user_input_line'].sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)

            go_back = post['button_submit'] == 'previous'
            next_page, _, last = request.env['survey.survey'].next_page(user_input, page_id, go_back=go_back)
            vals = {'last_displayed_page_id': page_id}
            if next_page is None and not go_back:
                vals.update({'state': 'done'})
            else:
                vals.update({'state': 'skip'})
            user_input.sudo(user=user_id).write(vals)
            if user_input:
                answers = [x.value_suggested.value for x in user_input.user_input_line_ids ]
                line_send_mail_ids = []
                line_continue_ids =[]
                for x in user_input.user_input_line_ids:
                    incidents_manager_id = False
                    incidents_manager = False
                    if x.page_id.id == page_id:
                        if  x.value_suggested.execution_type == 'send_mail': 
                            line_send_mail_ids.append(x.id)
                            if x.value_suggested.controller_id:
                                incidents_manager_id = x.value_suggested.controller_id.id
                                incidents_manager = x.value_suggested.controller_id.user_id.partner_id.id
                        elif x.value_suggested.execution_type == 'continue':
                            line_continue_ids.append(x.id)
                print ("_-------------------",line_send_mail_ids)
                if line_send_mail_ids:
                    user_id = request.env.uid
                    search_emp_id = request.env['hr.employee'].search([('user_id','=',user_id )])
                    user_brw = request.env['res.users'].browse(user_id)
                    mail_val = {
	                          'subject':'Incident Created',
	                          'body': ('Incident Created BY %s .')%(user_brw.name,),
	                          'author_id':user_brw.partner_id.id,
	                           'email_from': user_brw.login ,
	                           'message_type':'email',
	                           'model':'sale.order',
	                           'partner_ids':[(6,0, [incidents_manager or search_emp_id.incidents_manager_id.user_id.partner_id.id ] )] or False, 
	                           'res_id': user_input.sale_order_id.id
	                            }
                    request.env['mail.message'].create(mail_val)
                else : 
                    sale_brw =so_obj.browse(int(post['so']))
                    sale_brw.state = 'check_compliance'
            ret['redirect'] = '/survey/fill/so/%s/%s/%s' % (survey.id, post['token'], post['so'])
            if go_back:
                ret['redirect'] += '/prev'
        return json.dumps(ret)



    # Container Survey start
    @http.route(['/survey/start/wash/<model("survey.survey"):survey>/<string:wash>' ],
                type='http', auth='public', website=True)
    def start_survey_wash(self, survey, wash=None , **post):
        context = dict(request.context)
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey, token=None)
        if errpage:
            return errpage

        # Manual surveying
        vals = {'survey_id': survey.id, 'wash_order_id':int(wash)}
        if request.website.user_id != request.env.user:
            vals['partner_id'] = request.env.user.partner_id.id
        user_input = UserInput.create(vals)

        # Do not open expired survey
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = {'survey': survey, 'page': None, 'token': user_input.token, 'wash':wash}
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s/%s' % (survey.id, user_input.token, wash))

    @http.route(['/survey/fill/wash/<model("survey.survey"):survey>/<string:token>/<string:wash>',
                 '/survey/fill/wash/<model("survey.survey"):survey>/<string:token>/<string:prev>'],
                type='http', auth='public', website=True)
    def fill_survey_wash(self, survey, token, prev=None, wash=None, **post):
        '''Display and validates a survey'''
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey)
        if errpage:
            return errpage

        # Load the user_input
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        if not user_input:  # Invalid token
            return request.render("website.403")

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # First page
            page, page_nr, last = Survey.next_page(user_input, 0, go_back=False)
            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'wash':wash}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        elif user_input.state == 'done':  # Display success message
            return request.render('survey.sfinished', {'survey': survey,
                                                       'token': token,
                                                       'user_input': user_input,
                                                       'wash':wash})
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=flag)

            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page:
                page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=True)

            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'wash':wash}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        else:
            return request.render("website.403")


    @http.route(['/survey/submit/wash/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit_wash(self, survey, **post):
        wash_obj = request.env['wash.order']
        _logger.debug('Incoming data: %s', post)
        print ("xxxxxxxxxxxxxxxxx",post)
        page_id = int(post['page_id'])
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])

        # Answer validation
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
            except KeyError:  # Invalid token
                return request.render("website.403")
            user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                request.env['survey.user_input_line'].sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)

            go_back = post['button_submit'] == 'previous'
            next_page, _, last = request.env['survey.survey'].next_page(user_input, page_id, go_back=go_back)
            vals = {'last_displayed_page_id': page_id}
            if next_page is None and not go_back:
                vals.update({'state': 'done'})
            else:
                vals.update({'state': 'skip'})
            user_input.sudo(user=user_id).write(vals)
            wash_brw = wash_obj.browse(int(post['wash']))
            user_id = request.env.uid
            search_emp_id = request.env['hr.employee'].search([('user_id','=',user_id )])
            user_brw = request.env['res.users'].browse(user_id)
            if user_input:
                answers = [x.value_suggested.value for x in user_input.user_input_line_ids ]
                line_send_mail_ids = []
                line_continue_ids =[]
                incidents_manager_id = False
                incidents_manager = False
                for x in user_input.user_input_line_ids:
                    
                    if x.page_id.id == page_id:
                        if  x.value_suggested.execution_type == 'send_mail': 
                            line_send_mail_ids.append(x.id)
                            if x.value_suggested.controller_id:
                                incidents_manager_id = x.value_suggested.controller_id.id
                                incidents_manager = x.value_suggested.controller_id.user_id.partner_id.id
                        elif x.value_suggested.execution_type == 'continue':
                            line_continue_ids.append(x.id)
                if line_send_mail_ids:
                    if wash_brw.type_of_order == 'container':
                        wash_brw.state = 'check_compliance'
                elif line_continue_ids: 
                    if wash_brw.type_of_order == 'container':
                        wash_brw.state = 'quality_control'  
            ret['redirect'] = '/survey/fill/wash/%s/%s/%s' % (survey.id, post['token'], post['wash'])
            if go_back:
                ret['redirect'] += '/prev'
        return json.dumps(ret)


    @http.route(['/survey/start/drum/<model("survey.survey"):survey>/<string:drum>' ],
                type='http', auth='public', website=True)
    def start_survey_drum(self, survey, drum=None , **post):
        context = dict(request.context)
        print ("cccccccccccpostcontextccccccc",context,post)
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey, token=None)
        if errpage:
            return errpage

        # Manual surveying
        vals = {'survey_id': survey.id, 'wash_order_id':int(drum)}
        if request.website.user_id != request.env.user:
            vals['partner_id'] = request.env.user.partner_id.id
        user_input = UserInput.create(vals)

        # Do not open expired survey
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = {'survey': survey, 'page': None, 'token': user_input.token, 'drum':drum}
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s/%s' % (survey.id, user_input.token, drum))

    @http.route(['/survey/fill/drum/<model("survey.survey"):survey>/<string:token>/<string:drum>',
                 '/survey/fill/drum/<model("survey.survey"):survey>/<string:token>/<string:prev>'],
                type='http', auth='public', website=True)
    def fill_survey_drum(self, survey, token, prev=None, drum=None, **post):
        '''Display and validates a survey'''
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey)
        if errpage:
            return errpage

        # Load the user_input
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        if not user_input:  # Invalid token
            return request.render("website.403")

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # First page
            page, page_nr, last = Survey.next_page(user_input, 0, go_back=False)
            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'drum':drum}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        elif user_input.state == 'done':  # Display success message
            return request.render('survey.sfinished', {'survey': survey,
                                                       'token': token,
                                                       'user_input': user_input,
                                                       'drum':drum})
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=flag)

            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page:
                page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=True)

            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'drum':drum}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        else:
            return request.render("website.403")


    @http.route(['/survey/submit/drum/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit_drum(self, survey, **post):
        drum_obj = request.env['wash.order']
        _logger.debug('Incoming data: %s', post)
        print ("xxxxxxxxxxxxxxxxx",post)
        page_id = int(post['page_id'])
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])

        # Answer validation
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
            except KeyError:  # Invalid token
                return request.render("website.403")
            user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                request.env['survey.user_input_line'].sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)

            go_back = post['button_submit'] == 'previous'
            next_page, _, last = request.env['survey.survey'].next_page(user_input, page_id, go_back=go_back)
            vals = {'last_displayed_page_id': page_id}
            if next_page is None and not go_back:
                vals.update({'state': 'done'})
            else:
                vals.update({'state': 'skip'})
            user_input.sudo(user=user_id).write(vals)
            drum_brw = drum_obj.browse(int(post['drum']))
            user_id = request.env.uid
            search_emp_id = request.env['hr.employee'].search([('user_id','=',user_id )])
            user_brw = request.env['res.users'].browse(user_id)
            if user_input:
                answers = [x.value_suggested.value for x in user_input.user_input_line_ids ]
                line_send_mail_ids = []
                line_continue_ids =[]
                incidents_manager_id = False
                incidents_manager = False
                for x in user_input.user_input_line_ids:
                    
                    if x.page_id.id == page_id:
                        if  x.value_suggested.execution_type == 'send_mail': 
                            line_send_mail_ids.append(x.id)
                            if x.value_suggested.controller_id:
                                incidents_manager_id = x.value_suggested.controller_id.id
                                incidents_manager = x.value_suggested.controller_id.user_id.partner_id.id
                        elif x.value_suggested.execution_type == 'continue':
                            line_continue_ids.append(x.id)
                if line_send_mail_ids:
                    if drum_brw.type_of_order == 'drum': 
                        partner_ids=[]
                        if incidents_manager:
                            partner_ids = [incidents_manager]
                        if search_emp_id.incidents_manager_id:
                            partner_ids =[ search_emp_id.incidents_manager_id.user_id.partner_id.id ]
                        mail_val = {
	                          'subject':'Incident Created',
	                          'body': ('Incident Created BY %s .')%(user_brw.name,),
	                          'author_id':user_brw.partner_id.id,
	                           'email_from': user_brw.login ,
	                           'message_type':'email',
	                           'model':'wash.order',
	                           'partner_ids':[(6,0, partner_ids )] , 
	                           'res_id': user_input.wash_order_id.id
	                            }
                        a = request.env['mail.message'].create(mail_val)
                        drum_brw.state = 'end_wash'
                elif line_continue_ids : 
                    if drum_brw.type_of_order == 'drum':   
                        drum_brw.state = 'quality_control'   
            ret['redirect'] = '/survey/fill/drum/%s/%s/%s' % (survey.id, post['token'], post['drum'])
            if go_back:
                ret['redirect'] += '/prev'
        return json.dumps(ret)


    #############repair survey
    # Survey start
    @http.route(['/survey/start/repair/<model("survey.survey"):survey>/<string:repair>' ],
                type='http', auth='public', website=True)
    def start_survey_repair(self, survey, repair=None , **post):
        context = dict(request.context)
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey, token=None)
        if errpage:
            return errpage

        # Manual surveying
        vals = {'survey_id': survey.id, 'repair_id':int(repair)}
        if request.website.user_id != request.env.user:
            vals['partner_id'] = request.env.user.partner_id.id
        user_input = UserInput.create(vals)

        # Do not open expired survey
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = {'survey': survey, 'page': None, 'token': user_input.token, 'repair':repair}
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s/%s' % (survey.id, user_input.token, wash))

    @http.route(['/survey/fill/repair/<model("survey.survey"):survey>/<string:token>/<string:repair>',
                 '/survey/fill/repair/<model("survey.survey"):survey>/<string:token>/<string:prev>'],
                type='http', auth='public', website=True)
    def fill_survey_repair(self, survey, token, prev=None, repair=None, **post):
        '''Display and validates a survey'''
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey)
        if errpage:
            return errpage

        # Load the user_input
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        if not user_input:  # Invalid token
            return request.render("website.403")

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # First page
            page, page_nr, last = Survey.next_page(user_input, 0, go_back=False)
            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'repair':repair}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        elif user_input.state == 'done':  # Display success message
            return request.render('survey.sfinished', {'survey': survey,
                                                       'token': token,
                                                       'user_input': user_input,
                                                       'repair':repair})
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=flag)

            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page:
                page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=True)

            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'repair':repair}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        else:
            return request.render("website.403")


    @http.route(['/survey/submit/repair/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit_repair(self, survey, **post):
        repair_obj = request.env['mrp.repair']
        wash_obj = request.env['mrp.repair']
        _logger.debug('Incoming data: %s', post)
        page_id = int(post['page_id'])
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])

        # Answer validation
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
            except KeyError:  # Invalid token
                return request.render("website.403")
            user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                request.env['survey.user_input_line'].sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)

            go_back = post['button_submit'] == 'previous'
            next_page, _, last = request.env['survey.survey'].next_page(user_input, page_id, go_back=go_back)
            vals = {'last_displayed_page_id': page_id}
            if next_page is None and not go_back:
                vals.update({'state': 'done'})
            else:
                vals.update({'state': 'skip'})
            user_input.sudo(user=user_id).write(vals)
            repair_brw = repair_obj.browse(int(post['repair']))
            if user_input:
                answers = [x.value_suggested.value for x in user_input.user_input_line_ids ]
                line_send_mail_ids = []
                line_continue_ids =[]
                for x in user_input.user_input_line_ids:
                    incidents_manager_id = False
                    incidents_manager = False
                    if x.page_id.id == page_id:
                        if  x.value_suggested.execution_type == 'send_mail': 
                            line_send_mail_ids.append(x.id)
                            if x.value_suggested.controller_id:
                                incidents_manager_id = x.value_suggested.controller_id.id
                                incidents_manager = x.value_suggested.controller_id.user_id.partner_id.id
                        elif x.value_suggested.execution_type == 'continue':
                            line_continue_ids.append(x.id)
                if line_send_mail_ids:
                    user_id = request.env.uid
                    search_emp_id = request.env['hr.employee'].search([('user_id','=',user_id )])
                    user_brw = request.env['res.users'].browse(user_id)
                    partner_ids=[]
                    if incidents_manager:
                        partner_ids = [incidents_manager]
                    if search_emp_id.incidents_manager_id:
                        partner_ids =[ search_emp_id.incidents_manager_id.user_id.partner_id.id ]
                    mail_val = {
                              'subject':'Incident Created',
                              'body': ('Incident Created BY %s .')%(user_brw.name,),
                              'author_id':user_brw.partner_id.id,
                               'email_from': user_brw.login ,
                               'message_type':'email',
                               'model':'mrp.repair',
                               'partner_ids':[(6,0, partner_ids)], 
                               'res_id': user_input.repair_id.id
                                }
                    request.env['mail.message'].create(mail_val)
                    repair_brw.wash_id.repair_compliance = 'no'
                    repair_brw.wash_id.state = 'repair_create'
                elif line_continue_ids : 
                    repair_brw.state = 'check_compliance'   
                    repair_brw.wash_id.repair_compliance = 'yes'          
            ret['redirect'] = '/survey/fill/repair/%s/%s/%s' % (survey.id, post['token'],  post['repair'])
            if go_back:
                ret['redirect'] += '/prev'
        return json.dumps(ret)

     # Survey start
    @http.route(['/survey/start/crush/<model("survey.survey"):survey>/<string:crush>' ],
                type='http', auth='public', website=True)
    def start_survey_crush(self, survey, crush=None , **post):
        context = dict(request.context)
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey, token=None)
        if errpage:
            return errpage

        # Manual surveying
        vals = {'survey_id': survey.id, 'wash_order_id':int(crush)}
        if request.website.user_id != request.env.user:
            vals['partner_id'] = request.env.user.partner_id.id
        user_input = UserInput.create(vals)

        # Do not open expired survey
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = {'survey': survey, 'page': None, 'token': user_input.token, 'crush':crush}
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s/%s' % (survey.id, user_input.token, crush))

    @http.route(['/survey/fill/crush/<model("survey.survey"):survey>/<string:token>/<string:crush>',
                 '/survey/fill/crush/<model("survey.survey"):survey>/<string:token>/<string:prev>'],
                type='http', auth='public', website=True)
    def fill_survey_crush(self, survey, token, prev=None, crush=None, **post):
        '''Display and validates a survey'''
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey)
        if errpage:
            return errpage

        # Load the user_input
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        if not user_input:  # Invalid token
            return request.render("website.403")

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # First page
            page, page_nr, last = Survey.next_page(user_input, 0, go_back=False)
            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'crush':crush}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        elif user_input.state == 'done':  # Display success message
            return request.render('survey.sfinished', {'survey': survey,
                                                       'token': token,
                                                       'user_input': user_input,
                                                       'crush':crush})
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=flag)

            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page:
                page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=True)

            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'crush':crush}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        else:
            return request.render("website.403")


    @http.route(['/survey/submit/crush/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit_crush(self, survey, **post):
        wash_obj = request.env['wash.order']
        _logger.debug('Incoming data: %s', post)
        page_id = int(post['page_id'])
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])

        # Answer validation
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
            except KeyError:  # Invalid token
                return request.render("website.403")
            user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                request.env['survey.user_input_line'].sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)

            go_back = post['button_submit'] == 'previous'
            next_page, _, last = request.env['survey.survey'].next_page(user_input, page_id, go_back=go_back)
            vals = {'last_displayed_page_id': page_id}
            if next_page is None and not go_back:
                vals.update({'state': 'done'})
            else:
                vals.update({'state': 'skip'})
            user_input.sudo(user=user_id).write(vals)
            if user_input:
                answers = [x.value_suggested.value for x in user_input.user_input_line_ids ]
                line_send_mail_ids = []
                line_continue_ids =[]
                for x in user_input.user_input_line_ids:
                    incidents_manager_id = False
                    incidents_manager = False
                    if x.page_id.id == page_id:
                        if  x.value_suggested.execution_type == 'send_mail': 
                            line_send_mail_ids.append(x.id)
                            if x.value_suggested.controller_id:
                                incidents_manager_id = x.value_suggested.controller_id.id
                                incidents_manager = x.value_suggested.controller_id.user_id.partner_id.id
                        elif x.value_suggested.execution_type == 'continue':
                            line_continue_ids.append(x.id)
                if line_send_mail_ids:
                    user_id = request.env.uid
                    search_emp_id = request.env['hr.employee'].search([('user_id','=',user_id )])
                    user_brw = request.env['res.users'].browse(user_id)
                    
                    request.env['survey.user_input_line'].create(val)
                    mail_val = {
	                          'subject':'Incident Created',
	                          'body': ('Incident Created BY %s .')%(user_brw.name,),
	                          'author_id':user_brw.partner_id.id,
	                           'email_from': user_brw.login ,
	                           'message_type':'email',
	                           'model':'wash.order',
	                           'partner_ids':[(6,0, [incidents_manager or search_emp_id.incidents_manager_id.user_id.partner_id.id ] )] or False, 
	                           'res_id': user_input.wash_order_id.id
	                            }
                    request.env['mail.message'].create(mail_val)
                else : 
                    wash_brw = wash_obj.browse(int(post['crush']))
                    wash_brw.state = 'check_compliance'
            '''if user_input:
                answers = [x.value_suggested.value for x in user_input.user_input_line_ids ]
                for x in user_input.user_input_line_ids:
                    incidents_manager_id = False
                    incidents_manager = False
                    if x.page_id.id == page_id:
                        if  x.value_suggested.execution_type == 'send_mail': 
                            user_id = request.env.uid
                            search_emp_id = request.env['hr.employee'].search([('user_id','=',user_id )])
                            user_brw = request.env['res.users'].browse(user_id)
                            if x.value_suggested.controller_id:
                                incidents_manager_id = x.value_suggested.controller_id.id
                                incidents_manager = x.value_suggested.controller_id.user_id.partner_id.id
                            val = {'execution_type':'send_mail',
                                        'employee_id':search_emp_id[0] or False,
					'incidents_manager_id': incidents_manager_id or search_emp_id.incidents_manager_id.id,
                                           'state':'mail_send'}
                            x.write(val)
                            mail_val = {
		                          'subject':'Incident Created',
		                          'body': ('Incident Created BY %s .')%(user_brw.name,),
		                          'author_id':user_brw.partner_id.id,
		                           'email_from': user_brw.login ,
		                           'message_type':'email',
		                           'model':'wash.order',
		                           'partner_ids':[(6,0, [incidents_manager or search_emp_id.incidents_manager_id.user_id.partner_id.id ] )] or False, 
		                           'res_id': user_input.wash_order_id.id
		                            }
                            request.env['mail.message'].create(mail_val)
                        else :
                            wash_brw = wash_obj.browse(int(post['crush']))
                            wash_brw.state = 'check_compliance' '''
            ret['redirect'] = '/survey/fill/crush/%s/%s/%s' % (survey.id, post['token'], post['crush'])
            if go_back:
                ret['redirect'] += '/prev'
        return json.dumps(ret)
    


    @http.route(['/survey/start/compact/<model("survey.survey"):survey>/<string:compact>' ],
                type='http', auth='public', website=True)
    def start_survey_compact(self, survey, compact=None , **post):
        context = dict(request.context)
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey, token=None)
        if errpage:
            return errpage

        # Manual surveying
        vals = {'survey_id': survey.id, 'wash_order_id':int(compact)}
        if request.website.user_id != request.env.user:
            vals['partner_id'] = request.env.user.partner_id.id
        user_input = UserInput.create(vals)

        # Do not open expired survey
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = {'survey': survey, 'page': None, 'token': user_input.token, 'compact':compact}
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s/%s' % (survey.id, user_input.token, compact))

    @http.route(['/survey/fill/compact/<model("survey.survey"):survey>/<string:token>/<string:compact>',
                 '/survey/fill/compact/<model("survey.survey"):survey>/<string:token>/<string:prev>'],
                type='http', auth='public', website=True)
    def fill_survey_compact(self, survey, token, prev=None, compact=None, **post):
        '''Display and validates a survey'''
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey)
        if errpage:
            return errpage

        # Load the user_input
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        if not user_input:  # Invalid token
            return request.render("website.403")

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # First page
            page, page_nr, last = Survey.next_page(user_input, 0, go_back=False)
            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'compact':compact}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        elif user_input.state == 'done':  # Display success message
            return request.render('survey.sfinished', {'survey': survey,
                                                       'token': token,
                                                       'user_input': user_input,
                                                       'compact':compact})
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=flag)

            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page:
                page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=True)

            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'compact':compact}
            if last:
                data.update({'last': True})
            return request.render('survey.survey', data)
        else:
            return request.render("website.403")


    @http.route(['/survey/submit/compact/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def submit_compact(self, survey, **post):
        wash_obj = request.env['wash.order']
        _logger.debug('Incoming data: %s', post)
        page_id = int(post['page_id'])
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])

        # Answer validation
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
            except KeyError:  # Invalid token
                return request.render("website.403")
            user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                request.env['survey.user_input_line'].sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)

            go_back = post['button_submit'] == 'previous'
            next_page, _, last = request.env['survey.survey'].next_page(user_input, page_id, go_back=go_back)
            vals = {'last_displayed_page_id': page_id}
            if next_page is None and not go_back:
                vals.update({'state': 'done'})
            else:
                vals.update({'state': 'skip'})
            user_input.sudo(user=user_id).write(vals)
            if user_input:
                answers = [x.value_suggested.value for x in user_input.user_input_line_ids ]
                line_send_mail_ids = []
                line_continue_ids =[]
                for x in user_input.user_input_line_ids:
                    incidents_manager_id = False
                    incidents_manager = False
                    if x.page_id.id == page_id:
                        if  x.value_suggested.execution_type == 'send_mail': 
                            line_send_mail_ids.append(x.id)
                            if x.value_suggested.controller_id:
                                incidents_manager_id = x.value_suggested.controller_id.id
                                incidents_manager = x.value_suggested.controller_id.user_id.partner_id.id
                        elif x.value_suggested.execution_type == 'continue':
                            line_continue_ids.append(x.id)
                if line_send_mail_ids:
                    user_id = request.env.uid
                    search_emp_id = request.env['hr.employee'].search([('user_id','=',user_id )])
                    user_brw = request.env['res.users'].browse(user_id)
                    
                    mail_val = {
	                          'subject':'Incident Created',
	                          'body': ('Incident Created BY %s .')%(user_brw.name,),
	                          'author_id':user_brw.partner_id.id,
	                           'email_from': user_brw.login ,
	                           'message_type':'email',
	                           'model':'wash.order',
	                           'partner_ids':[(6,0, [incidents_manager or search_emp_id.incidents_manager_id.user_id.partner_id.id ] )] or False, 
	                           'res_id': user_input.wash_order_id.id
	                            }
                    request.env['mail.message'].create(mail_val)
                else : 
                    wash_brw = wash_obj.browse(int(post['compact']))
                    wash_brw.state = 'check_compliance'
		
            ret['redirect'] = '/survey/fill/compact/%s/%s/%s' % (survey.id, post['token'], post['compact'])
            if go_back:
                ret['redirect'] += '/prev'
        return json.dumps(ret)
    
