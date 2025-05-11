# Email Verifier API

A simple REST API that verifies email addresses without sending actual emails.

## Features

- Email syntax validation
- Domain MX record verification
- SMTP mailbox existence check (without sending emails)
- Disposable email detection
- Ready for deployment to Render and similar platforms
- Proper error handling and logging

## API Endpoints

### Root Endpoint
**Endpoint**: `/`
**Method**: `GET`

Returns API information and available endpoints.

### Verify Email

**Endpoint**: `/api/verify`
**Method**: `POST`
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "email": "example@domain.com"
}
```

**Response**:
```json
{
  "email": "example@domain.com",
  "is_valid_format": true,
  "is_deliverable": true,
  "has_mx_records": true,
  "is_disposable": false,
  "message": "Email address is valid and deliverable",
  "verification_date": "2025-05-11 12:00:00"
}
```

### Health Check

**Endpoint**: `/api/health`
**Method**: `GET`

**Response**:
```json
{
  "status": "ok",
  "service": "email-verifier-api",
  "timestamp": "2025-05-11 12:00:00"
}
```

## Local Development

1. Create and activate a virtual environment:
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```
   python -m app.main
   ```

4. The API will be available at `http://localhost:5000`

## HTTPS Support

By default, the API runs on HTTP only. To enable HTTPS, set the following environment variables:

```
export SSL_CERT_PATH=/path/to/your/certificate.pem
export SSL_KEY_PATH=/path/to/your/private_key.pem
```

If you're seeing errors like:
```
127.0.0.1 - - [DATE] code 400, message Bad request version ('À\x13À')
```

This means a client is trying to connect with HTTPS to your HTTP-only server. Solutions:
1. Enable HTTPS as shown above
2. Make sure clients connect with HTTP not HTTPS if you don't have certificates
3. When deploying to Render, HTTPS is automatically handled

## Deployment to Render

1. Create a new Web Service on Render
2. Connect your repository
3. Set the following values:
   - Name: `email-verifier-api` (or your preferred name)
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app.main:app --preload`
4. Click "Create Web Service"

Render will automatically provide HTTPS for your deployment.

## Troubleshooting

### API Returns 400 Bad Request
- Ensure you're sending a proper JSON body with the `email` field
- Check that your Content-Type header is set to `application/json`

### SMTP Checks Failing
- Some email providers block SMTP verification attempts
- Try increasing the SMTP timeout if checks take too long
- Use only the syntax and MX checks for higher reliability

### SSL/TLS Connection Issues
- If using HTTP locally, ensure clients connect with http:// not https://
- For production, always use HTTPS via Render or by providing SSL certificates

## Notes

- The API performs SMTP checks without sending actual emails
- Some email providers may block SMTP verification attempts
- The list of disposable email domains is not exhaustive and may need to be updated