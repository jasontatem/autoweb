import requests
from lxml import html
from copy import deepcopy
import urlparse


class Browser(object):
    def __init__(self):
        self.history = list()
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        self.response = None
        self.html = None
        self.allow_redirects = True

    def save_state(self):
        """
        Saves the state of the browser into the history list
        :return: Nothing
        """
        current_state = deepcopy(self)
        self.history.append(current_state)

    def update_state(self, response):
        """
        Updates object attributes with new state data
        :param response: Requests response object to use for state update
        :return: Nothing
        """
        self.response = response
        self.html = html.fromstring(response.content)

    def clear_history(self):
        """
        Clears history
        :return: Nothing
        """
        self.history = list()

    def forms(self):
        """
        List all forms found in the current HTML
        :return: List of forms represented as field:value dicts
        """
        if self.html is None:
            return None
        else:
            return [form_fields_to_dict(form.fields) for form in self.html.forms]

    def links(self):
        """
        List all links found in the current HTML
        :return: List of link URLs as strings
        """
        if self.html is None:
            return None
        else:
            return self.html.xpath('//a/@href')

    def scripts(self):
        """
        List all scripts found in the current HTML
        :return: List of scripts as strings
        """
        if self.html is None:
            return None
        else:
            return [s.text for s in self.html.xpath('//script')]

    def open(self, *args, **kwargs):
        """
        Convenience method for familiarity with mechanize, just a wrapper for
        get()
        All arguments are passed through to get()
        :return: Result of get() - a requests response object or exception
        """
        return self.get(*args, **kwargs)

    def submit_form(self, form_index, post_data):
        """
        Form submission method.  Use forms() method to get a list of forms
        parsed from the page's HTML, if any.
        :param form_index: Integer index of the form, matching its index in the
        output of forms()
        :param post_data: Dict with form input keys:values.  This dict will be
        merged with form values pre-existing in the HTML, with user-supplied
        values overriding in key conflicts.
        :return: Result of get() or post() (as determined by the form action) - a
        requests response object or exception
        """

        if self.html is None:
            raise ValueError('No HTML present in browser object, have you viewed a URL yet?')
        if self.forms() is None or len(self.forms()) == 0:
            raise ValueError('No forms present in current HTML')
        if form_index >= len(self.html.forms) or form_index < 0:
            raise IndexError('index out of range, {0} forms available'.format(len(self.html.forms)))

        form_defaults = form_fields_to_dict(self.html.forms[form_index].fields)
        full_postdata = merge_two_dicts(form_defaults, post_data)

        action_url = self.html.forms[form_index].action
        url = resolve_form_url(self.response.url, action_url)

        if self.html.forms[form_index].method == 'GET':
            return self.get(url, params=full_postdata)
        elif self.html.forms[form_index].method == 'POST':
            return self.post(url, data=full_postdata)
        else:
            raise Exception('Form method {0} found, expect GET or POST'.format(self.html.forms[form_index].method))

    def get(self, *args, **kwargs):
        """
        Wrapper function for get() method on the session object, with history
        persistence.
        All arguments will be passed to the session's get() method, which mirrors
        the functionality of requests.get()
        :return: Result of session.get() - a requests response object or exception
        """
        self.save_state()
        response = self.session.get(allow_redirects=self.allow_redirects, *args, **kwargs)
        self.update_state(response)
        return response

    def post(self, *args, **kwargs):
        """
        Wrapper function for post() method on the session object, with history
        persistence.
        All arguments will be passed to the session's post() method, which mirrors
        the functionality of requests.post()
        :return: Result of session.post() - a requests response object or exception
        """
        self.save_state()
        response = self.session.post(allow_redirects=self.allow_redirects, *args, **kwargs)
        self.update_state(response)
        return response

    def put(self, *args, **kwargs):
        """
        Wrapper function for put() method on the session object, with history
        persistence.
        All arguments will be passed to the session's put() method, which mirrors
        the functionality of requests.put()
        :return: Result of session.put() - a requests response object or exception
        """
        self.save_state()
        response = self.session.put(allow_redirects=self.allow_redirects, *args, **kwargs)
        self.update_state(response)
        return response

    def patch(self, *args, **kwargs):
        """
        Wrapper function for patch() method on the session object, with history
        persistence.
        All arguments will be passed to the session's patch() method, which mirrors
        the functionality of requests.patch()
        :return: Result of session.patch() - a requests response object or exception
        """
        self.save_state()
        response = self.session.patch(allow_redirects=self.allow_redirects, *args, **kwargs)
        self.update_state(response)
        return response

    def delete(self, *args, **kwargs):
        """
        Wrapper function for delete() method on the session object, with history
        persistence.
        All arguments will be passed to the session's delete() method, which mirrors
        the functionality of requests.delete()
        :return: Result of session.delete() - a requests response object or exception
        """
        self.save_state()
        response = self.session.delete(allow_redirects=self.allow_redirects, *args, **kwargs)
        self.update_state(response)
        return response

    def request(self, *args, **kwargs):
        """
        Wrapper function for request() method on the session object, with history
        persistence.
        All arguments will be passed to the session's request() method, which mirrors
        the functionality of requests.request()
        :return: Result of session.request() - a requests response object or exception
        """
        self.save_state()
        response = self.session.request(allow_redirects=self.allow_redirects, *args, **kwargs)
        self.update_state(response)
        return response


def form_fields_to_dict(form_fields):
    """
    Takes a lxml form fields object and returns a friendly dict of field: value pairs
    :param form_fields: lxml form fields object
    :return: dict of field: value pairs
    """
    result = {}
    for k in form_fields:
        result[k] = form_fields[k]
    return result


def resolve_form_url(page_url, action_url):
    """
    Takes a page URL and a form action URL and resolves into a full URL
    :param page_url: URL of the page where the form submission is occurring
    :param action_url: URL of the form's action attribute
    :return: String with the combined full URL
    """
    page_url_p = urlparse.urlparse(page_url)
    action_url_p = urlparse.urlparse(action_url)
    if action_url_p.scheme != '':
        return action_url
    elif action_url_p.path.startswith('/'):
        return '{0}://{1}{2}'.format(page_url_p.scheme, page_url_p.netloc, action_url_p.path)
    else:
        return '{0}://{1}{2}{2}'.format(page_url_p.scheme, page_url_p.netloc, page_url_p.path, action_url_p.path)


def merge_two_dicts(x, y):
    """
    Merge two dictionaries, allowing the second to override any keys present in the first
    :param x: Dict 1
    :param y: Dict 2, with precedence for any shraed keys
    :return: Combined dict
    """
    z = x.copy()
    z.update(y)
    return z
