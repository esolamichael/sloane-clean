# Secret Management

This document outlines how secrets are managed in the Clean Code application.

## Secret Manager

The application uses Google Cloud Secret Manager to store sensitive information such as:

- Service account keys
- Database connection strings
- API keys and tokens

## Setting Up a New Secret

To add a new secret to Secret Manager:

```bash
# Create a new secret
gcloud secrets create SECRET_NAME --replication-policy="automatic"

# Add a version with the secret value
gcloud secrets versions add SECRET_NAME --data-file=/path/to/file.json
# OR
echo -n "secret-value" | gcloud secrets versions add SECRET_NAME --data-stdin
```

## Common Secrets

The application expects these common secrets:

| Secret Name | Description | Format |
|-------------|-------------|--------|
| `app-service-account-key` | App Engine service account key | JSON file |
| `mongodb-connection` | MongoDB connection string | String |
| `twilio-auth-token` | Twilio authentication token | String |

## Accessing Secrets in Code

Secrets can be accessed through the utility functions in `app/utils/secrets.py`:

```python
from app.utils.secrets import get_secret_version, get_project_id

# Get the project ID
project_id = get_project_id()

# Get a secret
secret_value = get_secret_version(project_id, "secret-name")
```

## Local Development

For local development, create a `.env` file with necessary environment variables. The application will use these values instead of Secret Manager when running locally.

Example `.env` file:
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_NAME=sloane_ai_service
TWILIO_AUTH_TOKEN=your_test_auth_token
```

## Managing Secret Access

Grant access to secrets using IAM roles:

```bash
# Grant a service account access to a secret
gcloud secrets add-iam-policy-binding SECRET_NAME \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"
```

## Rotating Secrets

Secrets should be rotated regularly for security:

1. Create a new version of the secret
2. Verify the application works with the new secret
3. Disable or destroy old versions

```bash
# Add a new version
gcloud secrets versions add SECRET_NAME --data-file=/path/to/new_file.json

# Disable an old version
gcloud secrets versions disable VERSION_ID --secret=SECRET_NAME

# Destroy an old version (permanent deletion)
gcloud secrets versions destroy VERSION_ID --secret=SECRET_NAME
```

## Security Best Practices

- Never commit secrets to version control
- Use the principle of least privilege when granting access
- Rotate secrets regularly
- Monitor access to secrets with Cloud Audit Logs
- Use Secret Manager for all sensitive information