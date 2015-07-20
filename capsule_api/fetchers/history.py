class HistoryFetcher(object):
    def __init__(self, capsule_api):
        self._capsule_api = capsule_api

    def get(self, history_id):
        return self._capsule_api.request.get('history/%d' % int(history_id))['historyItem']

    def get_list(self, area, area_id):
        resp = self._capsule_api.request.get('%s/%d/history' % (area, int(area_id)))
        history = resp['history'].get('historyItem')
        if not history:
            return []
        if isinstance(history, dict):
            history = [history]
        return history

    def post(self, area, area_id, **kwargs):
        data = {'historyItem': kwargs}
        resp = self._capsule_api.request.post('%s/%d/history' % (area, int(area_id)), data)
        return resp.headers.get('location', '').split('/')[-1]

    def put(self, history_id, **kwargs):
        data = {'historyItem': kwargs}
        self._capsule_api.request.put('history/%d' % int(history_id), data)

    def delete(self, history_id):
        self._capsule_api.request.delete('history/%d' % int(history_id))
