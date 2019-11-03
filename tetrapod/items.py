import os
import math
import time
import datetime
import logging
from collections.abc import Mapping
from decimal import Decimal

log = logging.getLogger(__name__)


class PodioFieldMediator(object):
    """
    A Mediator is an object that converts a Python-side value of Podio item field
    to its Podio JSON form and back.

    When you use __getitem__() on an Item object, the Mediators take value and
    convert it into something easily useable in Python, e.g.:

    >>> item = Item(podio.get('https://api.podio.com/item/123455'))
    >>> print(item['title'])

    As soon as you call ['title'] the Mediator gets involved. The same goes
    for set-value operations, e.g.:

    >>> item['title'] = "Some example text."
    """

    def update(self, field, value, field_param=None):
        raise NotImplementedError()

    def fetch(self, field, field_param):
        raise NotImplementedError()


class EmbedMediator(PodioFieldMediator):
    """
    embed:
      embed: The id of an embed returned from the Add an embed operation.
      file: The id of one the thumbnail files returned from the same operation.
    """
    def fetch(self, field, field_param=None):
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


class ContactMediator(PodioFieldMediator):
    """
    contact:
        value: The profile id of the contact

    Example:
      {
        "user_id": 1234567,
        "space_id": null,
        "rights": [
          "view"
        ],
        "url": [
          "http://example.com"
        ],
        "type": "user",
        "image": {
          "hosted_by": "podio",
          "hosted_by_humanized_name": "Podio",
          "thumbnail_link": "https://d2cmuesa4snpwn.cloudfront.net/public/123456789",
          "link": "https://d2cmuesa4snpwn.cloudfront.net/public/123456789",
          "file_id": 123456789,
          "external_file_id": null,
          "link_target": "_blank"
        },
        "profile_id": 123456789,
        "org_id": null,
        "phone": [
          "+xxxxxxxxxx"
        ],
        "link": "https://podio.com/users/1234567",
        "avatar": 123456789,
        "mail": [
          "john@example.com"
        ],
        "external_id": null,
        "last_seen_on": "2018-11-11 11:11:00",
        "name": "John Doe"
      }
    """
    def fetch(field, field_param=None):
        if field_param is None:
            for value in field.get('values', []):
                return value['value']
        elif field_param == 'all':
            return [v['value'] for v in field.get('values', [])]
        return None

# member:
#   value: The user id of the member

class AppMediator(PodioFieldMediator):
    """
    app:
      value: The id of the app item
    """
    def fetch(self, field, field_param=None):
        if field_param is None:
            for value in field.get('values', []):
                return value['value']
        elif field_param == 'all':
            return [v['value'] for v in field.get('values', [])]
        return None


class DateMediator(PodioFieldMediator):
    """
    date:
        start_date: The start date
        start_time: The start time
        end_date: The end date
        end_time: The end time
    """
    def fetch(self, field, field_param=None):
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


class NumberMediator(PodioFieldMediator):
    """
    number:
        value: The decimal value of the field as a string.
    """
    def fetch(field, field_param=None):
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


class TextMediator(PodioFieldMediator):
    """
    text:
        value: The value of the field which can be any length.
        format: The format of the text, either plain, markdown or html
    """
    def update(self, field, value, field_param=None):
        field['values'] = [{
            'value': value
        }]

    def fetch(self, field, field_param=None):
        if field_param is None:
            for value in field.get('values', []):
                return value['value']
        return None


class CategoryMediator(PodioFieldMediator):
    """
    category:
        value: The id of the option
    """
    def fetch(self, field, field_param=None):
        if field_param == 'choices':
            options = field['config']['settings']['options']
            # inactive options are not show to the user
            return [(opt['id'], opt['text']) for opt in options if opt['status'] == 'active']
        # The same as '__choices' but instead of a list of tuples it returns a dictionary
        # that contains the choices and choice ID numbers.
        elif field_param == 'choices_dict':
            options = field['config']['settings']['options']
            # inactive options are not show to the user
            return {opt['text']: opt['id'] for opt in options if opt['status'] == 'active'}
        elif field_param == 'active':
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

