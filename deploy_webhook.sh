#!/usr/bin/env bash
set -e

REGION="eu-north-1"
FUNCTION="msci-poland-telegram-webhook"
ROLE="arn:aws:iam::905418356298:role/msci-poland-telegram-webhook-role"

# Set these before running (or export them in your shell):
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-8521910826:AAHbOLnsWFGRBNFWHWbrxJ9Puyg9LcBZc1g}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-7366508056}"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY env var before running}"
REPORT_LAMBDA="msci-poland-inclusion-report"
DEPLOY_ID="v3"

echo "==> Building zip..."
zip -j /tmp/webhook_deploy.zip msci_poland_telegram_webhook.py

ENV_VARS="Variables={TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN,TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID,ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY,REPORT_LAMBDA_NAME=$REPORT_LAMBDA,DEPLOY_ID=$DEPLOY_ID}"

# Check if function exists
if aws lambda get-function --function-name "$FUNCTION" --region "$REGION" > /dev/null 2>&1; then
  echo "==> Updating existing Lambda code..."
  aws lambda update-function-code \
    --function-name "$FUNCTION" \
    --zip-file fileb:///tmp/webhook_deploy.zip \
    --region "$REGION"

  echo "==> Waiting for update to complete..."
  aws lambda wait function-updated --function-name "$FUNCTION" --region "$REGION"

  echo "==> Setting environment variables..."
  aws lambda update-function-configuration \
    --function-name "$FUNCTION" \
    --environment "$ENV_VARS" \
    --timeout 900 \
    --region "$REGION"
else
  echo "==> Creating Lambda function..."
  aws lambda create-function \
    --function-name "$FUNCTION" \
    --runtime python3.12 \
    --role "$ROLE" \
    --handler msci_poland_telegram_webhook.lambda_handler \
    --zip-file fileb:///tmp/webhook_deploy.zip \
    --timeout 900 \
    --memory-size 256 \
    --environment "$ENV_VARS" \
    --region "$REGION"
fi

echo "==> Waiting for function to be active..."
aws lambda wait function-active --function-name "$FUNCTION" --region "$REGION"

echo "==> Setting reserved concurrency to 1 (prevents duplicate polling chains)..."
aws lambda put-function-concurrency \
  --function-name "$FUNCTION" \
  --reserved-concurrent-executions 1 \
  --region "$REGION"

echo "==> Invoking Lambda to start polling..."
aws lambda invoke \
  --function-name "$FUNCTION" \
  --invocation-type Event \
  --payload "{\"deploy_id\":\"$DEPLOY_ID\"}" \
  --region "$REGION" \
  /tmp/invoke_response.json

echo "==> Done. Bot is now polling Telegram."
echo "    Send a message in your Telegram chat to test it."
