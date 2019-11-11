import os
import math
import time
import datetime
import logging


log = logging.getLogger(__name__)


def iterate_array(client, url, http_method='GET', limit=100, offset=0, params=None):
    """
    Get a list of objects from the Podio API and provide a generator to iterate
    over these items. Use this for 

    e.g. to read all the items of one app use:

        url = 'https://api.podio.com/comment/item/{}/'.format(item_id)
        for item in iterate_array(client, url, 'GET'):
            print(item)
    """
    all_elements = []
    if params is None:
        params = dict(limit=limit, offset=offset)
    else:
        params['limit'] = limit
        params['offset'] = offset
        
    do_requests = True
    while do_requests == True:
        if http_method == 'POST':
            api_resp = client.post(url, data=params)
        elif http_method == 'GET':
            api_resp = client.get(url, params=params)
        else:
            raise Exception("Method not supported.")
        
        if api_resp.status_code != 200:
            raise Exception('Podio API response was bad: {}'.format(api_resp.content))
            
        resp = api_resp.json()
        num_entries = len(resp)
        if num_entries < limit or num_entries <= 0:
            do_requests = False

        params['offset'] += limit
        
        all_elements.extend(resp) 
    # print(f"array of {len(all_elements)}")
    return all_elements
    
    

def iterate_resource(client, url, http_method='POST', limit=500, offset=0, params=None):
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
        api_resp = client.post(url, json=params)
    elif http_method == 'GET':
        api_resp = client.get(url, params=params)
    else:
        raise Exception("Method not supported.")

    if api_resp.status_code != 200:
        raise Exception('Podio API response was bad: {}'.format(api_resp.content))

    all_items = []
    resp = api_resp.json()
    log.debug(f"Got {len(resp['items'])} ...")
    all_items.extend(resp['items'])

    total = resp['total']
    log.debug('Getting items from offset: %d, total: %d' % (offset, total))
    steps_left = []
    if total > limit:
        num_steps = int(math.ceil(total / limit))
        steps = list(range(0, num_steps * limit, limit))
        # we don't need step 0 because we already got the data.
        steps_left = steps[1:]

    for curr_offset in steps_left:
        log.debug('Getting items from offset: %d, total: %d' % (curr_offset, total))
        params['limit'] = limit
        params['offset'] = curr_offset
        if http_method == 'POST':
            api_resp = client.post(url, json=params)
        else: # method == 'GET'
            api_resp = client.get(url, params=params)

        if api_resp.status_code != 200:
            raise Exception('Podio API response was bad: {}'.format(api_resp.content))
        resp = api_resp.json()
        all_items.extend( resp['items'] )

    log.debug("Got all items!")
    return all_items
