from flask import current_app, render_template_string
from flask_mail import Mail, Message
from typing import List, Dict, Optional
from datetime import datetime

class EmailService:
    def __init__(self, mail: Mail):
        self.mail = mail
    
    def send_alert_email(self, recipient: str, alert: Dict) -> bool:
        """Send alert notification email"""
        try:
            subject = f"[{alert['severity'].upper()}] Compliance Alert: {alert['title']}"
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; }
                    .alert-box { 
                        border: 2px solid #ddd; 
                        padding: 20px; 
                        margin: 20px 0;
                        border-radius: 5px;
                    }
                    .high { border-color: #dc3545; background-color: #f8d7da; }
                    .medium { border-color: #ffc107; background-color: #fff3cd; }
                    .low { border-color: #28a745; background-color: #d4edda; }
                    .critical { border-color: #721c24; background-color: #f8d7da; }
                    h2 { color: #333; }
                    .details { margin: 10px 0; }
                    .footer { margin-top: 30px; font-size: 0.9em; color: #666; }
                </style>
            </head>
            <body>
                <h2>Compliance Alert Notification</h2>
                <div class="alert-box {{ alert.severity }}">
                    <h3>{{ alert.title }}</h3>
                    <div class="details">
                        <p><strong>Type:</strong> {{ alert.alert_type }}</p>
                        <p><strong>Severity:</strong> {{ alert.severity }}</p>
                        <p><strong>Contract:</strong> {{ alert.contract }} - {{ alert.vendor }}</p>
                        <p><strong>Trigger Date:</strong> {{ alert.trigger_date }}</p>
                    </div>
                    <div class="message">
                        <p>{{ alert.message }}</p>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated notification from the Compliance Audit System.</p>
                    <p>Please log in to the system to review and acknowledge this alert.</p>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=render_template_string(html_template, alert=alert),
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Email sending error: {e}")
            return False
    
    def send_audit_reminder(self, recipient: str, contracts: List[Dict]) -> bool:
        """Send audit reminder email"""
        try:
            subject = f"Compliance Audit Reminder - {len(contracts)} Contracts Due"
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background-color: #f4f4f4; }
                    .high { color: #dc3545; font-weight: bold; }
                    .medium { color: #ffc107; }
                    .low { color: #28a745; }
                </style>
            </head>
            <body>
                <h2>Compliance Audit Reminder</h2>
                <p>The following contracts are due for compliance audit:</p>
                
                <table>
                    <thead>
                        <tr>
                            <th>Contract Number</th>
                            <th>Vendor</th>
                            <th>Risk Level</th>
                            <th>Last Audit</th>
                            <th>Next Audit Due</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for contract in contracts %}
                        <tr>
                            <td>{{ contract.contract_number }}</td>
                            <td>{{ contract.vendor_name }}</td>
                            <td class="{{ contract.risk_level }}">{{ contract.risk_level|upper }}</td>
                            <td>{{ contract.last_audit_date or 'Never' }}</td>
                            <td>{{ contract.next_audit_date }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <p>Please log in to the Compliance Audit System to review these contracts.</p>
                
                <div style="margin-top: 30px; font-size: 0.9em; color: #666;">
                    <p>This is an automated reminder from the Compliance Audit System.</p>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=render_template_string(html_template, contracts=contracts),
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Email sending error: {e}")
            return False
    
    def send_contract_expiration_notice(self, recipient: str, contract: Dict, days_until_expiry: int) -> bool:
        """Send contract expiration notice"""
        try:
            subject = f"Contract Expiration Notice - {contract['contract_number']}"
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; }
                    .warning-box { 
                        border: 2px solid #ffc107; 
                        background-color: #fff3cd;
                        padding: 20px; 
                        margin: 20px 0;
                        border-radius: 5px;
                    }
                    .details { margin: 10px 0; }
                    .details p { margin: 5px 0; }
                </style>
            </head>
            <body>
                <h2>Contract Expiration Notice</h2>
                
                <div class="warning-box">
                    <h3>Contract Expiring Soon</h3>
                    <div class="details">
                        <p><strong>Contract Number:</strong> {{ contract.contract_number }}</p>
                        <p><strong>Vendor:</strong> {{ contract.vendor_name }}</p>
                        <p><strong>Title:</strong> {{ contract.title }}</p>
                        <p><strong>Expiration Date:</strong> {{ contract.end_date }}</p>
                        <p><strong>Days Until Expiry:</strong> {{ days_until_expiry }}</p>
                    </div>
                </div>
                
                <p>Please take appropriate action:</p>
                <ul>
                    <li>Review the contract terms</li>
                    <li>Initiate renewal discussions if needed</li>
                    <li>Prepare for contract termination if not renewing</li>
                    <li>Ensure all compliance requirements are met before expiry</li>
                </ul>
                
                <div style="margin-top: 30px; font-size: 0.9em; color: #666;">
                    <p>This is an automated notification from the Compliance Audit System.</p>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=render_template_string(
                    html_template, 
                    contract=contract, 
                    days_until_expiry=days_until_expiry
                ),
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Email sending error: {e}")
            return False
    
    def send_welcome_email(self, recipient: str, username: str, temp_password: Optional[str] = None) -> bool:
        """Send welcome email to new user"""
        try:
            subject = "Welcome to Compliance Audit System"
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; }
                    .info-box { 
                        background-color: #e3f2fd;
                        padding: 20px; 
                        margin: 20px 0;
                        border-radius: 5px;
                    }
                </style>
            </head>
            <body>
                <h2>Welcome to the Compliance Audit System</h2>
                
                <p>Hello {{ username }},</p>
                
                <p>Your account has been created successfully. You can now access the Compliance Audit System to:</p>
                <ul>
                    <li>Upload and analyze vendor contracts</li>
                    <li>Track compliance requirements</li>
                    <li>Receive alerts for important dates and obligations</li>
                    <li>Generate compliance reports</li>
                </ul>
                
                {% if temp_password %}
                <div class="info-box">
                    <p><strong>Your temporary password is:</strong> {{ temp_password }}</p>
                    <p>Please change this password after your first login.</p>
                </div>
                {% endif %}
                
                <p>If you have any questions, please contact your system administrator.</p>
                
                <div style="margin-top: 30px; font-size: 0.9em; color: #666;">
                    <p>Best regards,<br>Compliance Audit System Team</p>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=render_template_string(
                    html_template, 
                    username=username, 
                    temp_password=temp_password
                ),
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Email sending error: {e}")
            return False