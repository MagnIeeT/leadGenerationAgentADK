# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/bin/bash

# Run the below script to publish the agent into your agentspace.

# Get the directory where the script is located
SCRIPT_DIR=$(dirname "$0")

# Source the environment variables from the .env file located in the parent directory of the script
if [ -f "${SCRIPT_DIR}/../.env" ]; then
  export $(grep -v '^#' "${SCRIPT_DIR}/../.env" | xargs)
fi

export APP_ID="${AGENT_SPACE_ID}"
export LOCATION="${GOOGLE_CLOUD_LOCATION}"
export REASONING_ENGINE_ID="${REASONING_ENGINE_ID}"

export PROJECT_ID=$(gcloud config get-value project)
echo "Using Project ID: ${PROJECT_ID}" 

curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: ${PROJECT_ID}" \
-d "{
  \"displayName\": \"Lead Generation Agent\",
  \"description\": \"This agent discovers investment patterns and finds new leads.\",
  \"adk_agent_definition\": {
    \"tool_settings\": {
      \"tool_description\": \"This agent discovers investment patterns and finds new leads.\"
    },
    \"provisioned_reasoning_engine\": {
      \"reasoning_engine\": \"projects/${PROJECT_ID}/locations/${LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}\"
    }
  }
}" \
"https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents"
