import asyncio
import aiohttp
from aiohttp import ClientConnectorError
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_dot_notation.dot_template import DotTemplate

from tracardi_discord_webhook.model.configuration import DiscordWebHookConfiguration


def validate(config: dict) -> DiscordWebHookConfiguration:
    return DiscordWebHookConfiguration(**config)


class DiscordWebHookAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()

        try:

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:

                params = {
                    "json": {
                        "content": template.render(self.config.message, dot),
                        "username": self.config.username if self.config.username and len(
                            self.config.username) > 0 else None
                    }
                }

                async with session.request(
                        method="POST",
                        url=str(self.config.url),
                        **params
                ) as response:
                    # todo add headers and cookies
                    result = {
                        "status": response.status
                    }

                    if response.status in [200, 201, 202, 203, 204]:
                        return Result(port="response", value=payload), Result(port="error", value=None)
                    else:
                        return Result(port="response", value=None), Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="response", value=None), Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="response", value=None), Result(port="error", value="Discord webhook timed out.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi_discord_webhook.plugin',
            className='DiscordWebHookAction',
            inputs=['payload'],
            outputs=["response", "error"],
            init={
                "url": None,
                "timeout": 10,
                "message": "",
                "username": None
            },
            form=Form(groups=[
                FormGroup(
                    name="Discord server settings",
                    description="This action will require a webhook URL. See documentation how to obtain it.",
                    fields=[
                        FormField(
                            id="url",
                            name="Discord webhook URL",
                            description="Paste here a webhook for a given channel.",
                            component=FormComponent(type="text", props={
                                "label": "Webhook URL"
                            })
                        ),
                        FormField(
                            id="timeout",
                            name="Webhook timeout",
                            component=FormComponent(type="text", props={
                                "label": "Webhook time-out"
                            })
                        ),
                    ]
                ),
                FormGroup(
                    name="Discord message settings",
                    fields=[
                        FormField(
                            id="message",
                            name="Message",
                            description="Type message template. Data placeholders can be used to obtain data from "
                                        "profile, event etc.",
                            component=FormComponent(type="textarea", props={"label": "Message template", "rows": 6})
                        ),
                        FormField(
                            id="username",
                            name="Sender username",
                            description="Type sender username. This field is optional.",
                            component=FormComponent(type="text", props={"label": "Sender"})
                        )
                    ]
                )
            ]
            ),
            version="0.6.0.1",
            author="Risto Kowaczewski",
            license="MIT",
            manual="discord_webhook_action"
        ),
        metadata=MetaData(
            name='Discord webhook',
            desc='Sends message to discord webhook.',
            type='flowNode',
            width=200,
            height=100,
            icon='discord',
            group=["Connectors"]
        )
    )
