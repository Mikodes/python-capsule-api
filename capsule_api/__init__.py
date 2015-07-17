from .objects import Opportunity
from .request import Request
from .fetchers.customfields import CustomFieldsFetcher
from .fetchers.opportunity import OpportunityFetcher
from .fetchers.tags import TagsFetcher
from .fetchers.party import PartyFetcher


class CapsuleAPI(object):
    def __init__(self, capsule_name, capsule_key, objects=None):
        self.request = Request(capsule_name, capsule_key)

        if objects is None:
            objects = {}
        objects.setdefault('opportunity', Opportunity)

        if not hasattr(self, 'tags'):
            self.tags = TagsFetcher(self)
        if not hasattr(self, 'customfields'):
            self.customfields = CustomFieldsFetcher(self)
        if not hasattr(self, 'opportunity'):
            self.opportunity = OpportunityFetcher(self, objects['opportunity'])
        if not hasattr(self, 'party'):
            self.party = PartyFetcher(self)
