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

"""Test deployment of Lead Generation Agent to Agent Engine."""

import os
import sys
import uuid
import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


FLAGS = flags.FLAGS

flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string(
    "resource_id",
    None,
    "ReasoningEngine resource ID. If not provided, it will be read from the REASONING_ENGINE_ID environment variable.",
)


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument

    load_dotenv()

    resource_id = (
        FLAGS.resource_id
        if FLAGS.resource_id
        else os.getenv("REASONING_ENGINE_ID")
    )
    if not resource_id:
        print(
            "Missing required environment variable: REASONING_ENGINE_ID. "
            "You can also pass it as a command-line flag --resource_id."
        )
        return

    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    bucket = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    )

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print(
            "Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET"
        )
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    user_id = f"user_{uuid.uuid4()}"
    agent = agent_engines.get(resource_id)
    print(f"Found agent with resource ID: {resource_id}")
    session = agent.create_session(user_id=user_id)
    print(f"Created session for user ID: {user_id}")
    
    
    print("Type 'quit' to exit.")



    while True:
        user_input = input("Input: ")
        if user_input == "quit":
            break

        for event in agent.stream_query(
            user_id=user_id,
            session_id=session["id"], 
            message=user_input
        ):
            if "content" in event:
                if "parts" in event["content"]:
                    parts = event["content"]["parts"]
                    for part in parts:
                        if "text" in part:
                            text_part = part["text"]
                            print(f"Response: {text_part}")




    agent.delete_session(user_id=user_id, session_id=session["id"])
    print(f"Deleted session for user ID: {user_id}")


if __name__ == "__main__":
    app.run(main)
