class TagsFetcher(object):
    def __init__(self, capsule_api):
        self._capsule_api = capsule_api

    def get_list(self, area, area_id, **kwargs):
        result = self._capsule_api.request.get('%s/%d/tag' % (area, int(area_id)), **kwargs)
        return result['tags'].get('tag', [])
