#!/usr/bin/env bash
# ==============================================================================
# CareerForge AI — Google Cloud Run Deployment Script
# ==============================================================================
set -e

PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="careerforge-agent-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
CORS_ALLOWED=${BACKEND_CORS_ORIGINS:-"*"}
PROVIDER=${LLM_PROVIDER:-"gemini"}

echo "================================================================="
echo " Deploying CareerForge AI (FastAPI + Agent) to Google Cloud Run "
echo " Project: ${PROJECT_ID} | Region: ${REGION} "
echo "================================================================="

if [ -z "$PROJECT_ID" ]; then
  echo "ERROR: GCP_PROJECT_ID is not set and could not be detected from gcloud."
  echo "Please run: gcloud config set project YOUR_PROJECT_ID"
  exit 1
fi

echo "1. Building container image with Google Cloud Build..."
gcloud builds submit --tag "${IMAGE_NAME}" -f backend/Dockerfile .

echo "2. Deploying service to Google Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "LLM_PROVIDER=${PROVIDER},GEMINI_API_KEY=${GEMINI_API_KEY},BACKEND_CORS_ORIGINS=${CORS_ALLOWED}" \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --format 'value(status.url)')

echo "================================================================="
echo " CareerForge AI Backend successfully deployed to Google Cloud Run! "
echo " Service Endpoint: ${SERVICE_URL} "
echo " Health Check:     ${SERVICE_URL}/health "
echo " OpenAPI Docs:     ${SERVICE_URL}/docs "
echo "================================================================="
echo ""
echo "Next Step for Frontend (Vercel):"
echo "Set VITE_API_URL in your Vercel Project Settings:"
echo "VITE_API_URL=${SERVICE_URL}/api/v1"
echo "================================================================="
