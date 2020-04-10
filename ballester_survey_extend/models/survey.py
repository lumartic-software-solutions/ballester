# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Survey Extend.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).# 
from odoo import models, fields, api, _
from werkzeug import urls
from odoo.addons.http_routing.models.ir_http import slug


# new fields 
class SurveySurvey(models.Model):
    _inherit = 'survey.survey'
     
    instruction_info = fields.Html(string='Instruction Information')
    public_url = fields.Char("Public link", compute="_compute_survey_url")
    public_url_html = fields.Char("Public link (html version)", compute="_compute_survey_url")
    print_url = fields.Char("Print link", compute="_compute_survey_url")
    result_url = fields.Char("Results link", compute="_compute_survey_url")
    is_compliance_survey = fields.Boolean("Is Compliance Survey?")
    
    @api.model
    def next_page(self, user_input, page_id, go_back=False):
        """ The next page to display to the user, knowing that page_id is the id
            of the last displayed page.

            If page_id == 0, it will always return the first page of the survey.

            If all the pages have been displayed and go_back == False, it will
            return None

            If go_back == True, it will return the *previous* page instead of the
            next page.

            .. note::
                It is assumed here that a careful user will not try to set go_back
                to True if she knows that the page to display is the first one!
                (doing this will probably cause a giant worm to eat her house)
        """
        survey = user_input.survey_id
        context = self._context
        pages = list(enumerate(survey.page_ids))
        
        # First page
        if page_id == 0:
            return (pages[0][1], 0, len(pages) == 1)
        line_send_mail_ids =[]
        page_continue_ids=[]
        controller_id = False
        if user_input:
            for x in user_input.user_input_line_ids:
                print ("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPP", x)
                if x.page_id.id == page_id:
                    if x.value_suggested.execution_type:
                        if x.value_suggested.execution_type == 'continue':
                            if x.value_suggested.page_question_id:
                                page_continue_ids.append(x.value_suggested.page_question_id.id)
                                print ("zzzzzzzzzzzzzzzzzzzzz", page_continue_ids)
                        elif x.value_suggested.execution_type == 'send_mail': 
                            line_send_mail_ids.append(x.id) 
                            if x.value_suggested.controller_id:
                                user_id = self.env.uid
                                search_emp_id = self.env['hr.employee'].search([('user_id','=',user_id )])
                                print ("************search_emp_id******0", search_emp_id , x.value_suggested.controller_id.id)
                                val = {'execution_type':'send_mail',
                                        'employee_id':search_emp_id[0] or False,
					'incidents_manager_id': x.value_suggested.controller_id.id,
                                           'state':'mail_send'}
                                x.write(val)
                                controller_id = x.value_suggested.controller_id.user_id.id
                                print ("******controller_id*********",controller_id )
                                template = self.env.ref(
				             'ballester_survey_extend.incidents_purchase_mail_template')
                                print ("*((((((((((((((((((((0", template)
                                if template :
                                    template.send_mail(x.id, force_send=True)
                                user_brw = self.env['res.users'].browse(user_id)
                                mail_val = {
                                  'subject':  _('Incident Created'),
                                  'body':_('Incident Created BY %s .')%(search_emp_id.name,),
                                  'author_id':user_brw.partner_id.id,
                                   'email_from': user_brw.login ,
                                   'message_type':'email',
                                   'model':'purchase.order',
                                    'partner_ids':[(6,0, [x.value_suggested.controller_id.user_id.partner_id.id])] or False,
                                   'res_id': user_input.purchase_order_id.id
                                    }
                                print ("&**************mail_val************",mail_val )
                                self.env['mail.message'].create(mail_val) 
        current_page_index = pages.index(next(p for p in pages if p[1].id == page_id))
        if line_send_mail_ids:
            if controller_id:
                controller_id = controller_id
            else:
                controller_id = user_input.purchase_order_id.user_id.id
            print ("*************controller_id*********",controller_id )
            user_input.purchase_order_id.write({'user_id':controller_id })
            return (None, -1, False)
        elif page_continue_ids:
            Pages = self.env['survey.page'].browse(page_continue_ids[-1])
            next_page_index = pages.index(next(p for p in pages if p[1].id == page_continue_ids[-1]))
            return (Pages, next_page_index , False)
        else:
            if not line_send_mail_ids:
                if user_input.purchase_order_id:
                    user_input.purchase_order_id.write({'state': 'check_compliance' })
            return (None, -1, False)
    
    '''@api.model
    def next_page(self, user_input, page_id, go_back=False):
        """ The next page to display to the user, knowing that page_id is the id
            of the last displayed page.

            If page_id == 0, it will always return the first page of the survey.

            If all the pages have been displayed and go_back == False, it will
            return None

            If go_back == True, it will return the *previous* page instead of the
            next page.

            .. note::
                It is assumed here that a careful user will not try to set go_back
                to True if she knows that the page to display is the first one!
                (doing this will probably cause a giant worm to eat her house)
        """
        survey = user_input.survey_id
        context = self._context
        print ("UIIIIIIIIIIIIIIIIIIII",context)
        print (">>>>>>>>>>>>survey>>>>>>>>>>",survey , page_id , go_back)
        pages = list(enumerate(survey.page_ids))
        print (">>>>>pages>>>>>>>survey>>>>>>>>>>",pages)
        
        # First page
        if page_id == 0:
            return (pages[0][1], 0, len(pages) == 1)
        (if page_id:
            print ("2222222222222222222222222")
            page_brw= self.env['survey.page'].browse(page_id)
            if page_brw.question_ids:
                for question in page_brw.question_ids:
                    if question.labels_ids:
                        for label in question.labels_ids:
                            print ("UUUUUUUUUUUUUUUlabelUUUUUUUUUU",label)
                            if label.execution_type == "continue":
                                print (">>>>>>>>>>>continue>>>>>>>>>>>>>>>>>>>>jhbjhvf")
                            elif label.execution_type =="send_mail":
                                print ("&&&&&&&&&&&&&&&send_mail&&&&&&&&&&&&&&&"))
        current_page_index = pages.index(next(p for p in pages if p[1].id == page_id))
        print ("&&&&&&&&&&&&&&&&&&&&&&&&",current_page_index,len(pages) - 1  ,go_back)
        # All the pages have been displayed
        if current_page_index == len(pages) - 1 and not go_back:
            print ("HHHHHHHHHHHHHHHHHHHHHHHHHHH")
            return (None, -1, False)
        # Let's get back, baby!
        elif go_back and survey.users_can_go_back:
            return (pages[current_page_index - 1][1], current_page_index - 1, False)
        else:
            print ("^^^^^^^^^^^^^^^^^^^^^^")
            # This will show the last page
            if current_page_index == len(pages) - 2:
                return (pages[current_page_index + 1][1], current_page_index + 1, True)
            # This will show a regular page
            else:
                return (pages[current_page_index ][1], current_page_index + 1, False)'''
    
      
    
    def _compute_survey_url(self):
        """ Computes a public URL for the survey """
        base_url = '/' if self.env.context.get('relative_url') else \
                   self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for survey in self:
            if self.env.context.get('purchase'):
                survey.public_url = urls.url_join(base_url, "survey/start/po/%s" % (slug(survey)))
                survey.print_url = urls.url_join(base_url, "survey/print/%s" % (slug(survey)))
                survey.result_url = urls.url_join(base_url, "survey/results/%s" % (slug(survey)))
                survey.public_url_html = '<a href="%s">%s</a>' % (survey.public_url, _("Click here to start survey"))
            elif self.env.context.get('sale'):
                survey.public_url = urls.url_join(base_url, "survey/start/so/%s" % (slug(survey)))
                survey.print_url = urls.url_join(base_url, "survey/print/%s" % (slug(survey)))
                survey.result_url = urls.url_join(base_url, "survey/results/%s" % (slug(survey)))
                survey.public_url_html = '<a href="%s">%s</a>' % (survey.public_url, _("Click here to start survey"))
            elif self.env.context.get('wash'):
                survey.public_url = urls.url_join(base_url, "survey/start/wash/%s" % (slug(survey)))
                survey.print_url = urls.url_join(base_url, "survey/print/%s" % (slug(survey)))
                survey.result_url = urls.url_join(base_url, "survey/results/%s" % (slug(survey)))
                survey.public_url_html = '<a href="%s">%s</a>' % (survey.public_url, _("Click here to start survey"))
            elif self.env.context.get('drum'):
                survey.public_url = urls.url_join(base_url, "survey/start/drum/%s" % (slug(survey)))
                survey.print_url = urls.url_join(base_url, "survey/print/%s" % (slug(survey)))
                survey.result_url = urls.url_join(base_url, "survey/results/%s" % (slug(survey)))
                survey.public_url_html = '<a href="%s">%s</a>' % (survey.public_url, _("Click here to start survey"))
            elif self.env.context.get('repair'):
                survey.public_url = urls.url_join(base_url, "survey/start/repair/%s" % (slug(survey)))
                survey.print_url = urls.url_join(base_url, "survey/print/%s" % (slug(survey)))
                survey.result_url = urls.url_join(base_url, "survey/results/%s" % (slug(survey)))
                survey.public_url_html = '<a href="%s">%s</a>' % (survey.public_url, _("Click here to start survey"))
            elif self.env.context.get('crush'):
                survey.public_url = urls.url_join(base_url, "survey/start/crush/%s" % (slug(survey)))
                survey.print_url = urls.url_join(base_url, "survey/print/%s" % (slug(survey)))
                survey.result_url = urls.url_join(base_url, "survey/results/%s" % (slug(survey)))
                survey.public_url_html = '<a href="%s">%s</a>' % (survey.public_url, _("Click here to start survey"))   
            elif self.env.context.get('compact'):
                survey.public_url = urls.url_join(base_url, "survey/start/compact/%s" % (slug(survey)))
                survey.print_url = urls.url_join(base_url, "survey/print/%s" % (slug(survey)))
                survey.result_url = urls.url_join(base_url, "survey/results/%s" % (slug(survey)))
                survey.public_url_html = '<a href="%s">%s</a>' % (survey.public_url, _("Click here to start survey"))

            else:
                survey.public_url = urls.url_join(base_url, "survey/start/%s" % (slug(survey)))
                survey.print_url = urls.url_join(base_url, "survey/print/%s" % (slug(survey)))
                survey.result_url = urls.url_join(base_url, "survey/results/%s" % (slug(survey)))
                survey.public_url_html = '<a href="%s">%s</a>' % (survey.public_url, _("Click here to start survey"))


