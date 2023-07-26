import os, json
import telegram
from base64 import b64decode
from discord_webhook import DiscordWebhook, DiscordEmbed


def get_message_data(event):
    payload = json.loads(event.get("attributes").get("payload"))

    message_data = {
        'cluster': event.get("attributes").get("cluster_name"),
        'location': event.get("attributes").get("cluster_location"),
        'cluster_resource': payload.get("resourceType"),
        'current_version': payload.get("currentVersion"),
        'target_version': payload.get("targetVersion"),
        'start_time': payload.get("operationStartTime"),
        'message': b64decode(event.get("data")).decode("utf-8"),
    }

    return message_data


def send_message_to_discord(message_data):
    webhook = DiscordWebhook(url = os.environ["DISCORD_WEBHOOK_URL"])

    # create embed object for webhook
    embed = DiscordEmbed(
        title = '\U0001F6A8 GKE cluster is upgrading !!',
        description = 'Please check cluster status when cluster is upgrading.\n',
        color = 'f80365'
    )

    # add url and fields to embed
    embed.add_embed_field(name = 'Cluster', value = message_data.get('cluster'))
    embed.add_embed_field(name = 'Location', value = message_data.get('location'))
    embed.add_embed_field(name = 'Resource Type', value = message_data.get('cluster_resource'))
    embed.add_embed_field(name = 'Current Version', value = message_data.get('current_version'))
    embed.add_embed_field(name = 'Target Version', value = message_data.get('target_version'))
    embed.add_embed_field(name = 'Start Time', value = message_data.get('start_time'), inline=False)
    embed.add_embed_field(name = 'Details', value = message_data.get('message'), inline=False)

    # add embed object to webhook
    webhook.add_embed(embed)

    # execute send message
    webhook.execute()


def send_org_data_to_telegram(message):
    # send message to telegram bot
    bot = telegram.Bot(token = os.environ["TELEGRAM_TOKEN"])
    bot.send_message(chat_id = os.environ["USER_ID"], text = message, parse_mode=telegram.ParseMode.HTML)


def send_message(event):
    try:
        message_data = get_message_data(event)
        send_message_to_discord(message_data)
    
    except Exception as err:
        print(err)
        send_org_data_to_telegram(str(err))
        send_org_data_to_telegram(str(event))
