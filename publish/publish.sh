#!/bin/bash

# Run the below script to publish the agent into your agentspace.

export APP_ID="Provide your agentspace id"
export LOCATION="your-gcp-location" # e.g., us-central1
export REASONING_ENGINE_ID="your-reasoning-engine-id" # The ID returned after running deploy.py

export PROJECT_ID=$(gcloud config get-value project)
echo "Using Project ID: ${PROJECT_ID}" 

curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: ${PROJECT_ID}" \
-d '{
  "displayName": "Lead Generation Agent",
  "description": "This agent discovers investment patterns and finds new leads.",
  "adk_agent_definition": {
    "tool_settings": {
      "tool_description": "This agent discovers investment patterns and finds new leads."
    },
    "provisioned_reasoning_engine": {
      "reasoning_engine": "projects/'"${PROJECT_ID}"'/locations/'"${LOCATION}"'/reasoningEngines/'"${REASONING_ENGINE_ID}"'"
    }
  }
}' \
"https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents"
