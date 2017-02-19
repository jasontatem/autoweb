autoweb
=======

A wrapper on top of requests' Session object to aid in browser emulation script development.

Why?
----

I occasionally write scripts where I need to pretend to be a browser.  Stuff like Mechanize and requests' Session object get me there most of the time, but sometimes I have trouble putting the pieces together.
 
The main advantage of this wrapper is historic state tracking.  As long as you interact with the Browser object's wrappers of the underlying Session's methods, a copy of the session state is made on each new "click".

Features
--------

* All major methods of requests Session objects are wrapped - get, post, put, patch, delete, request
* open() method to ease transition for Mechanize users
* lxml-based HTML processing to find forms, links, scripts
* submit_form() helper method, also similar to Mechanize
* History tracking - complete state of browser object is copied on every request.
* Debug mode prints request information as you go for easy capture


Requirements
------------

requests, lxml

Usage
-----

Create a browser object:
```
>>> import autoweb
>>> b = autoweb.Browser()
```
    
Open a URL with a GET:
```
>>> b.get('https://www.google.com')
<Response [200]>
```
Each wrapper (get, post, put, patch, delete, request) returns the requests Response object, but the most recent is also available at b.response

Look at forms:
```
>>> b.forms()
[{'btnI': "I'm Feeling Lucky", 'sclient': 'psy-ab', 'btnK': 'Google Search', 'site': '', 'q': '', 'source': 'hp'}]
```

Submit a form:
```
>>> form_fields = b.forms()[0]  # forms() returns a list, there's only 1 on google.com
>>> form_fields['q'] = 'python'  # Fill in the "q" field with a search term
>>> b.submit_form(0, form_fields)  # Form index number and the dict containing values
```

It is not necessary to capture the fields first.  The dict supplied for the field data will be merged with any values already set in the form.  Values from the user-supplied dict take precedence.

Look at the first 10 links in the Google result:

```
>>> b.links()[0:10]
['#content', '#python-network', '/', '/psf-landing/', 'https://docs.python.org', 'https://pypi.python.org/', '/jobs/', '/community/', '#top', '/']
```

How many links, scripts, and forms are there?
```
>>> len(b.links())
197
>>> len(b.scripts())
7
>>> len(b.forms())
1
```

Look at a script:
```
>>> print(b.scripts()[2])

    var _gaq = _gaq || [];
    _gaq.push(['_setAccount', 'UA-39055973-1']);
    _gaq.push(['_trackPageview']);

    (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
    })();
```

Enable debugging:
```
>>> b.debug_enable = True
>>> b.get('https://www.google.com')
URL: https://www.google.com/
Response Code: 200
Content-Type: text/html; charset=UTF-8
Headers: 11, Cookies: 0
Forms: 1, Links: 41, Scripts: 12
Response first 120 char: <!doctype html><html itemscope="" itemtype="http://schema.org/WebPage" lang="en"><head><meta content="Search the world's
<Response [200]>
```

Disable redirects:
```
>>> b.get('http://www.google.com')
URL: https://www.google.com/?gws_rd=ssl
Response Code: 200
Content-Type: text/html; charset=UTF-8
Headers: 11, Cookies: 0
Forms: 1, Links: 41, Scripts: 12
Response first 120 char: <!doctype html><html itemscope="" itemtype="http://schema.org/WebPage" lang="en"><head><meta content="Search the world's
<Response [200]>
>>> b.allow_redirects = False
>>> b.get('http://www.google.com')
URL: http://www.google.com/
Response Code: 302
Content-Type: text/html; charset=UTF-8
Headers: 8, Cookies: 0
Forms: 0, Links: 1, Scripts: 0
Response first 120 char: <HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>302 Moved</TITLE></HEAD><BODY>
<H1
<Response [302]>
```

With allow_redirects = True (default as it is in requests), the redirection to https://www.google.com happens silently.  Setting to false exposes the 302 response.

Access history:
```
>>> len(b.history)
7
>>> b.history[1].response.url
u'https://www.google.com/'
>>> b.history[2].response.url
u'https://www.python.org/'
>>> b.history[3].session.cookies
<RequestsCookieJar[Cookie(version=0, name='NID', value='<some stuff that looks like a session token>', port=None, port_specified=False, domain='.google.com', domain_specified=True, domain_initial_dot=True, path='/', path_specified=True, secure=False, expires=1503330776, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)]>
```