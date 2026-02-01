#!/bin/bash

# Client Need Agent - Test Script
# This script allows you to test the agent with custom client briefs

set -e

API_BASE="http://localhost:8000/api/v1"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       CLIENT NEED AGENT - TEST SCRIPT                      ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if arguments provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <client_name> <client_email> \"<client_brief_text>\""
    echo ""
    echo "Example:"
    echo "  $0 \"John Doe\" \"john@example.com\" \"I need a mobile app...\""
    exit 1
fi

CLIENT_NAME="$1"
CLIENT_EMAIL="$2"
CLIENT_BRIEF="$3"

echo -e "${YELLOW}Step 1: Ingesting client brief...${NC}"
echo "Client: $CLIENT_NAME <$CLIENT_EMAIL>"
echo ""

# Ingest the text
INTAKE_ID=$(curl -s -X POST "$API_BASE/intake/upload/text" \
  -F "text_content=$CLIENT_BRIEF" \
  -F "client_name=$CLIENT_NAME" \
  -F "client_email=$CLIENT_EMAIL" \
  -F "source_label=Test Script" | jq -r '.id')

if [ -z "$INTAKE_ID" ] || [ "$INTAKE_ID" == "null" ]; then
    echo "Error: Failed to ingest client brief"
    exit 1
fi

echo -e "${GREEN}✓ Ingested successfully${NC}"
echo "  Intake ID: $INTAKE_ID"
echo ""

echo -e "${YELLOW}Step 2: Processing through Client Need Agent...${NC}"
echo ""

# Process through agent
RESULT=$(curl -s -X POST "$API_BASE/agent/process-intake" \
  -H "Content-Type: application/json" \
  -d "{\"intake_id\": \"$INTAKE_ID\"}")

# Extract client need ID
CLIENT_NEED_ID=$(echo "$RESULT" | jq -r '.intermediate_steps[] | select(.step == "save_client_need") | .details.client_need_id')

echo -e "${GREEN}✓ Processing complete${NC}"
echo "  Client Need ID: $CLIENT_NEED_ID"
echo ""

# Display results
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}AI SUMMARY:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "$RESULT" | jq -r '.output'
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}EXTRACTION PROCESS:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "$RESULT" | jq -r '.intermediate_steps[] | "✓ \(.action)\n  Completeness: \(.details.completeness_score // "N/A")%\n  Fields: \(.details.fields_extracted // "N/A")\n"'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STRUCTURED CLIENT NEED:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Fetch and display structured data
curl -s "$API_BASE/client-needs/$CLIENT_NEED_ID" | jq '
{
  "Client": {
    "name": .client_name,
    "email": .client_email,
    "company": .client_company
  },
  "Project": {
    "title": .project_title,
    "type": .project_type,
    "industry": .industry,
    "description": (.project_description // "N/A")[:200]
  },
  "Skills": {
    "required": .required_skills,
    "preferred": .preferred_skills,
    "level": .skill_level
  },
  "Budget": {
    "min": .budget_min,
    "max": .budget_max,
    "currency": .budget_currency,
    "type": .budget_type
  },
  "Timeline": {
    "weeks": .timeline_duration_weeks,
    "start_date": .timeline_start_date,
    "urgency": .urgency_level,
    "flexibility": .timeline_flexibility
  },
  "Work": {
    "location": .work_location,
    "team_size": .team_size_needed
  },
  "Completeness": "\(.profile_completeness_score)%"
}'

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}TEST COMPLETE!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
