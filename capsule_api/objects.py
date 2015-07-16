import dateutil.parser
from decimal import Decimal
from collections import OrderedDict


class Opportunity(dict):

    @property
    def createdOn(self):
        return dateutil.parser.parse(self['createdOn'])

    @property
    def expectedCloseDate(self):
        try:
            return dateutil.parser.parse(self['expectedCloseDate'])
        except KeyError:
            raise AttributeError

    @property
    def actualCloseDate(self):
        return dateutil.parser.parse(self['actualCloseDate'])

    @property
    def updatedOn(self):
        return dateutil.parser.parse(self['updatedOn'])

    @property
    def open(self):
        return 'actualCloseDate' not in self

    @property
    def probability(self):
        return int(self['probability'])

    @property
    def milestoneId(self):
        return int(self['milestoneId'])

    @property
    def customfields(self):
        try:
            custom_fields = self.get('raw_customfields') or self['customfields']
            return dict((x['label'], x['text']) for x in custom_fields if 'text' in x)
        except KeyError:
            raise AttributeError

    @property
    def value(self):
        try:
            return Decimal(self['value'])
        except KeyError:
            return Decimal(0)

    @property
    def weighted_value(self):
        return self.value * self.probability / 100

    @property
    def tags(self):
        return list(x['name'] for x in self['tags_id'])

    @property
    def datatags(self):
        return OrderedDict((x['label'], dateutil.parser.parse(x['date']).date()) for x in sorted(self['raw_datatags'], key=lambda x: x['date']))

    @property
    def positive_outcome(self):
        return not self.open and self.probability == 100

    @property
    def negative_outcome(self):
        return not self.open and self.probability == 0

    def load_customfields_from_api(self, customfields):
        self['raw_customfields'] = [x for x in customfields if 'date' not in x]
        self['raw_datatags'] = [x for x in customfields if 'date' in x]

    def load_tags_from_api(self, tags):
        self['tags_id'] = [x for x in tags]

    def __getattr__(self, element):
        if element == 'customfields':
            raise AttributeError
        if element in self:
            return self[element]
        if element in self.customfields:
            return self.customfields[element]
        raise AttributeError
