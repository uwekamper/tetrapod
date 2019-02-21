import math
import time
import datetime
import logging
from collections.abc import Mapping
from decimal import Decimal

log = logging.getLogger(__name__)

# embed:
#   embed: The id of an embed returned from the Add an embed operation.
#   file: The id of one the thumbnail files returned from the same operation.
def fetch_embed_field(field, field_param=None):
    if field_param is None:
        for value in field.get('values', []):
            return value['embed']['url']
    elif field_param == 'all':
        return [v['embed']['url'] for v in field.get('values', [])]
    return None


# duration:
#   value: The duration in seconds

# video:
#   value: The file id of the video file

# location:
#   value: The location as entered by the user
#   formatted: The resolved formatted full address
#   street_number: The number in the street
#   street_name: The name of the street
#   postal_code: The zip code for the city
#   city: The name of the city
#   state: The state of the city, if any
#   country: The country of the city
#   lat: The latitude of the location
#   lng: The longitude of the location

# progress:
#   value: The current progress as an integer from 0 to 100

# money:
#   value: The decimal amount of the value as a string.
#   currency: The currency of the value.

# contact:
#   value: The profile id of the contact
# Example
# {
#   "user_id": 1234567,
#   "space_id": null,
#   "rights": [
#     "view"
#   ],
#   "url": [
#     "http://example.com"
#   ],
#   "type": "user",
#   "image": {
#     "hosted_by": "podio",
#     "hosted_by_humanized_name": "Podio",
#     "thumbnail_link": "https://d2cmuesa4snpwn.cloudfront.net/public/123456789",
#     "link": "https://d2cmuesa4snpwn.cloudfront.net/public/123456789",
#     "file_id": 123456789,
#     "external_file_id": null,
#     "link_target": "_blank"
#   },
#   "profile_id": 123456789,
#   "org_id": null,
#   "phone": [
#     "+xxxxxxxxxx"
#   ],
#   "link": "https://podio.com/users/1234567",
#   "avatar": 123456789,
#   "mail": [
#     "john@example.com"
#   ],
#   "external_id": null,
#   "last_seen_on": "2018-11-11 11:11:00",
#   "name": "John Doe"
# }
def fetch_contact_field(field, field_param=None):
    if field_param is None:
        for value in field.get('values', []):
            return value['value']
    elif field_param == 'all':
        return [v['value'] for v in field.get('values', [])]
    return None

# member:
#   value: The user id of the member


# app:
#   value: The id of the app item
def fetch_app_field(field, field_param=None):
    if field_param is None:
        for value in field.get('values', []):
            return value['value']
    elif field_param == 'all':
        return [v['value'] for v in field.get('values', [])]
    return None

# date:
#   start_date: The start date
#   start_time: The start time
#   end_date: The end date
#   end_time: The end time
def fetch_date_field(field, field_param=None):
    if field_param is None:
        for value in field.get('values', []):
            return value['start']
    if field_param == 'datetime':
        for value in field.get('values', []):
            date_str = value['start']
            return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    return None

# image:
#   value: The file id of the image file

# number:
#   value: The decimal value of the field as a string.
def fetch_number_field(field, field_param=None):
    if field_param is None:
        for value in field.get('values', []):
            return Decimal(value['value'])
    if field_param == 'int':
        for value in field.get('values', []):
            return int(Decimal(value['value']).to_integral())
    if field_param == 'float':
        for value in field.get('values', []):
            return float(Decimal(value['value']))
    return None


# text:
#   value: The value of the field which can be any length.
#   format: The format of the text, either plain, markdown or html
def fetch_text_field(field, field_param=None):
    if field_param is None:
        for value in field.get('values', []):
            return value['value']
    return None

# category:
#   value: The id of the option
def fetch_category_field(field, field_param=None):
    if field_param == 'active':
        val = field.get('values', [None])[0]
        if val is not None:
            return val['value']
        else:
            return None
    elif field_param == 'all':
        values = []
        for v in field.get('values', []):
            values.append(v.get('value'))
        return values
    elif field_param == 'labels':
        values = []
        for v in field.get('values', []):
            podval = v.get('value')
            if podval is not None:
                values.append(podval['text'])
        return values
    elif field_param is None:
        val = field.get('values', [None])[0]
        if val is not None:
            return val['value']['text']
        else:
            return None
