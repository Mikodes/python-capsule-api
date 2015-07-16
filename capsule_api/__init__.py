from .objects import Opportunity
from .request import Request
from .fetchers.customfields import CustomFieldsFetcher
from .fetchers.opportunity import OpportunityFetcher
from .fetchers.tags import TagsFetcher


class CapsuleAPI(object):
    def __init__(self, capsule_name, capsule_key, objects=None):
        self.request = Request(capsule_name, capsule_key)

        if objects is None:
            objects = {}
        objects.setdefault('opportunity', Opportunity)

        self.tags = TagsFetcher(self)
        self.customfields = CustomFieldsFetcher(self)
        self.opportunity = OpportunityFetcher(self, objects['opportunity'])
