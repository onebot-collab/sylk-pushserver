from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class PushTokens(Model):
    __table_name__   = 'push_tokens'
    username         = columns.Text(partition_key=True)
    domain           = columns.Text(partition_key=True)
    device_id        = columns.Text(primary_key=True)
    app_id           = columns.Text(primary_key=True)
    background_token = columns.Text(required=False)
    device_token     = columns.Text()
    platform         = columns.Text()
    silent           = columns.Text()
    user_agent       = columns.Text(required=False)


class OpenSips(Model):
    """Useful for servers that need to take routing
    decisions based on the fact that the user has push
    tokens, without having to send push notifications
    """

    __table_name__ = 'mobile_devices'
    opensipskey = columns.Text(primary_key=True)
    opensipsval = columns.Text()