# email:
#   value: Text value (max 254 characters)
#   type: "home"/"work"/ "other"
def fetch_email_field(field, field_param=None):
    """
    email: only the first value is returned
    email__all: [{"type": "work", "value": "xyz@example.com"}]
    email__work/home/other: The first value of the particular type is returned.
    """
    if field_param == 'all':
        vals = field.get('values', [])
        return vals
    elif field_param in ['work', 'home', 'other']:
        vals = field.get('values', None)
        if vals is None:
            return None
        for val in vals:
            if val.get('type') == field_param:
                return val.get('value')
    elif field_param is None:
        val = field.get('values', [None])[0]
        if val is not None:
            return val.get('value')
        else:
            return None

# phone:
#   type: "mobile"/"work"/"home"/"main"/"work_fax"/"private_fax"/ "other"
#   value: string value  (max 50 characters)

# calculation:
def fetch_calculation_field(field, field_param=None):
    # Dates are special
    if field['config']['settings'].get('return_type') == 'date':
        for value in field.get('values', []):
            dt = datetime.datetime.strptime(value['start'], '%Y-%m-%d %H:%M:%S')
            if field_param == 'datetime':
                return dt
            else:
                return '{}'.format(dt)
    for value in field.get('values', []):
        return value['value']

    print(field.get('values'))


def fetch_field(field_descriptor, item_json):
    """
    Fetch the first value of a field - or None if the field is empty.
    :param field_descriptor: The Podio external_id name as shown in the developer view.
    :param item_json: The JSON representation of the Podio item.
    :return: First value or None
    """
    descriptor_parts = field_descriptor.split('__', 1)
    if len(descriptor_parts) == 2:
        external_id = descriptor_parts[0]
        field_param = descriptor_parts[1]
    else:
        external_id = descriptor_parts[0]
        field_param = None
    fields = item_json.get('fields', [])
    if '_' in external_id:
        external_id = external_id.replace('_', '-')
    for field in fields:
        if field['external_id'] == external_id:
            field_type = field['type']
            if field_type == 'text':
                return fetch_text_field(field, field_param)
            elif field_type == 'category':
                return fetch_category_field(field, field_param)
            elif field_type == 'app':
                return fetch_app_field(field, field_param)
            elif field_type == 'calculation':
                return fetch_calculation_field(field, field_param)
            elif field_type == 'date':
                return fetch_date_field(field, field_param)
            elif field_type == 'embed':
                return fetch_embed_field(field, field_param)
            elif field_type == 'email':
                return fetch_email_field(field, field_param)
            elif field_type == 'contact':
                return fetch_contact_field(field, field_param)
            elif field_type == 'number':
                return fetch_number_field(field, field_param)
            else:
                raise NotImplementedError('Field type %s not supported' % field_type)
    return None


class BaseItem(Mapping):
    def __getitem__(self, key):
        return fetch_field(key, self.get_item_data())

    def __iter__(self):
        return iter(self.get_item_data()['fields'])

    def __len__(self):
        return len(self.get_item_data()['fields'])

    def get_item_data(self):
        raise NotImplementedError()

    @property
    def item_id(self):
        return self.get_item_data()['item_id']

    @property
    def item_id__str(self):
        return '%d' % self.item_id

    @property
    def unique_id(self):
        return int(self.get_item_data()['link'].rsplit('/', 1)[1])

    @property
    def unique_id__str(self):
        return self.get_item_data()['link'].rsplit('/', 1)[1]

    @property
    def link(self):
        return self.get_item_data()['link']


class Item(BaseItem):

    def __init__(self, item_data):
        self.item_data = item_data

    def get_item_data(self):
        return self.item_data


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
    print(f"Got {len(resp['items'])} ...")
    all_items.extend(resp['items'])

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

    print("Got all items!") 
    return all_items
