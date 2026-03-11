# GCP Deployment Guide (Cloud Run + Cloud SQL)

This guide deploys Transfer Assistant with:
- Cloud Run (app runtime)
- Artifact Registry (container images)
- Cloud SQL for PostgreSQL (database)
- Secret Manager (`OPENAI_API_KEY`, `DATABASE_URL`)

## 1) Set project variables

```powershell
$PROJECT_ID = "your-gcp-project-id"
$REGION = "us-central1"
$SERVICE_NAME = "transfer-assistant"
$REPOSITORY = "transfer-assistant"
$DB_INSTANCE = "transfer-assistant-pg"
$DB_NAME = "transfer_assistant_db"
$DB_USER = "transfer_user"
$DB_PASSWORD = "replace-with-strong-password"

gcloud auth login
gcloud config set project $PROJECT_ID
```

## 2) Enable APIs

```powershell
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## 3) Create Artifact Registry repo

```powershell
gcloud artifacts repositories create $REPOSITORY `
  --repository-format=docker `
  --location=$REGION `
  --description="Transfer Assistant images"
```

If it already exists, continue.

## 4) Create Cloud SQL instance + database + user

```powershell
gcloud sql instances create $DB_INSTANCE `
  --database-version=POSTGRES_16 `
  --region=$REGION `
  --cpu=1 `
  --memory=3840MiB

gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE
gcloud sql users create $DB_USER --instance=$DB_INSTANCE --password=$DB_PASSWORD
```

Build connection values:

```powershell
$INSTANCE_CONNECTION_NAME = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"
$DATABASE_URL = "postgresql://$DB_USER:$DB_PASSWORD@/$DB_NAME?host=/cloudsql/$INSTANCE_CONNECTION_NAME"
```

## 5) Create / update secrets

```powershell
$OPENAI_API_KEY = "sk-..."

$OPENAI_API_KEY | gcloud secrets create OPENAI_API_KEY --data-file=-
$DATABASE_URL | gcloud secrets create DATABASE_URL --data-file=-
```

If already created:

```powershell
$OPENAI_API_KEY | gcloud secrets versions add OPENAI_API_KEY --data-file=-
$DATABASE_URL | gcloud secrets versions add DATABASE_URL --data-file=-
```

Grant Cloud Run runtime secret access:

```powershell
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
$RUNTIME_SA = "$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding OPENAI_API_KEY `
  --member="serviceAccount:$RUNTIME_SA" `
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding DATABASE_URL `
  --member="serviceAccount:$RUNTIME_SA" `
  --role="roles/secretmanager.secretAccessor"
```

## 6) Deploy with cloudbuild.yaml

From repo root:

```powershell
gcloud builds submit --config cloudbuild.yaml `
  --substitutions=_REGION=$REGION,_REPOSITORY=$REPOSITORY,_IMAGE_NAME=app,_SERVICE_NAME=$SERVICE_NAME,_INSTANCE_CONNECTION_NAME=$INSTANCE_CONNECTION_NAME
```

## 7) Initialize DB schema and seed data

Run these once using the same `DATABASE_URL` for Cloud SQL:

```powershell
python init_db.py
python migrate_json_to_db.py
```

## 8) Verify

```powershell
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
Invoke-WebRequest "$SERVICE_URL/health"
```

Expected response is `OK`.
