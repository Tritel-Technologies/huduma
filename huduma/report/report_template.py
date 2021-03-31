# -*- coding: utf-8 -*-
try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass

class HudumaCaseXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, cases):
        sheet = workbook.add_worksheet()
        header = workbook.add_format({'font_size': 16, 'align': 'center', 'bg_color': '#D3D3D3', 'bold': True})
        subheader = workbook.add_format({'font_size': 10, 'bg_color': '#D3D3D3', 'bold': True})
        bold = workbook.add_format({'font_size': 10, 'bold': True})
        normal = workbook.add_format({'font_size': 10}) 

        sheet.merge_range('B1:E1', 'Karibu Center Cases: %s - %s' %(data['form']['start_date'] or "", data['form']['end_date'] or ""), header)
        sheet.merge_range('A2:B2', 'Departments:', bold)

        department_ids = data['form']['department_ids']
        departments = self.env['huduma.department'].search([('id','in',department_ids)]).mapped('name')
        departments = ",".join(departments)
        
        sheet.merge_range('C2:D2', departments, normal)
        sheet.merge_range('A3:B3', '', bold)
        sheet.merge_range('C3:D3', '', normal)
        sheet.merge_range('A4:B4', '', bold)
        sheet.merge_range('C4:D4', '', normal) 

        # Adjust height: top row
        sheet.set_row(0, 20) 

        # Adjust column sizes
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 3, 5)
        sheet.set_column(4, 4, 10)
        sheet.set_column(6, 6, 12)

        # Table Headers
        row = 4
        sheet.write(row, 0, "No.", bold)
        sheet.write(row, 1, "Title", bold)
        sheet.write(row, 2, "Nature", bold)
        sheet.write(row, 3, "Tags", bold)
        sheet.write(row, 4, "Customer", bold)
        sheet.write(row, 5, "Opened By", bold)
        sheet.write(row, 6, "Department", bold)
        sheet.write(row, 7, "Assigned To", bold)
        sheet.write(row, 8, "Case Information", bold)
        sheet.write(row, 9, "Case Information", bold)
        sheet.write(row, 10, "Resolution Status", bold)
        sheet.write(row, 11, "Priority", bold)
        sheet.write(row, 12, "Status", bold)
        sheet.write(row, 13, "Opened Date", bold)
        sheet.write(row, 14, "Due Date", bold)
        sheet.write(row, 15, "Resolved Date", bold)
        sheet.write(row, 16, "Days Lapsed", bold)

        # Table data
        index = 1
        row += 1

        for case in cases:
            sheet.write(row, 0, case.name or "", normal)
            sheet.write(row, 1, case.title or "", normal)
            sheet.write(row, 2, case.case_type.name or "", normal)
            sheet.write(row, 3, ",".join(case.mapped('tag_ids.name')), normal)
            sheet.write(row, 4, case.customer.name or "", normal)
            sheet.write(row, 5, case.opened_by.name or "", normal)
            sheet.write(row, 6, case.department_id.name or "", normal)
            sheet.write(row, 7, "%s(%s)" %(case.assigned_to.name or "",case.assigned_to_email or ""), normal)
            sheet.write(row, 8, case.case_information or "", normal)
            sheet.write(row, 9, case.case_resolution or "", normal)
            sheet.write(row, 10, case.resolution_status or "", normal)
            sheet.write(row, 11, case.priority or "", normal)
            sheet.write(row, 12, case.stage_id.name or "", normal)
            sheet.write(row, 13, case.opened_date or "", normal)
            sheet.write(row, 14, case.due_date or "", normal)
            sheet.write(row, 15, case.resolved_date or "", normal)
            sheet.write(row, 16, case.days_lapsed, normal)

            row += 1

HudumaCaseXlsx('report.monthly_report.xlsx', 'huduma.case.header')