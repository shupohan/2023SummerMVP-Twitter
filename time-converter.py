import datetime


class time_converter:
    def __init__(self):
        pass

    def convert(self, pg_datetime):
        # Convert to a specific timezone, for example, UTC
        utc_datetime = pg_datetime.astimezone(datetime.timezone.utc)

        # Preserve the same time and date but without a specific timezone
        regular_datetime = utc_datetime.replace(tzinfo=None)

        # Format the datetime as a string in a readable format
        formatted_datetime = regular_datetime.strftime("%Y-%m-%d %H:%M:%S")

        return formatted_datetime
