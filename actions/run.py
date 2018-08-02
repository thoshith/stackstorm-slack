import requests
import urllib
import urlparse

from st2common.runners.base_action import Action

BASE_URL = 'https://slack.com/api/'


class SlackAction(Action):

    def run(self, **kwargs):
        if kwargs.get('token', None) is None:
            kwargs['token'] = self.config['action_token']

        return self._do_request(kwargs)

    def _do_request(self, params):
        end_point = params['end_point']
        url = urlparse.urljoin(BASE_URL, end_point)
        del params['end_point']

        http_method = params['http_method']
        del params['http_method']

        headers = {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        for key in params.keys():
            if params[key] is None:
                del params[key]

        data = urllib.urlencode(params)

        if http_method == 'POST':
            response = requests.post(url=url,
                                     headers=headers, data=data)
        elif http_method == 'GET':
            response = requests.get(url=url,
                                    headers=headers, params=data)
        else:
            failure_reason = ('Failed to perform action %s: Invalid HTTP method: %s' % (
                end_point, http_method))
            self.logger.exception(failure_reason)
            raise Exception(failure_reason)

        results = response.json()
        if not results['ok']:
            failure_reason = ('Failed to perform action %s: %s \
                              (status code: %s)' % (end_point, response.text,
                              response.status_code))
            self.logger.exception(failure_reason)
            raise Exception(failure_reason)

        return results
