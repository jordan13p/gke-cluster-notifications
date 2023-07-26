import os, json
import telegram
from discord_webhook import DiscordWebhook, DiscordEmbed


def get_message_data(event):
    payload = json.loads(event.get("attributes").get("payload"))

    message_data = {
        'cluster': event.get("attributes").get("cluster_name"),
        'location': event.get("attributes").get("cluster_location"),
        'cluster_resource': payload.get("resourceTypeAffected"),
        'suggested_upgrade_target': payload.get("suggestedUpgradeTarget"),
        'bulletin_id': payload.get("bulletinId"),
        'severity': payload.get("severity"),
        'cve_ids': ", ".join(payload.get("cveIds")),
        'message': payload.get("briefDescription"),
        'url': payload.get("bulletinUri")
    }

    return message_data


def send_message_to_discord(message_data):
    webhook = DiscordWebhook(url = os.environ["DISCORD_WEBHOOK_URL"])

    # create embed object for webhook
    embed = DiscordEmbed(
        title = '\U0001F6A8 GKE issues a security bulletin !!',
        description = 'Click link to view more bulletin details \U00002934 \n'
    )

    # set embed colors by severity
    severity = message_data.get('severity')
    if severity == "High":
        embed.set_color('f80365')
    elif severity == "Medium":
        embed.set_color('e0f803')
    else:
        embed.set_color('4fb0e8')

    # add url and fields to embed
    embed.set_url(url = message_data.get('url'))
    embed.add_embed_field(name = 'Cluster', value = message_data.get('cluster'))
    embed.add_embed_field(name = 'Location', value = message_data.get('location'))
    embed.add_embed_field(name = 'Resource Type', value = message_data.get('cluster_resource'))
    embed.add_embed_field(name = 'Suggested Upgrade Target', value = message_data.get('suggested_upgrade_target'))
    embed.add_embed_field(name = 'Bulletin ID', value = message_data.get('bulletin_id'))
    embed.add_embed_field(name = 'Severity', value = message_data.get('severity'))
    embed.add_embed_field(name = 'Reference', value = message_data.get('cve_ids'), inline=False)
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
