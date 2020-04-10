# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Hr Attendance.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).# 
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta ,date


    
# new fields 
class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
     
    
    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                    'empl_name': attendance.employee_id.name,
                    'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
                })
            
            att_check_in = datetime.strptime(attendance.check_in, '%Y-%m-%d %H:%M:%S')
            
            emp_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('id', '!=', attendance.id)
                ])
            if emp_attendances:
                today = date.today()
                pre_emp_attendances_check_in = datetime.strptime(emp_attendances[0].check_in, '%Y-%m-%d %H:%M:%S')
                att_pre_check_in_after_5 = pre_emp_attendances_check_in + timedelta(minutes = 5)
                if attendance.check_out:
                    att_check_out = datetime.strptime(attendance.check_out, '%Y-%m-%d %H:%M:%S')
                    pre_emp_attendances_check_out = datetime.strptime(emp_attendances[0].check_out, '%Y-%m-%d %H:%M:%S')
                    att_pre_check_out_after_5 = pre_emp_attendances_check_out + timedelta(minutes = 5)
                    if att_check_out.date() == today:
                        if att_check_out < att_pre_check_out_after_5:
                            raise exceptions.ValidationError(_("esperar 5 minutos" ))
                
                if att_check_in.date() == today:
                    if att_check_in < att_pre_check_in_after_5:
                        raise exceptions.ValidationError(_("Ya has iniciado sesión. Probar después de 5 minutos" ))
                
                
            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ])
                if no_check_out_attendances:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
                    })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(last_attendance_before_check_out.check_in))),
                    })
    
    
    @api.multi    
    def set_question(self,question_type,survey):
        information_details = []
        for page in survey.page_ids:
            if page.question_ids :
                for rec in page.question_ids:
                    if rec.question_type == question_type and rec.type =='simple_choice':
                        answers = []
                        for label in rec.labels_ids:
                            answers.append({'answer':label.value ,'answer_id' : label.id,'execution_type':label.execution_type or ''})
                        information_details.append({
                            'question':rec.question  or '',
                            'question_id':rec.id  or '',
                            'answer_list' :answers,
                            'type' :'simple_choice',
                            })
        return information_details
    
    # set Attendance Notification Questions 
    @api.multi
    def set_information(self,attendance,stage):
        if stage == 'none' :
            return {'warning': 'No Found Attendance Status'}
        else:
            attendance_id = self.env['hr.attendance'].browse(int(attendance))
            if attendance_id :
                job  = attendance_id.employee_id.job_id
                if job :
                    survey = job.survey_id 
                    if survey :
                        if stage == 'checkin' :
                            question_type='entry'
                            information_details = self.set_question(question_type,survey)
                            return {'success': 'Successfully Get Entry Notification!','information_details' :information_details,
                                    'description' : survey.instruction_info if survey.instruction_info else ''}
                        elif stage == 'checkout' :
                            question_type='exit'
                            information_details = self.set_question(question_type,survey)
                            return {'success': 'Successfully Get Exit Notification!','information_details' :information_details,
                                    'description' : survey.instruction_info if survey.instruction_info else '' }
                    else:
                        return {'warning': (_('No Found Interview Form For %s Job Position') %job.name) }
                else:
                    return {'warning': (_('No Found Job Position For %s Employee') %attendance_id.employee_id.name) }
                
    # set Attendance status 
    @api.multi
    def send_notifications_mail(self,user_input_line_id,attendance):
        if len(user_input_line_id) > 0 :
            attendance_id = self.env['hr.attendance'].browse(int(attendance))
            if attendance_id:
                attendance_id.unlink()
            user_input_line_ids = self.env['survey.user_input_line'].search([('id','in',user_input_line_id)])
            template = self.env.ref(
                'ballester_survey_extend.incidents_mail_template')
            if template and user_input_line_ids:
                for line in user_input_line_ids :
                    template.send_mail(line.id, force_send=True)
                return {'success': 'Successfully Sent mail to Incidents Reporting Manager !'}
        else:
            return {'warning': 'Please try again!'}
        
    
    @api.multi
    def delete_answer(self,user_input_line_id):
        user_input_line_ids = self.env['survey.user_input_line'].search([('id','in',user_input_line_id)])
        if user_input_line_id:
            for line in user_input_line_ids :
                line.unlink()
            return {'success': 'Successfully Deleted The Answer !'}
        else:
            return {'warning': 'Please try again!'}
            
    
    @api.multi
    def create_answers(self,answer,question):
        ans_obj =self.env['survey.user_input']
        emp = self.employee_id
        job  = self.employee_id.job_id
        if job :
            survey = job.survey_id
            label_id = self.env['survey.label'].browse(int(answer)) 
            if label_id.execution_type == 'send_mail' :
                value = {'question_id':int(question),
                        'answer_type':'suggestion',
                        'value_suggested':int(answer),
                        'state':'mail_send'}
            else:
                value = {'question_id':int(question),
                        'answer_type':'suggestion',
                        'value_suggested':int(answer)}
            if survey :
                vals= {'survey_id' : survey.id,
                       'type':'manually',
                       'employee_id':emp.id,
                       'email':emp.work_email or '',
                       'state':'done',
                       'user_input_line_ids':[(0,0,value)]}
                ans_id = ans_obj.create(vals)
                return ans_id
            else:
                return {'warning': (_('No Found Incidents Form For %s Job Position') %job.name) }
        else:
            raise UserError(_('No Found Job Position For %s Employee') %self.employee_id.name)
            
    # set Attendance status 
    @api.multi
    def set_attendance_status(self,attendance,stage,answer,question):
        if stage == 'none' :
            return {'warning': 'No Found Attendance Status'}
        elif question =='' or answer=='' :
            return {'warning': 'No Found Question or Answer ! Please Try Again !'}
        else :
            answer_id = self.env['survey.label'].browse(int(answer))
            attendance_id = self.env['hr.attendance'].browse(int(attendance))
            if attendance_id and answer_id:
                if stage == 'checkin' :
                    ans_id = attendance_id.create_answers(answer,question)
                    if ans_id :
                        return {'success': 'Successfully Updated Attendance Status !','execution_type':answer_id.execution_type or 'none','ans_id':ans_id.id,'user_input_line_id':ans_id.user_input_line_ids.ids}
                    else:
                        return {'warning': 'Not Submitted The Answer! Please Try again!'}
                elif stage == 'checkout' :
                    ans_id =attendance_id.create_answers(answer,question)
                    if ans_id :
                        return {'success': 'Successfully Updated Attendance Status !','execution_type':answer_id.execution_type or 'none','ans_id':ans_id.id,'user_input_line_id':ans_id.user_input_line_ids.ids}
                    else:
                        return {'warning': 'Not Submitted The Answer! Please Try again!'}
                else:
                    return {'warning': 'No Found Attendance Status!'}
            else:
                return {'warning': 'No Found Attendance!'}



class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    @api.multi
    def attendance_action_change(self):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        if len(self) > 1:
            raise exceptions.UserError(_('Cannot perform check in or check out on multiple employees.'))
        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
            }
            search_att = self.env['hr.attendance'].search([('employee_id','=',self.id), ('check_in','=', action_date)])
            if not search_att:
                return self.env['hr.attendance'].create(vals)
        else:
            attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
            if attendance:
                attendance.check_out = action_date
            else:
                raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                    'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.name, })
            return attendance
            
