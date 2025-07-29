import io
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents

class ReportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12
        ))
    
    def generate_contract_report_csv(self, contracts: List[Dict]) -> io.BytesIO:
        """Generate CSV report of contracts"""
        output = io.StringIO()
        
        fieldnames = [
            'Contract Number', 'Vendor Name', 'Title', 'Start Date', 'End Date',
            'Contract Value', 'Currency', 'Risk Level', 'Compliance Status',
            'Last Audit Date', 'Next Audit Date', 'Number of Clauses',
            'High Risk Clauses', 'Action Required'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for contract in contracts:
            # Count high risk clauses
            high_risk_clauses = sum(1 for clause in contract.get('clauses', []) 
                                   if clause.get('risk_assessment') == 'high')
            action_required = any(clause.get('action_required', False) 
                                for clause in contract.get('clauses', []))
            
            writer.writerow({
                'Contract Number': contract.get('contract_number'),
                'Vendor Name': contract.get('vendor_name'),
                'Title': contract.get('title'),
                'Start Date': contract.get('start_date'),
                'End Date': contract.get('end_date'),
                'Contract Value': contract.get('contract_value'),
                'Currency': contract.get('currency'),
                'Risk Level': contract.get('risk_level'),
                'Compliance Status': contract.get('compliance_status'),
                'Last Audit Date': contract.get('last_audit_date'),
                'Next Audit Date': contract.get('next_audit_date'),
                'Number of Clauses': len(contract.get('clauses', [])),
                'High Risk Clauses': high_risk_clauses,
                'Action Required': 'Yes' if action_required else 'No'
            })
        
        # Convert to bytes
        output.seek(0)
        bytes_output = io.BytesIO(output.getvalue().encode('utf-8'))
        bytes_output.seek(0)
        
        return bytes_output
    
    def generate_clauses_report_csv(self, clauses: List[Dict]) -> io.BytesIO:
        """Generate CSV report of clauses"""
        output = io.StringIO()
        
        fieldnames = [
            'Contract Number', 'Vendor', 'Clause Type', 'Clause Subtype',
            'Title', 'Summary', 'Risk Assessment', 'Action Required',
            'Action Deadline', 'Compliance Requirement', 'Financial Amount',
            'Currency', 'Penalty Amount', 'Penalty Trigger'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for clause in clauses:
            writer.writerow({
                'Contract Number': clause.get('contract_number'),
                'Vendor': clause.get('vendor_name'),
                'Clause Type': clause.get('clause_type'),
                'Clause Subtype': clause.get('clause_subtype'),
                'Title': clause.get('title'),
                'Summary': clause.get('summary'),
                'Risk Assessment': clause.get('risk_assessment'),
                'Action Required': 'Yes' if clause.get('action_required') else 'No',
                'Action Deadline': clause.get('action_deadline'),
                'Compliance Requirement': clause.get('compliance_requirement'),
                'Financial Amount': clause.get('financial_amount'),
                'Currency': clause.get('financial_currency'),
                'Penalty Amount': clause.get('penalty_amount'),
                'Penalty Trigger': clause.get('penalty_trigger')
            })
        
        # Convert to bytes
        output.seek(0)
        bytes_output = io.BytesIO(output.getvalue().encode('utf-8'))
        bytes_output.seek(0)
        
        return bytes_output
    
    def generate_contract_report_pdf(self, contract: Dict) -> io.BytesIO:
        """Generate detailed PDF report for a single contract"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph(f"Contract Compliance Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Contract Information
        story.append(Paragraph("Contract Information", self.styles['SectionTitle']))
        
        contract_data = [
            ['Contract Number:', contract.get('contract_number', 'N/A')],
            ['Vendor Name:', contract.get('vendor_name', 'N/A')],
            ['Title:', contract.get('title', 'N/A')],
            ['Start Date:', contract.get('start_date', 'N/A')],
            ['End Date:', contract.get('end_date', 'N/A')],
            ['Contract Value:', f"{contract.get('currency', 'USD')} {contract.get('contract_value', 'N/A')}"],
            ['Risk Level:', contract.get('risk_level', 'N/A').upper()],
            ['Compliance Status:', contract.get('compliance_status', 'N/A').replace('_', ' ').title()],
        ]
        
        contract_table = Table(contract_data, colWidths=[2*inch, 4*inch])
        contract_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(contract_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Assessment
        if 'risk_assessment' in contract:
            story.append(Paragraph("Risk Assessment", self.styles['SectionTitle']))
            
            risk_data = [
                ['Overall Risk:', contract['risk_assessment'].get('overall_risk', 'N/A').upper()],
                ['High Risk Clauses:', str(contract['risk_assessment'].get('high_risk_clauses', 0))],
                ['Medium Risk Clauses:', str(contract['risk_assessment'].get('medium_risk_clauses', 0))],
            ]
            
            risk_table = Table(risk_data, colWidths=[2*inch, 4*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            story.append(risk_table)
            
            # Risk Factors
            if contract['risk_assessment'].get('risk_factors'):
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph("Risk Factors:", self.styles['Heading3']))
                for factor in contract['risk_assessment']['risk_factors']:
                    story.append(Paragraph(f"• {factor}", self.styles['Normal']))
            
            # Recommendations
            if contract['risk_assessment'].get('recommendations'):
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph("Recommendations:", self.styles['Heading3']))
                for rec in contract['risk_assessment']['recommendations']:
                    story.append(Paragraph(f"• {rec}", self.styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
        
        # Clauses Summary
        if 'clauses' in contract and contract['clauses']:
            story.append(PageBreak())
            story.append(Paragraph("Detected Clauses", self.styles['SectionTitle']))
            
            # Group clauses by type
            clauses_by_type = {}
            for clause in contract['clauses']:
                clause_type = clause.get('clause_type', 'other')
                if clause_type not in clauses_by_type:
                    clauses_by_type[clause_type] = []
                clauses_by_type[clause_type].append(clause)
            
            for clause_type, clauses in clauses_by_type.items():
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph(f"{clause_type.title()} Clauses", self.styles['Heading2']))
                
                for i, clause in enumerate(clauses, 1):
                    story.append(Spacer(1, 0.1*inch))
                    
                    # Clause title with risk indicator
                    risk_color = {
                        'high': colors.red,
                        'medium': colors.orange,
                        'low': colors.green
                    }.get(clause.get('risk_assessment', 'medium'), colors.black)
                    
                    clause_title = Paragraph(
                        f"<font color='{risk_color}'>{i}. {clause.get('title', 'Untitled Clause')}</font>",
                        self.styles['Heading3']
                    )
                    story.append(clause_title)
                    
                    # Clause details
                    if clause.get('summary'):
                        story.append(Paragraph(f"<b>Summary:</b> {clause['summary']}", self.styles['Normal']))
                    
                    if clause.get('compliance_requirement'):
                        story.append(Paragraph(f"<b>Compliance Requirement:</b> {clause['compliance_requirement']}", 
                                             self.styles['Normal']))
                    
                    if clause.get('action_required'):
                        story.append(Paragraph(f"<b>Action Required:</b> Yes", self.styles['Normal']))
                        if clause.get('action_deadline'):
                            story.append(Paragraph(f"<b>Deadline:</b> {clause['action_deadline']}", 
                                                 self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def generate_compliance_summary_pdf(self, contracts: List[Dict]) -> io.BytesIO:
        """Generate compliance summary report for multiple contracts"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("Compliance Summary Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                             self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary Statistics
        story.append(Paragraph("Summary Statistics", self.styles['SectionTitle']))
        
        total_contracts = len(contracts)
        compliant = sum(1 for c in contracts if c.get('compliance_status') == 'compliant')
        non_compliant = sum(1 for c in contracts if c.get('compliance_status') == 'non_compliant')
        pending = sum(1 for c in contracts if c.get('compliance_status') == 'pending')
        high_risk = sum(1 for c in contracts if c.get('risk_level') == 'high')
        
        stats_data = [
            ['Total Contracts:', str(total_contracts)],
            ['Compliant:', f"{compliant} ({compliant/total_contracts*100:.1f}%)"],
            ['Non-Compliant:', f"{non_compliant} ({non_compliant/total_contracts*100:.1f}%)"],
            ['Pending Review:', f"{pending} ({pending/total_contracts*100:.1f}%)"],
            ['High Risk Contracts:', f"{high_risk} ({high_risk/total_contracts*100:.1f}%)"],
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Contracts Table
        story.append(Paragraph("Contract Details", self.styles['SectionTitle']))
        
        # Table headers
        headers = ['Contract #', 'Vendor', 'Risk', 'Status', 'End Date']
        data = [headers]
        
        # Add contract rows
        for contract in contracts:
            row = [
                contract.get('contract_number', 'N/A'),
                contract.get('vendor_name', 'N/A')[:30],  # Truncate long names
                contract.get('risk_level', 'N/A').upper(),
                contract.get('compliance_status', 'N/A').replace('_', ' ').title(),
                contract.get('end_date', 'N/A')
            ]
            data.append(row)
        
        # Create table
        contracts_table = Table(data, colWidths=[1.5*inch, 2*inch, 0.8*inch, 1.5*inch, 1*inch])
        
        # Style the table
        table_style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Center align risk column
        ])
        
        # Color code risk levels
        for i, contract in enumerate(contracts, 1):
            risk_level = contract.get('risk_level', '').lower()
            if risk_level == 'high':
                table_style.add('TEXTCOLOR', (2, i), (2, i), colors.red)
            elif risk_level == 'medium':
                table_style.add('TEXTCOLOR', (2, i), (2, i), colors.orange)
            elif risk_level == 'low':
                table_style.add('TEXTCOLOR', (2, i), (2, i), colors.green)
        
        contracts_table.setStyle(table_style)
        story.append(contracts_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer