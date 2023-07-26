from event import security_bulletin_event
from event import upgrade_avaliable_event
from event import upgrade_event

# Triggered from a message on a Cloud Pub/Sub topic
def gke_cluster_notifications(event, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """

     # Print pub/sub event informations
    print(
        """This Function was triggered by messageId {} published at {}
    """.format(
            context.event_id, context.timestamp
        )
    )
    
    # Test print pub/sub event
    print(event)

    # check event type and send message
    type_url = event.get("attributes").get("type_url")

    if "SecurityBulletinEvent" in type_url:
        security_bulletin_event.send_message(event)
        return ("", 204)

    # elif "UpgradeAvailableEvent" in type_url:
    #     upgrade_avaliable_event.send_message(event)
    #     return ("", 204)

    elif "UpgradeEvent" in type_url:
        upgrade_event.send_message(event)
        return ("", 204)

    else:
        msg = f"Event is not exist, so it will be skipped."
        print(msg)
        return (f"Bad Request: {msg}", 400)