class EmailMediator(PodioFieldMediator):
    """
    email:
        value: Text value (max 254 characters)
        type: "home"/"work"/ "other"
    """

    def fetch(self, field, field_param=None):
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


class CalculationMediator(PodioFieldMediator):
    def fetch(self, field, field_param=None):
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

MEDIATORS = {
    'app': AppMediator,
    'calculation': CalculationMediator,
    'category': CategoryMediator,
    'contact': ContactMediator,
    'date': DateMediator,
    'email': EmailMediator,
    'embed': EmbedMediator,
    'number': NumberMediator,
    'text': TextMediator,
    # ... add future mediators here
}


def split_descriptor_parts(field_descriptor):
    """
    :param field_descriptor:
    :return:
    """
    descriptor_parts = field_descriptor.split('__', 1)
    if len(descriptor_parts) == 2:
        external_id = descriptor_parts[0]
        field_param = descriptor_parts[1]
    else:
        external_id = descriptor_parts[0]
        field_param = None
    return external_id, field_param

def get_field_from_podio_json_list(item_json, external_id):
    """
    :param external_id:
    :return:
    """
    if '_' in external_id:
        external_id = external_id.replace('_', '-')

    fields = item_json.get('fields', [])

    for field in fields:
        if field['external_id'] == external_id:
            return field


def find_mediator_class(field):
    field_type = field['type']
    # try to find the correct PodioFieldMediator class
    mediator_class = MEDIATORS.get(field_type)
    if not mediator_class:
        raise NotImplementedError('Field type "%s" is not supported, yet.' % field_type)
    return mediator_class


def fetch_field(field_descriptor, item_json):
    """
    Fetch the first value of a field - or None if the field is empty.
    :param field_descriptor: The Podio external_id name as shown in the developer view.
    :param item_json: The JSON representation of the Podio item.
    :return: First value or None
    """
    external_id, field_param = split_descriptor_parts(field_descriptor)

    # Get the only the JSON part of the desired field
    field = get_field_from_podio_json_list(item_json, external_id)
    if not field:
        return None

    # Find and instanciate the correct PodioFieldMediator for this kind of field.
    mediator_class = find_mediator_class(field)
    mediator = mediator_class()

    # Use the mediator to get the actual data
    return mediator.fetch(field, field_param)


def update_field(field_descriptor, new_value, item_json):
    external_id, field_param = split_descriptor_parts(field_descriptor)

    # Get the only the JSON part of the desired field
    field = get_field_from_podio_json_list(item_json, external_id)

    # Find and instanciate the correct PodioFieldMediator for this kind of field.
    mediator_class = find_mediator_class(field)
    mediator = mediator_class()

    # Use the mediator to get the actual data
    return mediator.update(field, new_value, field_param)


class BaseItem(Mapping):
    def __getitem__(self, key):
        return fetch_field(key, self.get_item_data())

    def __setitem__(self, key, value):
        update_field(key, value, self.get_item_data())
        self._tainted.add(key)

    def __iter__(self):
        return iter(self.get_item_data()['fields'])

    def __len__(self):
        return len(self.get_item_data()['fields'])

    def get_item_data(self) -> list:
        raise NotImplementedError()

    @property
    def app_id(self):
        return self.get_item_data()['app']['app_id']

    @property
    def app_id__str(self):
        return '%d' % self.app_id

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

    def as_podio_dict(self, fields=None):
        """
        Returns the object as a dictionary ready to be JSON-serialized and to be sent
        to Podio's "create item" (POST) or "update item values" (PUT).

        The fields parameter is an optional list of fields to be include. The default
        is to include all fields.
        """
        podio_dict = {}
        for field in self.get_item_data().get('fields', []):
            external_id = field['external_id']

            # do not add fields to the dict that are not in the fields list.
            if fields and external_id not in fields:
                continue

            podio_dict[external_id] = field['values']

        return podio_dict


class Item(BaseItem):

    def __init__(self, item_data):
        self._tainted = set()
        self.item_data = item_data

    def get_item_data(self):
        return self.item_data