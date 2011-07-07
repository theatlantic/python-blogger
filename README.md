This is a python wrapper around the Metaweblog, Wordpress, and MovableType XML-RPC APIs. It is a fork of the Google Code project [python-blogger](http://code.google.com/p/python-blogger/).

## Introduction

This library provides a python interface for the various blogging API. Currently, only Metaweblog and Wordpress are implemented but it will be soon be extended to use MovableType.
  
## Installing/Building

To install with pip from source:

    $ pip install git+git://github.com/theatlantic/python-blogger.git

If the source is already checked out, use setuptools:

    $ python setup.py install

## Using

    import pyblog
    blog = pyblog.WordPress('http://www.example.com/blog/xmlrpc.api', 'USERNAME', 'PASSWORD')
    print blog.get_recent_posts()

All return values are the standard Python based objects returned by xmlrpclib.

## Notes

pyblog.MetawWeblog objects implements all metaWeblog API as documented at [http://www.xmlrpc.com/metaWeblogApi](http://www.xmlrpc.com/metaWeblogApi). The method names are modified to follow python naming conventions, so getRecentPosts() becomes get_recent_posts(). For API calls requiring struct parameter you will have to pass a dictionary with the corresponding key/value pair.

pyblog.Wordpress which extends pyblog.MetaWeblog implements the extra Wordpress XML-RPC methods. Currently, this API library fulfills all the functions provided with Wordpress v2.6

## License

Licensed under the [Simplified BSD License](http://www.opensource.org/licenses/bsd-license.php). View the LICENSE file included with the source for complete license and copyright information.