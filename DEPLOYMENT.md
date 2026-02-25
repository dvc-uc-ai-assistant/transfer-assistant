# Transfer Assistant - GCP Deployment Guide

## Deployment Summary

**Application URL:** https://transfer-assistant-740230515244.us-central1.run.app

**GCP Project:** nexa-transfer-new (740230515244)

## Architecture

- **Cloud Run Service:** transfer-assistant
  - Region: us-central1
  - Container: Built from Dockerfile (Python 3.11-slim + Node 20 Alpine)
  - Port: 8080
  - Workers: 4 gunicorn workers with 2 threads each

- **Cloud SQL:** transfer-assistant-pg
  - PostgreSQL 16
  - Database: transfer_assistant_db
  - User: transfer_user
  - Connection: Via Unix socket proxy

- **Artifact Registry:** us-central1-docker.pkg.dev/nexa-transfer-new/transfer-assistant

- **Secret Manager:**
  - OPENAI_API_KEY (mounted to backend)
  - DATABASE_URL (Cloud SQL socket connection string)

- **Cloud Run Job:** transfer-assistant-seed
  - Purpose: Load JSON data from data/archived/ into assist_data table
  - Command: `python scripts/load_json_to_assist_data.py`

## Manual Deployment Steps

### 1. Build and Deploy via Cloud Build

```powershell
gcloud builds submit --region=us-central1 --substitutions="_INSTANCE_CONNECTION_NAME=nexa-transfer-new:us-central1:transfer-assistant-pg,COMMIT_SHA=v2"
```

This command:
- Builds the Docker container with frontend (React/Vite) and backend (Flask/SQLAlchemy)
- Pushes to Artifact Registry
- Deploys to Cloud Run with Cloud SQL proxy and secrets

### 2. Load Data into Database

After deployment, run the data loader job:

```powershell
gcloud run jobs execute transfer-assistant-seed --region=us-central1
```

This loads transfer agreement data from `data/archived/*.json` into the `assist_data` table.

### 3. Verify Deployment

Test the health endpoint:
```powershell
curl https://transfer-assistant-740230515244.us-central1.run.app/health
```

Test the chatbot:
```powershell
curl -X POST https://transfer-assistant-740230515244.us-central1.run.app/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What CS courses transfer to UC Berkeley?","session_id":"test"}'
```

## Key Configuration Files

- **cloudbuild.yaml:** CI/CD pipeline definition
- **Dockerfile:** Multi-stage build (frontend + backend)
- **scripts/load_json_to_assist_data.py:** Data loader for assist_data table

## Important Notes

### Dockerfile Changes
The Dockerfile was updated to include the `scripts/` directory:

```dockerfile
# Copy scripts for data loading jobs
COPY scripts/ ./scripts/
```

This is required for the Cloud Run Job to execute the data loader script.

### Cloud Run Job Image
When rebuilding the container, you must update the Cloud Run Job to use the new image:

```powershell
gcloud run jobs update transfer-assistant-seed \
  --region=us-central1 \
  --image=us-central1-docker.pkg.dev/nexa-transfer-new/transfer-assistant/app:v2
```

### IAM Permissions
The Cloud Run runtime service account (740230515244-compute@developer.gserviceaccount.com) has:
- roles/cloudsql.client (Cloud SQL connection)
- roles/secretmanager.secretAccessor (Access to secrets)

## Troubleshooting

### Empty assist_data Table
If the app returns "Could not find data for the requested campus(es)", run the data loader job:
```powershell
gcloud run jobs execute transfer-assistant-seed --region=us-central1
```

Check job execution status:
```powershell
gcloud run jobs executions list --job=transfer-assistant-seed --region=us-central1 --limit=1
```

### Database Connection Issues
Verify DATABASE_URL secret:
```powershell
gcloud secrets versions access latest --secret=DATABASE_URL
```

Should be in format:
```
postgresql://transfer_user:hello@/transfer_assistant_db?host=/cloudsql/nexa-transfer-new:us-central1:transfer-assistant-pg
```

### View Logs
Cloud Run service logs:
```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=transfer-assistant" --limit=50
```

Cloud Run job logs:
```powershell
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=transfer-assistant-seed" --limit=50
```

## Future: GitHub Trigger Setup

To enable automatic deployments on Git push:

1. Go to GCP Console → Cloud Build → Triggers
2. Click "Create Trigger"
3. Connect GitHub repository: dvc-uc-ai-assistant/transfer-assistant
4. Set branch: `^Local_Eleni$` (or `^main$` for production)
5. Build configuration: cloudbuild.yaml
6. Add substitution: `_INSTANCE_CONNECTION_NAME=nexa-transfer-new:us-central1:transfer-assistant-pg`

This will automatically build and deploy on every push to the specified branch.

## Testing

The application supports queries for:
- UC Berkeley (UCB)
- UC Davis (UCD)
- UC San Diego (UCSD)

Example queries:
- "What CS courses transfer to UC Berkeley?"
- "What physics courses do I need for UC Davis?"
- "Show me math requirements for UCSD"

## Data Files

Transfer agreement data is stored in:
- `data/archived/ucb_25-26.json` (UC Berkeley 2025-2026)
- `data/archived/ucd_24-25.json` (UC Davis 2024-2025)
- `data/archived/ucsd_24-25.json` (UC San Diego 2024-2025)

These files are loaded into the `assist_data` table by the Cloud Run Job.
