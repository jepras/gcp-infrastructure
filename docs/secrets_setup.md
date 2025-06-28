# Google Secret Manager Setup Commands

This document contains the `gcloud` commands to add your sensitive information to Google Secret Manager.
**IMPORTANT:** Replace the placeholder values (`YOUR_OUTLOOK_CLIENT_ID`, `YOUR_OUTLOOK_CLIENT_SECRET`, etc.) with your actual credentials.

---

## 1. Database Connection String

You've already created the `DATABASE_URL` secret and added its value. This is for your reference:

```bash
# Create the secret (if not already created)
/Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets create DATABASE_URL --replication-policy="automatic"

# Add the database connection string as a version
echo "postgresql://neondb_owner:npg_x4XoHw0RdLVu@ep-tiny-credit-a2ojl6oz-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require" | /Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets versions add DATABASE_URL --data-file=-
```

---

## 2. Outlook OAuth Credentials

### Outlook Client ID

```bash
# Create the secret (if not already created)
/Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets create OUTLOOK_CLIENT_ID --replication-policy="automatic"

# Add your Outlook Client ID as a version
echo "YOUR_OUTLOOK_CLIENT_ID" | /Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets versions add OUTLOOK_CLIENT_ID --data-file=-
```

### Outlook Client Secret

```bash
# Create the secret (if not already created)
/Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets create OUTLOOK_CLIENT_SECRET --replication-policy="automatic"

# Add your Outlook Client Secret as a version
echo "YOUR_OUTLOOK_CLIENT_SECRET" | /Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets versions add OUTLOOK_CLIENT_SECRET --data-file=-
```

---

## 3. Pipedrive OAuth Credentials

### Pipedrive Client ID

```bash
# Create the secret (if not already created)
/Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets create PIPEDRIVE_CLIENT_ID --replication-policy="automatic"

# Add your Pipedrive Client ID as a version
echo "YOUR_PIPEDRIVE_CLIENT_ID" | /Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets versions add PIPEDRIVE_CLIENT_ID --data-file=-
```

### Pipedrive Client Secret

```bash
# Create the secret (if not already created)
/Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets create PIPEDRIVE_CLIENT_SECRET --replication-policy="automatic"

# Add your Pipedrive Client Secret as a version
echo "YOUR_PIPEDRIVE_CLIENT_SECRET" | /Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets versions add PIPEDRIVE_CLIENT_SECRET --data-file=-
```

---

## 4. Firebase Service Account Credentials

The `project_overview.md` mentions `GOOGLE_APPLICATION_CREDENTIALS`. This is typically a JSON key file for a Firebase service account. You'll need to:

1.  Go to your Firebase project settings -> Service accounts.
2.  Generate a new private key. This will download a JSON file.
3.  The content of this JSON file needs to be stored as a secret.

```bash
# Create the secret (if not already created)
/Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets create GOOGLE_APPLICATION_CREDENTIALS --replication-policy="automatic"

# Add the content of your Firebase service account JSON key file as a version.
# Replace <PATH_TO_YOUR_FIREBASE_SERVICE_ACCOUNT_JSON_FILE> with the actual path.
cat <PATH_TO_YOUR_FIREBASE_SERVICE_ACCOUNT_JSON_FILE> | /Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets versions add GOOGLE_APPLICATION_CREDENTIALS --data-file=-
```

---

## 5. Credential Encryption Key

The `CREDENTIAL_ENCRYPTION_KEY` is used by your backend to encrypt sensitive tokens. You can generate a strong key using `openssl rand -hex 32`.

```bash
# Generate a key (example output: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef)
openssl rand -hex 32

# Create the secret (if not already created)
/Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets create CREDENTIAL_ENCRYPTION_KEY --replication-policy="automatic"

# Add your generated encryption key as a version
echo "YOUR_GENERATED_ENCRYPTION_KEY" | /Users/jepperasmussen/google-cloud-sdk/bin/gcloud secrets versions add CREDENTIAL_ENCRYPTION_KEY --data-file=-
```
