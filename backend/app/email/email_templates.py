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
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 600px;
            margin: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
        }
        .header {
            background-color: #007BFF;
            color: white;
            padding: 15px;
            border-radius: 6px 6px 0 0;
            text-align: center;
        }
        .info-box {
            background-color: #f4f8ff;
            padding: 15px;
            border-left: 4px solid #007BFF;
            margin: 20px 0;
            border-radius: 4px;
        }
        .credentials {
            background-color: #fff7e6;
            padding: 15px;
            border-left: 4px solid #ffa500;
            margin: 20px 0;
            border-radius: 4px;
        }
        .task-box {
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #28a745;
            margin: 20px 0;
            border-radius: 4px;
        }
        ul {
            padding-left: 20px;
        }
        .button {
            display: inline-block;
            padding: 12px 20px;
            color: white;
            background-color: #007BFF;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
        .button:hover {
            background-color: #0056b3;
        }
        .footer {
            margin-top: 25px;
            font-size: 14px;
            color: #777;
        }
        .highlight {
            color: #d9534f;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div class="container">

    <div class="header">
        <h2>🎉 Welcome to the Team, {{ candidate_name }}!</h2>
    </div>

    <p>Hello {{ candidate_name }},</p>

    <p>We’re excited to welcome you to the team! You will be joining us as a <strong>{{ role }}</strong> in the <strong>{{ department }}</strong> department.</p>

    <div class="info-box">
        <p><strong> Joining Date:</strong> {{ joining_date }}</p>
        <p><strong> Reporting Manager:</strong> {{ reporting_manager }}</p>
    </div>

    <h3> Your Login Credentials</h3>
    <div class="credentials">
        <p><strong>Email:</strong> {{ login_email }}</p>
        <p><strong>Password:</strong> {{ login_password }}</p>
        <p class="highlight"> For security reasons, please change your password after your first login.</p>
    </div>

    <h3>📋 Your Onboarding Tasks</h3>
    <div class="task-box">
        <p><strong>Please complete the following tasks to get started:</strong></p>
        <ul>
        {% for task in tasks %}
            <li>{{ task }}</li>
        {% endfor %}
        </ul>
    </div>

    <p style="margin-top: 30px; text-align: center;">
        <a href="{{ portal_url }}" class="button"> Access Onboarding Portal</a>
    </p>

    <p>If you need any assistance during your onboarding journey, feel free to reach out to your manager or HR team.</p>

    <p>We’re looking forward to seeing your impact and contributions. Welcome aboard! </p>

    <div class="footer">
        <p>Best regards,<br>
        <strong>HR Team</strong></p>
    </div>

</div>

</body>
</html>
"""

# 2. IT Team Notification Template
IT_NOTIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 600px;
            margin: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
        }
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            border-radius: 6px 6px 0 0;
            text-align: center;
        }
        .info-box {
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #4CAF50;
            margin: 20px 0;
            border-radius: 4px;
        }
        .info-box p {
            margin: 5px 0;
        }
        .section-title {
            font-weight: bold;
            margin-top: 20px;
        }
        ul {
            padding-left: 20px;
        }
        .footer {
            margin-top: 25px;
            font-size: 14px;
            color: #777;
        }
        .highlight {
            color: #d9534f;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div class="container">

    <div class="header">
        <h2>🖥️ IT Setup Required for New Joiner</h2>
    </div>

    <p>Hello IT Team,</p>

    <p>A new employee onboarding has been initiated. Please find the details below and ensure all required IT setup is completed before the joining date.</p>

    <div class="info-box">
        <p><strong>Name:</strong> {{ candidate_name }}</p>
        <p><strong>Email:</strong> {{ candidate_email }}</p>
        <p><strong>Role:</strong> {{ role }}</p>
        <p><strong>Department:</strong> {{ department }}</p>
        <p><strong>Joining Date:</strong> {{ joining_date }}</p>
        <p><strong>Reporting Manager:</strong> {{ reporting_manager }}</p>
    </div>

    <div class="section-title">🔧 Action Items:</div>
    <ul>
        <li>Allocate laptop/workstation</li>
       
        <li>Set up official email account</li>
        <li>Assign required software licenses</li>
        <li>Configure system and access permissions</li>
    </ul>

    <p class="highlight">⏰ Ensure all setups are completed before the joining date to avoid onboarding delays.</p>

    <p>If you have any questions or dependencies, please coordinate with the HR team.</p>

    <div class="footer">
        <p>Best regards,<br>
        <strong>HR Team</strong></p>
    </div>

</div>

</body>
</html>
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


# 6b. Work Profile Builder Email Template (Candidate)
WORK_PROFILE_BUILDER_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            line-height: 1.7;
            background-color: #f0f4ff;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 620px;
            margin: auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }
        .header {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            color: white;
            padding: 30px 30px 24px;
            text-align: center;
        }
        .header .brand {
            font-size: 13px;
            letter-spacing: 2px;
            text-transform: uppercase;
            opacity: 0.85;
            margin-bottom: 10px;
        }
        .header h1 {
            margin: 0;
            font-size: 26px;
            font-weight: 700;
        }
        .header .emoji {
            font-size: 40px;
            display: block;
            margin-bottom: 12px;
        }
        .body-content {
            padding: 32px 36px;
        }
        .greeting {
            font-size: 16px;
            margin-bottom: 18px;
            color: #2c3e50;
        }
        .what-is-box {
            background-color: #f0edff;
            border-left: 5px solid #4F46E5;
            border-radius: 6px;
            padding: 18px 20px;
            margin: 22px 0;
        }
        .what-is-box h2 {
            margin: 0 0 10px;
            font-size: 16px;
            color: #4F46E5;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .what-is-box p {
            margin: 0;
            font-size: 15px;
            color: #3d3d5c;
        }
        .why-box {
            background-color: #fff7ed;
            border-left: 5px solid #F59E0B;
            border-radius: 6px;
            padding: 18px 20px;
            margin: 22px 0;
        }
        .why-box h2 {
            margin: 0 0 10px;
            font-size: 16px;
            color: #d97706;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .why-box ul {
            margin: 0;
            padding-left: 20px;
        }
        .why-box ul li {
            margin: 8px 0;
            font-size: 15px;
            color: #3d3d5c;
        }
        .steps-box {
            background-color: #f0fdf4;
            border-left: 5px solid #22C55E;
            border-radius: 6px;
            padding: 18px 20px;
            margin: 22px 0;
        }
        .steps-box h2 {
            margin: 0 0 10px;
            font-size: 16px;
            color: #16a34a;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .steps-box ol {
            margin: 0;
            padding-left: 20px;
        }
        .steps-box ol li {
            margin: 8px 0;
            font-size: 15px;
            color: #3d3d5c;
        }
        .cta-area {
            text-align: center;
            margin: 32px 0 20px;
        }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            color: white !important;
            text-decoration: none;
            padding: 15px 36px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .cta-note {
            font-size: 13px;
            color: #888;
            margin-top: 10px;
        }
        .deadline-banner {
            background-color: #fef2f2;
            border: 1.5px solid #fca5a5;
            border-radius: 6px;
            padding: 12px 18px;
            margin: 22px 0;
            font-size: 14px;
            color: #b91c1c;
            text-align: center;
        }
        .footer {
            background-color: #f8f8f8;
            padding: 20px 36px;
            border-top: 1px solid #ebebeb;
            font-size: 13px;
            color: #888;
            text-align: center;
        }
        .footer a {
            color: #4F46E5;
            text-decoration: none;
        }
    </style>
</head>
<body>
<div class="container">

    <div class="header">
        <span class="brand">OnboardIQ &bull; KONVERGE.AI</span>
        <span class="emoji">🧑‍💼</span>
        <h1>Complete Your Work Profile</h1>
    </div>

    <div class="body-content">

        <p class="greeting">Hi <strong>{{ candidate_name }}</strong>,</p>

        <p>Welcome aboard! 🎉 As part of your onboarding journey at <strong>{{ department }}</strong>, we need you to complete your <strong>Work Profile Builder</strong> — one of the first and most important steps before your joining date.</p>

        <div class="what-is-box">
            <h2>🔍 What is the Work Profile Builder?</h2>
            <p>The <strong>Work Profile Builder</strong> is a structured form where you provide essential professional information about yourself — your skills, past experience, tools you work with, and your preferences. This helps us tailor your onboarding experience and set you up for success from day one.</p>
        </div>

        <div class="why-box">
            <h2>💡 Why are we collecting this?</h2>
            <ul>
                <li>📋 <strong>Personalised onboarding</strong> — we configure your training plan based on your background</li>
                <li>🛠️ <strong>Tool &amp; access provisioning</strong> — IT sets up the right software and permissions for your role</li>
                <li>🤝 <strong>Better team alignment</strong> — your manager and team get context before you officially join</li>
                <li>📈 <strong>Faster ramp-up</strong> — reduces first-week friction so you can hit the ground running</li>
                <li>🏢 <strong>Official records</strong> — your profile becomes part of the company's HR system</li>
            </ul>
        </div>

        <div class="steps-box">
            <h2>✅ How to complete it</h2>
            <ol>
                <li>Click the button below to log in to the Onboarding Portal</li>
                <li>Navigate to <strong>"Work Profile Builder"</strong> from your dashboard</li>
                <li>Fill in all required sections (takes ~10 minutes)</li>
                <li>Submit and you're done — we'll take it from there!</li>
            </ol>
        </div>

        {% if joining_date %}
        <div class="deadline-banner">
            ⏰ Please complete your Work Profile before your joining date: <strong>{{ joining_date }}</strong>
        </div>
        {% endif %}

        <div class="cta-area">
            <a href="{{ portal_url }}" class="cta-button">🚀 Go to Onboarding Portal</a>
            <p class="cta-note">Log in with your registered email: <strong>{{ candidate_email }}</strong></p>
        </div>

        <p>If you face any issues accessing the portal or have questions about the form, reach out to your HR team — we're happy to help!</p>

        <p>Looking forward to having you on board 🙌</p>

        <p style="margin-top: 20px;">Best regards,<br>
        <strong>HR Team, KONVERGE.AI</strong></p>

    </div>

    <div class="footer">
        <p>This is an automated email from <strong>OnboardIQ</strong> by KONVERGE.AI.</p>
        <p>Questions? Contact HR at <a href="mailto:{{ hr_email }}">{{ hr_email }}</a></p>
    </div>

</div>
</body>
</html>
"""


def render_work_profile_builder_email(
    candidate_name: str,
    candidate_email: str,
    department: str,
    joining_date: str,
    portal_url: str,
    hr_email: str
) -> str:
    """
    Render Work Profile Builder email for the candidate.

    Args:
        candidate_name: Full name of the candidate
        candidate_email:  Email of the candidate (shown as login hint)
        department: Department the candidate is joining
        joining_date: Formatted joining date string (e.g. "May 01, 2026")
        portal_url: URL to the onboarding / Work Profile Builder portal
        hr_email: HR contact email shown in the footer

    Returns:
        Rendered HTML email string
    """
    data = {
        'candidate_name': candidate_name,
        'candidate_email': candidate_email,
        'department': department,
        'joining_date': joining_date,
        'portal_url': portal_url,
        'hr_email': hr_email,
    }
    template = Template(WORK_PROFILE_BUILDER_EMAIL_TEMPLATE)
    return template.render(**data)


# 6. IT Equipment Allocation Template (with Action Buttons)
IT_EQUIPMENT_ALLOCATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 600px;
            margin: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            background-color: #ffffff;
        }
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 6px 6px 0 0;
            text-align: center;
        }
        .info-box {
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #4CAF50;
            margin: 20px 0;
            border-radius: 4px;
        }
        .info-box p {
            margin: 8px 0;
        }
        .section-title {
            font-weight: bold;
            font-size: 16px;
            margin-top: 20px;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        ul {
            padding-left: 20px;
            margin: 10px 0;
        }
        ul li {
            margin: 8px 0;
        }
        .action-buttons {
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        .btn-complete {
            display: inline-block;
            background-color: #4CAF50;
            color: white !important;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 0 10px;
            font-weight: bold;
            font-size: 16px;
        }
        .btn-complete:hover {
            background-color: #45a049;
        }
        .btn-need-time {
            display: inline-block;
            background-color: #FF9800;
            color: white !important;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 0 10px;
            font-weight: bold;
            font-size: 16px;
        }
        .btn-need-time:hover {
            background-color: #e68900;
        }
        .footer {
            margin-top: 25px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
            color: #777;
            text-align: center;
        }
        .task-id {
            font-family: 'Courier New', monospace;
            background-color: #f0f0f0;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
        }
        .highlight {
            color: #d9534f;
            font-weight: bold;
        }
        .note {
            font-size: 14px;
            color: #666;
            text-align: center;
            margin-top: 15px;
            font-style: italic;
        }
    </style>
</head>
<body>

<div class="container">

    <div class="header">
        <h2>🖥️ IT Setup Required for New Joiner</h2>
    </div>

    <p>Hello IT Team,</p>

    <p>A new employee onboarding has been initiated. Please allocate equipment and complete setup.</p>

    <div class="info-box">
        <p><strong>Name:</strong> {{ candidate_name }}</p>
        <p><strong>Email:</strong> {{ candidate_email }}</p>
        <p><strong>Role:</strong> {{ role }}</p>
        <p><strong>Department:</strong> {{ department }}</p>
        <p><strong>Joining Date:</strong> {{ joining_date }}</p>
        <p><strong>Reporting Manager:</strong> {{ reporting_manager }}</p>
    </div>

    <div class="section-title">🔧 Required Actions:</div>
    <ul>
        <li>Allocate laptop/workstation</li>
        <li>Set up official email account</li>
        <li>Assign required software licenses</li>
        <li>Configure system and access permissions</li>
    </ul>

    <p class="highlight">⏰ Please complete setup before the joining date: {{ joining_date }}</p>

    <div class="action-buttons">
        <p style="margin-bottom: 20px;"><strong>Once completed, please confirm:</strong></p>
        <a href="{{ complete_url }}" class="btn-complete">✅ Allocation Complete</a>
        <a href="{{ need_time_url }}" class="btn-need-time">⏰ Need More Time</a>
    </div>

    <p class="note">You can also reply directly to this email with your status update.</p>

    <div class="footer">
        <p>Task ID: <span class="task-id">{{ task_token }}</span></p>
        <p>Best regards,<br><strong>OnboardIQ System</strong></p>
    </div>

</div>

</body>
</html>
"""



def render_it_equipment_allocation_email(
    candidate_name: str,
    candidate_email: str,
    role: str,
    department: str,
    joining_date: str,
    reporting_manager: str,
    task_token: str,
    backend_url: str
) -> str:
    """
    Render IT equipment allocation email with action buttons
    
    Args:
        candidate_name: Name of the new joiner
        candidate_email: Email of the new joiner
        role: Job role
        department: Department name
        joining_date: Joining date (formatted string)
        reporting_manager: Manager's name
        task_token: Unique task response token
        backend_url: Backend API URL for webhook callbacks
        
    Returns:
        Rendered HTML email with action buttons
        
    Example:
        >>> email_html = render_it_equipment_allocation_email(
        ...     candidate_name="John Doe",
        ...     candidate_email="john.doe@company.com",
        ...     role="Software Engineer",
        ...     department="Engineering",
        ...     joining_date="2024-01-15",
        ...     reporting_manager="Jane Smith",
        ...     task_token="123_1704902400_a1b2c3d4",
        ...     backend_url="https://api.onboardiq.com"
        ... )
    """
    from urllib.parse import urlencode
    
    # Build action button URLs
    complete_params = urlencode({
        'token': task_token,
        'response': 'complete'
    })
    need_time_params = urlencode({
        'token': task_token,
        'response': 'need_time'
    })
    
    complete_url = f"{backend_url}/api/it-tasks/response/button?{complete_params}"
    need_time_url = f"{backend_url}/api/it-tasks/response/button?{need_time_params}"
    
    # Prepare template data
    data = {
        'candidate_name': candidate_name,
        'candidate_email': candidate_email,
        'role': role,
        'department': department,
        'joining_date': joining_date,
        'reporting_manager': reporting_manager,
        'task_token': task_token,
        'complete_url': complete_url,
        'need_time_url': need_time_url
    }
    
    # Render template
    template = Template(IT_EQUIPMENT_ALLOCATION_TEMPLATE)
    return template.render(**data)
