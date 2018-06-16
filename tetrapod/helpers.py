import math
import time


def iterate_resource(client, url, http_method='POST', limit=30, offset=0, params=None):
    """
    Get a list of items from the Podio API and provide a generator to iterate
    over these items.

    e.g. to read all the items of one app use:

        url = 'https://api.podio.com/item/app/{}/filter/'.format(app_id)
        for item in iterate_resource(client, url, 'POST'):
            print(item)

    """
    if params is None:
        params = dict(limit=limit, offset=offset)
    else:
        params['limit'] = limit
        params['offset'] = offset

    if http_method == 'POST':
        api_resp = client.post(url, data=params)
    elif http_method == 'GET':
        api_resp = client.get(url, params=params)
    else:
        raise Exception("Method not supported.")

    if api_resp.status_code != 200:
        raise Exception('Podio API response was bad: {}'.format(api_resp.content))

    resp = api_resp.json()
    for item in resp['items']:
        yield item

    total = resp['total']
    print('offset: {}, total: {}, '.format(offset, total))
    steps_left = []
    if total > limit:
        num_steps = int(math.ceil(total / limit))
        steps = list(range(0, num_steps * limit, limit))
        # we don't need step 0 because we already got the data.
        steps_left = steps[1:]

    for curr_offset in steps_left:
        print('offset: {}, total: {}, waiting ...'.format(curr_offset, total))
        time.sleep(2.0)
        params['limit'] = limit
        params['offset'] = offset
        if http_method == 'POST':
            api_resp = client.post(url, data=params)
        else: # method == 'GET'
            api_resp = client.get(url, params=params)

        if api_resp.status_code != 200:
            raise Exception('Podio API response was bad: {}'.format(api_resp.content))
        resp = api_resp.json()
        for item_data in resp['items']:
            yield item_data
