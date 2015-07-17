class HistoryFetcher(object):
    def __init__(self, capsule_api):
        self._capsule_api = capsule_api

    def get(self, history_id):
        return self._capsule_api.request.get('history/%d' % int(history_id))

    def get_list(self, area, area_id):
        return self._capsule_api.request.get('%s/%d/history' % (area, int(area_id)))

    def post(self, area, area_id):
        return self._capsule_api.request.post('%s/%d/history' % (area, int(area_id)))

    def put(self, history_id):
        return self._capsule_api.request.put('history/%d' % int(history_id))

    def delete(self, history_id):
        return self._capsule_api.request.delete('history/%d' % int(history_id))
