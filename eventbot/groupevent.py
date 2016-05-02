import datetime
import yaml

class GroupEvent(object):
    def __init__(self,
                 start_datetime,
                 end_datetime=None,
                 people_attending=None,
                 additional_info=None,
                 *args,
                 **kwargs
    ):
        """Initialises simple group event. *args and **kwargs are ignored.

        NOTE: people_attending is a list of dictionaries, each of which must
        contain at least a "name" field.
        """

        assert type(start_datetime) == datetime.datetime
        self.start_datetime = start_datetime
        if end_datetime is not None:
            self.end_datetime = end_datetime
        else:
            self.end_datetime = self.start_datetime + datetime.timedelta(hours=3)

        if people_attending is not None:
            # If people_attending is a yaml string, un yaml it.
            if type(people_attending) == str:
                people_attending = yaml.load(people_attending)

            for peep in people_attending:
                assert "name" in peep, \
                    "People dicts must contain \"name\" field."
            self.people_attending = people_attending
        else:
            self.people_attending = []

        if additional_info is not None:
            assert type(additional_info) == dict, \
                "additional_info must be of type dict"
            self.additional_info = additional_info
        else:
            self.additional_info = dict()

    def export(self):
        """Export class as a dictionary.

        The return value of this function can be used to initialise another
        GroupEvent using **kwargs e.g.

            new_group_event = GroupEvent(**group_event.export())

        It can also be used to insert into a table from dataset.
        """

        return {
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "people_attending": yaml.dump(self.people_attending),
            "additional_info": self.additional_info if self.additional_info else None
        }

    def add_person(self, name, **kwargs):
        """Adds a person as attending to the event.

        Returns the list of people attending.
        """
        self.people_attending.append(
            "name", name,
            **kwargs
        )

        return self.people_attending

    def how_many_attending(self):
        return len(self.people_attending)
