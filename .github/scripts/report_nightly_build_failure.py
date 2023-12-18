"""
Called by GH Actions when the nightly build fails.

This reports an error to the #nightly-build-failures Slack channel.
"""
import os

import requests

if "SLACK_WEBHOOK_URL" in os.environ:
    print("Reporting to #nightly-build-failures slack channel")
    response = requests.post(
        os.environ["SLACK_WEBHOOK_URL"],
        json={
            "text": "A Nightly build failed. See https://github.com/wagtail/wagtail-ai/actions/runs/"
            + os.environ["GITHUB_RUN_ID"],
        },
    )

    print("Slack responded with:", response)

else:
    print(
        "Unable to report to #nightly-build-failures slack channel because SLACK_WEBHOOK_URL is not set"
    )
