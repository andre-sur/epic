import sentry_sdk

sentry_sdk.init(
    dsn="https://c6e2a5d2ac77065550dd8284a11fda99@o4509518763917312.ingest.de.sentry.io/4509649418453072",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)