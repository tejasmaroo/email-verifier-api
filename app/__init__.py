from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import os
import logging
from validate_email import validate_email
import time
import ssl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('email-verifier-api')

app = Flask(__name__)
CORS(app)

# Register error handlers
@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"Bad request: {request.remote_addr} - {error}")
    return jsonify({
        'error': 'Bad Request',
        'message': 'The server could not understand the request due to invalid syntax',
        'status_code': 400
    }), 400

@app.errorhandler(404)
def not_found(error):
    logger.info(f"Not found: {request.remote_addr} - {request.path}")
    return jsonify({
        'error': 'Not Found',
        'message': f'The requested URL {request.path} was not found on the server',
        'status_code': 404
    }), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'The server encountered an internal error and was unable to complete your request',
        'status_code': 500
    }), 500

# Added a root route for better UX
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'Email Verifier API',
        'version': '1.0.0',
        'endpoints': {
            '/api/verify': 'POST - Verify an email address',
            '/api/health': 'GET - Check service health'
        },
        'documentation': 'See README.md for full documentation'
    })

@app.route('/api/verify', methods=['POST'])
def verify_email():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            logger.warning(f"Missing email in request: {request.remote_addr}")
            return jsonify({'error': 'Email address is required'}), 400
        
        email = data['email']
        logger.info(f"Verifying email: {email} - Request from {request.remote_addr}")
        
        # Start with basic syntax check
        result = {
            'email': email,
            'is_valid_format': False,
            'is_deliverable': False,
            'has_mx_records': False,
            'is_disposable': False,
            'message': '',
            'verification_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Check email syntax
        syntax_valid = validate_email(email, check_format=True, check_blacklist=False, 
                                      check_dns=False, check_smtp=False)
        result['is_valid_format'] = bool(syntax_valid)
        
        if not syntax_valid:
            result['message'] = 'Invalid email format'
            return jsonify(result)
        
        # Check MX records and deliverability
        mx_check = validate_email(email, check_format=False, check_blacklist=False, 
                                 check_dns=True, check_smtp=False)
        result['has_mx_records'] = bool(mx_check)
        
        if not mx_check:
            result['message'] = 'Domain does not have valid MX records'
            return jsonify(result)
        
        # Check SMTP with better error handling and timeout
        try:
            smtp_check = validate_email(email, check_format=False, check_blacklist=False, 
                                      check_dns=False, check_smtp=True, smtp_timeout=10, 
                                      smtp_helo_host='my.host.name', smtp_from_address='verify@example.com')
            result['is_deliverable'] = bool(smtp_check)
            
            if not smtp_check:
                result['message'] = 'Email address is not deliverable'
            else:
                result['message'] = 'Email address is valid and deliverable'
        except Exception as smtp_error:
            logger.warning(f"SMTP check failed for {email}: {str(smtp_error)}")
            result['message'] = f'SMTP verification failed: {str(smtp_error)}'
            result['is_deliverable'] = False
            
        # Check if disposable - expanded list
        disposable_domains = [
            'mailinator.com', 'guerrillamail.com', 'tempmail.com', 'temp-mail.org', 
            'throwawaymail.com', 'yopmail.com', '10minutemail.com', 'mailnesia.com',
            'dispostable.com', 'maildrop.cc', 'harakirimail.com', 'mailcatch.com',
            'trashmail.com', 'sharklasers.com', 'spam4.me', 'grr.la', 'minuteinbox.com'
        ]
        domain = email.split('@')[-1].lower()
        result['is_disposable'] = domain in disposable_domains
        
        logger.info(f"Verification result for {email}: format={result['is_valid_format']}, "
                   f"mx={result['has_mx_records']}, deliverable={result['is_deliverable']}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Verification failed with exception: {str(e)}")
        return jsonify({
            'error': 'Verification failed',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    logger.debug(f"Health check from {request.remote_addr}")
    return jsonify({
        'status': 'ok', 
        'service': 'email-verifier-api',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

