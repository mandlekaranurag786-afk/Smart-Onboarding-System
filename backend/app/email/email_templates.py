"""
HTML Email Templates for OnboardIQ
Uses Jinja2 for dynamic content
"""
from jinja2 import Template


# Base HTML template with styling
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .email-container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 3px solid #4CAF50;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #4CAF50;
        }
        .subtitle {
            color: #666;
            font-size: 14px;
        }
        h1 {
            color: #2c3e50;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .info-box {
            background-color: #f8f9fa;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .info-box strong {
            color: #2c3e50;
        }
        .task-list {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .task-list ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .task-list li {
            margin: 8px 0;
        }
        .button {
            display: inline-block;
            padding: 12px 30px;
            margin: 10px 5px;
            background-color: #4CAF50;
            color: white !important;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            text-align: center;
        }
        .button-danger {
            background-color: #f44336;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
        .credentials {
            background-color: #e3f2fd;
            border: 2px dashed #2196F3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">🚀 OnboardIQ</div>
            <div class="subtitle">by KONVERGE.AI</div>
        </div>
        {{ content }}
        <div class="footer">
            <p>This is an automated email from OnboardIQ by KONVERGE.AI</p>
            <p>If you have any questions, please contact HR at <a href="mailto:{{ hr_email }}">{{ hr_email }}</a></p>
        </div>
    </div>
</body>
</html>
"""


# 1. Welcome Email Template
WELCOME_EMAIL_TEMPLATE = """
<h1>Welcome to the Team, {{ candidate_name }}! 🎉</h1>

<p>We're thrilled to have you join us as <strong>{{ role }}</strong> in the <strong>{{ department }}</strong> department!</p>

<div class="info-box">
    <strong>📅 Joining Date:</strong> {{ joining_date }}<br>
    <strong>👤 Reporting Manager:</strong> {{ reporting_manager }}
</div>

<h2>Your Login Credentials</h2>
<div class="credentials">
    <strong>Email:</strong> {{ login_email }}<br>
    <strong>Password:</strong> {{ login_password }}<br>
    <br>
    <em>⚠️ Please change your password after first login</em>
</div>

<h2>Your Onboarding Tasks</h2>
<div class="task-list">
    <p><strong>Please complete the following mandatory tasks:</strong></p>
    <ul>
    {% for task in tasks %}
        <li>{{ task }}</li>
    {% endfor %}
    </ul>
</div>

<p style="margin-top: 30px;">
    <a href="{{ portal_url }}" class="button">Access Onboarding Portal</a>
</p>

<p>We're excited to have you on board and look forward to your contributions!</p>

<p>Best regards,<br>
<strong>The OnboardIQ Team</strong></p>
"""


# 2. IT Team Notification Template
IT_NOTIFICATION_TEMPLATE = """
<h1>🖥️ New Joiner - IT Setup Required</h1>

<p>A new employee is joining and requires IT setup and asset allocation.</p>

<div class="info-box">
    <strong>👤 Name:</strong> {{ candidate_name }}<br>
    <strong>📧 Email:</strong> {{ candidate_email }}<br>
    <strong>💼 Role:</strong> {{ role }}<br>
    <strong>🏢 Department:</strong> {{ department }}<br>
    <strong>📅 Joining Date:</strong> {{ joining_date }}<br>
    <strong>👔 Reporting Manager:</strong> {{ reporting_manager }}
</div>

<h2>Action Required:</h2>
<ul>
    <li>✅ Allocate laptop/workstation</li>
    <li>✅ Create Employee ID</li>
    <li>✅ Setup email account</li>
    <li>✅ Provide necessary software licenses</li>
    <li>✅ Configure access permissions</li>
</ul>

<p><strong>⏰ Please ensure all assets are ready before the joining date.</strong></p>

<p>Best regards,<br>
<strong>OnboardIQ Automation System</strong></p>
"""


# 3. Manager Notification Template
MANAGER_NOTIFICATION_TEMPLATE = """
<h1>👋 New Team Member Joining</h1>

<p>Dear {{ manager_name }},</p>

<p>A new team member has been assigned to you and will be joining soon!</p>

<div class="info-box">
    <strong>👤 Name:</strong> {{ candidate_name }}<br>
    <strong>📧 Email:</strong> {{ candidate_email }}<br>
    <strong>💼 Role:</strong> {{ role }}<br>
    <strong>🏢 Department:</strong> {{ department }}<br>
    <strong>📅 Joining Date:</strong> {{ joining_date }}
</div>

<h2>Next Steps:</h2>
<ul>
    <li>📅 Schedule a welcome meeting</li>
    <li>📋 Prepare onboarding plan</li>
    <li>👥 Introduce to the team</li>
    <li>🎯 Set initial goals and expectations</li>
</ul>

<p>HR will coordinate with you to schedule the onboarding meeting.</p>

<p>Best regards,<br>
<strong>OnboardIQ Team</strong></p>
"""


# 4. Laptop Confirmation Template
LAPTOP_CONFIRMATION_TEMPLATE = """
<h1>💻 Laptop Delivery Confirmation</h1>

<p>Hi {{ candidate_name }},</p>

<p>We hope you're settling in well! We'd like to confirm whether you've received your laptop and IT assets.</p>

<div class="info-box">
    <p><strong>Please confirm by clicking one of the buttons below:</strong></p>
</div>

<div style="text-align: center; margin: 30px 0;">
    <a href="{{ confirmation_link_yes }}" class="button">✅ Yes, I received it</a>
    <a href="{{ confirmation_link_no }}" class="button button-danger">❌ No, not yet</a>
</div>

<p><em>This helps us track asset delivery and ensure you have everything you need to get started.</em></p>

<p>Thank you!<br>
<strong>OnboardIQ Team</strong></p>
"""


# 5. HR Alert Template
HR_ALERT_TEMPLATE = """
<h1>🔔 OnboardIQ Alert</h1>

<p><strong>Alert Type:</strong> {{ alert_type }}</p>

<div class="info-box">
    <strong>👤 Candidate:</strong> {{ candidate_name }}<br>
    <strong>📧 Email:</strong> {{ candidate_email }}<br>
</div>

<h2>Message:</h2>
<div class="task-list">
    <p>{{ message }}</p>
</div>

{% if additional_info %}
<h2>Additional Information:</h2>
<div class="info-box">
    {% for key, value in additional_info.items() %}
        <strong>{{ key }}:</strong> {{ value }}<br>
    {% endfor %}
</div>
{% endif %}

<p>Please take appropriate action.</p>

<p>Best regards,<br>
<strong>OnboardIQ Automation System</strong></p>
"""


def render_email(template_content: str, data: dict, hr_email: str) -> str:
    """
    Render email template with data
    
    Args:
        template_content: The email template content
        data: Dictionary with template variables
        hr_email: HR contact email
        
    Returns:
        Rendered HTML email
    """
    # Render the content template
    content_template = Template(template_content)
    rendered_content = content_template.render(**data)
    
    # Wrap in base template
    base = Template(BASE_TEMPLATE)
    return base.render(content=rendered_content, hr_email=hr_email)
