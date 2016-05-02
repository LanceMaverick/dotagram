import telepot
import dataset
from dateutil.parser import parse as dparse

from .groupevent import GroupEvent

class EventBot(telepot.async.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout, db_name="sqlite:///eventbot.db"):
        """Basic bot for handling group events."""
        super(EventBot, self).__init__(seed_tuple, timeout)

        # TODO make configurable through config file.
        # And maybe chat independent
        # Or maybe have a chat independent table, probably neater
        self.db_name = db_name
        self.db_table_name = "default_name" # TODO Change!

    async def on_chat_message(self, msg):
        """Default on chat message behaviour. """
        # This will eventually be replaced by the old bot code.

        print("HELLO WORLD")
        if msg['text'] == "/newevent":
            await self.create_event(msg)
        if msg['text'] == "/currentevents":
            await self.post_current_events(msg)


    async def create_event(self, msg):
        """Create group event. """
        await self.sender.sendMessage(
            "When would you like the event? (Times will be interpreted as today)")

        # TODO add error checking here
        response = await self.listener.wait()
        start_datetime = dparse(response["text"])

        await self.sender.sendMessage(
            "Creating default group event, with you as first attendee.")

        group_event = GroupEvent(
            start_datetime,
            people_attending=[
                {"name": msg["from"]["username"]}])

        print(group_event.export_as_dict())
        # TODO check if there is already an event
        with dataset.connect(self.db_name) as db:
            table = db[self.db_table_name]
            table.insert(group_event.export_as_dict())


    # TODO rewrite this function to be much more human
    async def post_current_events(self, msg):
        """Message the chat with a list of 'current' events from the db. """
        with dataset.connect(self.db_name) as db:
            table = db[self.db_table_name]
            for event in table.all():
                print(event)
                # if event["start_datetime"] > datetime.datetime.now():
                await self.sender.sendMessage(
                    "{}".format(event["start_datetime"]))
        await self.sender.sendMessage("That's all the events for now.")
