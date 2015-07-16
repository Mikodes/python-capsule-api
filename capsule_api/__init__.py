from .models import Opportunity  # backwards compatibility, otherwise it would be OpportunityModel
from .request import Request
from .api.customfields import CustomFields
from .api.opportunity import Opportunity as OpportunityApi
from .api.tags import Tags


class Api(object):
    # TODO: TEMP! add in a loader method for this
    pass


class CapsuleAPI(object):
    def __init__(self, capsule_name, capsule_key, models=None):
        self.request = Request(capsule_name, capsule_key)

        # TODO: remove these at some point. Directly access self.request.
        self.get = self.request.get
        self.post = self.request.post
        self.put = self.request.put
        self.delete = self.request.delete

        if models is None:
            models = {}
        models.setdefault('opportunity', Opportunity)

        # TODO: TEMP! add in a loader method for these
        self.api = Api()
        self.api.customfields = CustomFields(self)
        self.api.tags = Tags(self)
        self.api.opportunity = OpportunityApi(self, models['opportunity'])
