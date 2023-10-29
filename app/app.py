import json
import os
import re
import logging

import boto3
import gradio as gr
import xml.etree.ElementTree as ET
import html

from collections import defaultdict

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

bedrock_runtime = boto3.client("bedrock-runtime", region_name="eu-central-1")

PASSWORD = os.environ.get("PASSWORD")


def action_item_to_dict(action_item):
    result = {}
    for child in action_item:
        result[child.tag] = child.text
    return result


def extract_and_convert(xml_text):
    match = re.search(r"<actions>(.*?)</actions>", xml_text, re.DOTALL)
    if not match:
        return "No <actions> tag found in the text."

    actions_xml = match.group(1)

    try:
        root = ET.fromstring(f"<actions>{actions_xml}</actions>")
    except ET.ParseError as e:
        return f"Error parsing XML: {str(e)}"

    actions_list = [action_item_to_dict(action_item) for action_item in root.findall(".//action-item")]
    return actions_list


def to_html_grouped_by_person(actions):
    logger.debug(actions)
    grouped_actions = defaultdict(list)

    for action_item in actions:
        person = action_item.get("person", "no person assigned")
        grouped_actions[person].append(action_item["action"])

    html_string = ""
    for person, actions in grouped_actions.items():
        html_string += "<h3>"
        html_string += f"{html.escape(person)}"
        html_string += "</h3>"
        for action in actions:
            html_string += "</ul>"
            html_string += f"<li>{html.escape(action)}</li>"
            html_string += "</ul>"

    return html_string


def follow_up_actions(text):
    prompt = """
Human:
<email>
{query}
</email>

Identify the receiver ann the sender of the email. The sender is probably referred to a 'I' in the email.
Identify all otehr persons mentioned in the email. And keep track of them.

Identify if there are actions defined the the above email and if there is a person assigned to that action.
for each action point, write down the action and the person assigned to it. Keep into account references to the potential action points.
If there is no person assigned to it, write down "No person assigned" (but make sure it is not implicit with a reference).

This is the only thing you need to do. You don't need to write down the context of the action point, only the action and the person assigned to it.
Do not do anything else than writing down the action and the person assigned to it. There are no other tasks to do.
Only respond in English.

Format the results in XLM format. The format is the following:

<actions>
    <action-item>
        <action>Action 1</action>
        <person>No person assigned</person>
    </action-item>
</actions>

What are the actions and the person assigned to it? Only response with the actions and the person assigned to it as like the XML example. Do not write anything else.

Assistant:
"""

    input_body = '{"prompt":"Human: \\n\\nHuman: What is the color of the sky?\\n\\nAssistant:","max_tokens_to_sample":300,"temperature":1,"top_k":250,"top_p":0.999,"stop_sequences":["\\n\\nHuman:"],"anthropic_version":"bedrock-2023-05-31"}'
    json_input = json.loads(input_body)

    json_input["prompt"] = prompt.replace("{query}", text)

    input_body = json.dumps(json_input)

    output = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-instant-v1",
        contentType="application/json",
        accept="*/*",
        body=input_body,
    )

    body = json.loads(output["body"].read().decode())
    completion = "<actions></actions>"

    try:
        completion = body["completion"]
        logger.debug(completion)
    except Exception as e:
        logger.error(e)

    actions_dict = extract_and_convert(completion)
    return to_html_grouped_by_person(actions_dict)


input_text = gr.Textbox(lines=10, label="Context", placeholder="Enter your text here...")

output_html = gr.HTML(label="Action points")

app = gr.Interface(
    fn=follow_up_actions,
    inputs=[input_text],
    outputs=[output_html],
    title="Action points",
    allow_flagging=False,
    description="This app creates action points from email conversations. (This is an example app, not a real product, a real implementation would require more checks, tests, guardrails, etc...))",
    examples=[
        """
hi Jack,

Great meeting today! I'll send you the final offer by the end of the week. Please can you send the names of the people that will be involved in the pilot? Maybe Jacky can help with that? Our services team can set everything up to start early next week.

Thank you 
Best regards,

Jimmy
""",
        """
Dear mr. Smith,

We're looking forward to welcome you next at our conference. In order to make sure everything is ready for you, please send us the following information:
- Your flight number (we'll send a driver to pick you up)
- Are you planning to use a Mac or PC? (Mike will prepare the laptop for you)
- Will you bring a plus one for the conference dinner?

I'll make sure the hotel is booked for you.

Thank you 
Best regards,

Stacy
""",
    ],
)

apps = []

apps.append(app)

demo = gr.TabbedInterface(apps, ["Actions"])

demo.launch(
    server_port=8080,
    auth=("user", PASSWORD),
    server_name="0.0.0.0",
    share=False,
    auth_message="Enter your username and password to access the app!",
)
