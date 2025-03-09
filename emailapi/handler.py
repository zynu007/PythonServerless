import json
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def send_email(event, context):
    """
    Lambda function to send email using Gmail SMTP
    """
    # Parse request body
    try:
        body = json.loads(event['body'])
        
        # Extract required fields
        receiver_email = body.get('receiver_email')
        subject = body.get('subject')
        body_text = body.get('body_text')
        
        # Validate inputs
        if not receiver_email:
            return create_response(400, {'error': 'receiver_email is required'})
        if not subject:
            return create_response(400, {'error': 'subject is required'})
        if not body_text:
            return create_response(400, {'error': 'body_text is required'})
        
        # Get Gmail credentials from environment variables
        gmail_user = os.environ.get('GMAIL_USER')
        gmail_password = os.environ.get('GMAIL_PASSWORD')
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain'))
        
        # Send email using Gmail SMTP
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            text = msg.as_string()
            server.sendmail(gmail_user, receiver_email, text)
            server.quit()
            
            # Return success response
            return create_response(200, {
                'message': 'Email sent successfully',
                'to': receiver_email
            })
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return create_response(500, {'error': f'Failed to send email: {str(e)}'})
        
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def serve_form(event, context):
    """
    Function to serve the HTML form for sending emails
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Send Email Form</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input[type="email"],
            input[type="text"],
            textarea {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            textarea {
                height: 150px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #45a049;
            }
            .alert {
                padding: 10px;
                margin-bottom: 15px;
                display: none;
                border-radius: 4px;
            }
            .alert-success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .alert-error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <h1>Send Email</h1>
        
        <div id="successAlert" class="alert alert-success">
            Email sent successfully!
        </div>
        
        <div id="errorAlert" class="alert alert-error">
            Error sending email. Please try again.
        </div>
        
        <form id="emailForm">
            <div class="form-group">
                <label for="receiver_email">Recipient Email:</label>
                <input type="email" id="receiver_email" name="receiver_email" required>
            </div>
            
            <div class="form-group">
                <label for="subject">Subject:</label>
                <input type="text" id="subject" name="subject" required>
            </div>
            
            <div class="form-group">
                <label for="body_text">Message:</label>
                <textarea id="body_text" name="body_text" required></textarea>
            </div>
            
            <button type="submit">Send Email</button>
        </form>
        
        <script>
            document.getElementById('emailForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const receiverEmail = document.getElementById('receiver_email').value;
                const subject = document.getElementById('subject').value;
                const bodyText = document.getElementById('body_text').value;
                
                // Hide any visible alerts
                document.getElementById('successAlert').style.display = 'none';
                document.getElementById('errorAlert').style.display = 'none';
                
                // Send the request to the API
                fetch('/dev/send-email', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        receiver_email: receiverEmail,
                        subject: subject,
                        body_text: bodyText
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        // Show success message
                        document.getElementById('successAlert').style.display = 'block';
                        document.getElementById('emailForm').reset();
                    } else {
                        // Show error message
                        document.getElementById('errorAlert').textContent = data.error || 'Error sending email';
                        document.getElementById('errorAlert').style.display = 'block';
                    }
                })
                .catch(error => {
                    document.getElementById('errorAlert').textContent = 'Error connecting to server';
                    document.getElementById('errorAlert').style.display = 'block';
                    console.error('Error:', error);
                });
            });
        </script>
    </body>
    </html>
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*',
        },
        'body': html
    }

def create_response(status_code, body):
    """
    Helper function to create response with CORS headers
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(body)
    }