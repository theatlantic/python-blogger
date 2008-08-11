#!/usr/bin/python


""""
Copyright (c) 2008, Ritesh Nadhani
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer 
in the documentation and/or other materials provided with the distribution.
Neither the name of Ritesh Nadhani nor the names of its contributors may be used to endorse or promote products 
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, 
BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import xmlrpclib
import urllib

# Helper function to check if URL exists

def checkURL(url):
    try: urllib.urlopen(url)
    except IOError: return 0
    return 1

class BlogError(Exception):
    
    '''Base class for Blog errors'''
    METHOD_NOT_SUPPORTED           = 'Method not (yet) supported'
    
    def __init__(self, msg):
        self.msg  = msg
        
    def __repr__(self):
        return self.msg   

    __str__ = __repr__   
        
class Blog(object):
    """
    Base class for all blog object. Python interface to various blogging API

    This and extending class are just simple encapsulators over XML-RPC. It does nothing but call the corresponding XMLRPC functions and check for error.
    
    Rightnow, it returns Python based dictionary as it is returned by the server but later on we maybe encapsulate the data using simplified custon object.
    """
    def __init__(self, serverapi, username, password):
        """
        Args:
            serverapi = URL to the XML-RPC API.
            username  = Username for the Blog account.
            password  = Password for the Blog account.
        """
        self.username           = username
        self.password           = password
        self.methods            = []

        # Check if URL exists
        if not checkURL(serverapi):
            raise BlogError('XML-RPC API URL not found.')

        # Connect to the api. Call listMethods to keep a dictionary of available methods
        self.server             = xmlrpclib.ServerProxy(serverapi)
        self.list_methods()

    def list_methods(self):
        """Call systen.listMethods on server.

        Returns:
            List of XML-RPC methods implemented by the server. 
        """
        if not len(self.methods):
            try:
                self.methods = self.server.system.listMethods()
            except xmlrpclib.Fault, fault:
                raise BlogError(fault.faultString)

        return self.methods.sort()

    def execute(self, methodname, *args):

        """
        Callback function to call the XML-RPC method

        Args:
           methodname = XML-RPC methodname.
           args = Arguments to the call. 
        """
        if not methodname in self.methods:
            raise BlogError(BlogError.METHOD_NOT_SUPPORTED)

        try:
            r = getattr(self.server, methodname)(args)
        except xmlrpclib.Fault, fault:
            raise BlogError(fault.faultString)

        return r
        

class Blogger(object):
    """
    A Python interface to the blogger API.
    """

    def __init__(self, serverapi, username, password):
        raise BlogError("This class has not yet been implemented")

class MetaWeblog(Blog):
    """
    Python interface to Metaweblog API
    This class extends Blog to implement metaWeblog API
    """

    def __init__(self, serverapi, username, password):
        Blog.__init__(self, serverapi, username, password)
        
    def get_recent_posts(self, numposts=10, blogid=1):
        """
        Returns 'numposts' number of recent post for the blog identified by 'blogid'
        
        Args:
            numposts = Number of posts to be returned [optional]
            blogid   = id of thr blog
            """
        return self.execute('metaWeblog.getRecentPosts', blogid, self.username, self.password, numposts)
    
    def get_post(self, postid):
        """
        Returns dictionary based post content corresponding to postid.
        
        Args:
            postid = Unique identifier for the post
        """
        return self.execute('metaWeblog.getPost', postid, self.username, self.password)
        
    def new_post(self, content, publish=True, blogid=1):
        """
        New post

        Args:
            content = Dictionary containing post dat.
            Publish = Publish status.
            blogid  = Blog ID
        
        """
        return self.execute('metaWeblog.newPost', blogid, self.username, self.password, content, publish)

    def edit_post(self, postid, newpost, pubish=True):
        """
        Edits a post identified by postid with content passed in newpost

        Args:
            postid = post identified by postid.
            newpost = dictionary with content details about the new post.
            Publish = Publish status.        
        """
        return self.execute('metaWeblog.editPost', postid, self.username, self.password, newpost, publish)

    def delete_post(self, postid, publish=True):
        """
        Deletes a post identified by postid

        Args:
            postid = post identified by postid.
            Publish = Publish status.

        """
        return self.execute('metaWeblog.deletePost', postid, self.username, self.password, publish)

    def get_categories(self, blogid=1):
        """
        Returns a list of categories.

        Args:
            blogid = Blog ID
        """
        return self.execute('metaWeblog.getCategories', blogid, self.username, self.password)

    def get_users_blogs(self):
        """
        Returns a list of blogs associated by the user.

        """
        return self.execute('metaWeblog.getUsersBlogs', self.username, self.password)

    def new_media_object(self, new_object, blogid=1):
        """
        Args:
            new_object = Structure containing information about new media object to be uploaded
            blogid = Blog ID
            
        Returns:
            URL to the uploaded file

        """
        return self.execute('metaWeblog.newMediaObject', blogid, self.username, self.password, new_object)
        
class WordPress(MetaWeblog):
    """
    Python interface to Wordpress API
    Wordpress basically implements all MetaWebLog and extends it by providing it with its methods.
    """

    def __init__(self, serverapi, username, password):
        MetaWeblog.__init__(self, serverapi, username, password)
        
    def delete_category(self, catid, blogid=1):
        """
        Args:
            catid = Category ID
            blogid = Blog ID
            
        """
        return self.execute('wp.deleteCategory', blogid, self.username, self.password, catid)

    def edit_page(new, content, publish=True, blogid=1):
        """
        Args:
            content - Dictionary of new content
        """
        return self.execute('wp.newPage', blogid, self.username, self.password, content, publish)
        
    def edit_page(self, pageid, content, publish=True, blogid=1):
        """
        Args:
            pageid = Page to edit
            content - Dictionary of new content
        """
        return self.execute('wp.editPage', blogid, pageid, self.username, self.password, content, publish)

    def delete_page(self, pageid, blogid=1):
        """
        Args:
            pageid = Page to delete
        """
        return self.execute('wp.deletePage', blogid, self.username, self.password, pageid)

    def get_pages(self, blogid=1):
        """
        Returns a list of the most recent pages in the system.
        """
        return self.execute('wp.getPages', blogid, self.username, self.password)

    def get_page(self, pageid, blogid=1):
        """
        Returns the content of page identified by pageid
        """
        return self.execute('wp.getPage', blogid, pageid, self.username, self.password)

        
def main():

if __name__ == '__main__':
    main()
