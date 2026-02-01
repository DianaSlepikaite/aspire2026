# Azure Services Setup Guide

This guide walks you through setting up the required Azure services for the Client Need Service Agent.

## Prerequisites

- Active Azure subscription with appropriate permissions
- Azure CLI installed ([Download here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- Access to Azure Portal

## Services Required

1. **Azure OpenAI Service** - For conversational AI
2. **Azure Speech Service** - For speech-to-text and text-to-speech

## Setup Steps

### 1. Login to Azure

```bash
az login
```

### 2. Set Your Subscription

```bash
# List available subscriptions
az account list --output table

# Set the subscription you want to use
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### 3. Create Resource Group

```bash
# Create a resource group in your preferred region
az group create \
  --name aspire-hackathon \
  --location eastus
```

## Azure OpenAI Service Setup

### 1. Create Azure OpenAI Resource

```bash
az cognitiveservices account create \
  --name aspire-openai \
  --resource-group aspire-hackathon \
  --kind OpenAI \
  --sku S0 \
  --location eastus \
  --yes
```

**Note:** Azure OpenAI is available in limited regions. Check [regional availability](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#model-summary-table-and-region-availability).

### 2. Deploy GPT-4 Model

The model deployment must be done through the Azure Portal:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource (`aspire-openai`)
3. Go to **"Model deployments"** → **"Manage Deployments"**
4. This will open Azure OpenAI Studio
5. Click **"Create new deployment"**
6. Select:
   - Model: **gpt-4** or **gpt-4-turbo**
   - Deployment name: **gpt-4** (use this name in your .env file)
   - Model version: Latest
7. Click **"Create"**

### 3. Get OpenAI Credentials

```bash
# Get endpoint
az cognitiveservices account show \
  --name aspire-openai \
  --resource-group aspire-hackathon \
  --query properties.endpoint \
  --output tsv

# Get API key
az cognitiveservices account keys list \
  --name aspire-openai \
  --resource-group aspire-hackathon \
  --query key1 \
  --output tsv
```

## Azure Speech Service Setup

### 1. Create Speech Service Resource

```bash
az cognitiveservices account create \
  --name aspire-speech \
  --resource-group aspire-hackathon \
  --kind SpeechServices \
  --sku S0 \
  --location eastus \
  --yes
```

### 2. Get Speech Service Credentials

```bash
# Get region
az cognitiveservices account show \
  --name aspire-speech \
  --resource-group aspire-hackathon \
  --query location \
  --output tsv

# Get API key
az cognitiveservices account keys list \
  --name aspire-speech \
  --resource-group aspire-hackathon \
  --query key1 \
  --output tsv
```

## Configuration

### 1. Update .env File

Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

Then update the following values with your credentials:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://aspire-openai.openai.azure.com/
AZURE_OPENAI_KEY=your_openai_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure Speech
AZURE_SPEECH_KEY=your_speech_api_key_here
AZURE_SPEECH_REGION=eastus
```

### 2. Verify Configuration

Run the application and check the health endpoint:

```bash
# Start the application
cd backend
python -m uvicorn client_need_service.main:app --reload

# In another terminal, check health
curl http://localhost:8000/api/v1/health/detailed
```

You should see all services showing as "healthy" or "configured".

## Cost Management

### Azure OpenAI Pricing

- Pay-per-use model based on tokens
- GPT-4: ~$0.03 per 1K prompt tokens, ~$0.06 per 1K completion tokens
- Set up budgets and alerts in Azure Portal

### Azure Speech Pricing

- Pay-per-use model
- Speech-to-Text: ~$1 per hour of audio
- Text-to-Speech: ~$16 per 1M characters
- First 5 hours of speech-to-text are free each month

### Cost Optimization Tips

1. **Use GPT-4-turbo** instead of GPT-4 for lower costs
2. **Set conversation limits** using the `MAX_CONVERSATION_MESSAGES` setting
3. **Disable speech features** if not needed (set `ENABLE_SPEECH_TO_TEXT=false`)
4. **Monitor usage** through Azure Portal Cost Management
5. **Set up budget alerts** to avoid unexpected charges

## Troubleshooting

### "Access Denied" Error

If you get access denied when creating Azure OpenAI:

- Azure OpenAI requires approval. Apply for access at: https://aka.ms/oai/access
- Processing can take several days

### "Region Not Available" Error

If your region doesn't support Azure OpenAI:

- Try these regions: `eastus`, `southcentralus`, `westeurope`
- Check current availability: https://aka.ms/oai/models

### "Quota Exceeded" Error

If you hit quota limits:

- Check your quota in Azure Portal → Azure OpenAI → Quotas
- Request quota increase through Azure Portal
- Consider using rate limiting in your application

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use Azure Key Vault** for production credentials
3. **Enable Azure Private Link** for enhanced security
4. **Implement rate limiting** to prevent abuse
5. **Monitor usage** regularly through Azure Portal
6. **Rotate API keys** periodically

## Additional Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure Speech Documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/)
- [Azure CLI Reference](https://learn.microsoft.com/en-us/cli/azure/)

## Support

For issues or questions:

- Azure OpenAI: https://learn.microsoft.com/en-us/azure/ai-services/openai/overview
- Azure Speech: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/
- Create an issue in the project repository
