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
        
    def __str__(self):
        return self.msg   

class Blogger(object):
    """
    
    A Python interface to the blogger API.
    Since Blogger API for BlogSpot has been discontinued, this class will be built upon using Google Blogger API.
    
    """

    def __init__(self, serverapi, username, password):
        
        raise BlogError("This class has not yet been implemented")
        
    #     self.username   = username
    #     self.password   = password
    #     self.appid      = '0123456789ABCDEF'        # Now blogger.com does not require appid. This default value will do
    #     
    #     self.server     = xmlrpclib.Server(serverapi)
    # 
    # def ListMethods(self):
    #     """Helper function to list methods"""
    #     return self.server.system.listMethods()
    # 
    # def GetUserBlogs(self):
    #     """Returns the blogs associated with the user"""
    #     return self.server.blogger.getUsersBlogs(self.appid, self.username, self.password)
    # 
    # def GetUserInfo(self):
    #     """Returns info for the user"""
    #     return self.server.blogger.getUserInfo(self.appid, self.username, self.password)
    # 
    # def GetRecentPosts(self, blogid=1, numposts=10):
    #     """Returns the recent numposts for blogid"""
    #     return self.server.blogger.getRecentPosts(self.appid, blogid, self.username, self.password, numposts)
    #     
    # def GetPost(self, postid):
    #     """Returns details about a particular post"""
    #     return self.server.metaWeblog.getPost(postid, self.username, self.password)
    # 
class MetaWeblog(object):
    """
    Python interface to Metaweblog API

    This class is just a simple encapsulator over Metaweblog API RPC-XML. It does nothing but call the corresponding XMLRPC functions and check for error.
    
    Rightnow, it returns Python based dictionary as it is returned by the server but later on we maybe encapsulate the data using simplified custon object.
    """

    def __init__(self, serverapi, username, password):
        
        """
        Creates and returns a Metaweblog object.
        
        Args:
            serverapi = URL to the XML-RPC API.
            username  = Username for the MetaWeblog enabled Blog account.
            password  = Password for the MetaWevlog enabled Blog account.
        """
        self.username           = username
        self.password           = password
        self.methods            = []

        # Check if URL exists
        if not checkURL(serverapi):
            raise BlogError('XML-RPC API URL not found.')
        
        # Connect to the api. Call listMethods to keep a dictionary of available methods
        self.server             = xmlrpclib.ServerProxy(serverapi)
        self.ListMethods()
        
    def ListMethods(self):
        """Call systen.listMethods on server.
        
        Returns:
            List of XML-RPC methods implemented by the server. 
        """
        if not len(self.methods):
            try:
                self.methods = self.server.system.listMethods()
            except xmlrpclib.Fault, fault:
                raise BlogError(fault.faultString)
            
        return self.methods #.sort()
        
    def GetRecentPosts(self, numposts=10, blogid=1):
        """
        Returns 'numposts' number of recent post for the blog identified by 'blogid'
        
        Args:
            numposts = Number of posts to be returned [optional]
            blogid   = id of thr blog
            """
        return self.Execute('metaWeblog.getRecentPosts', blogid, self.username, self.password, numposts)
    
    def GetPost(self, postid):
        """
        Returns dictionary based post content corresponding to postid.
        
        Args:
            postid = Unique identifier for the post
        """
        return self.Execute('metaWeblog.getPost', postid, self.username, self.password)
        
    def DeletePost(self, postid, publish=True):
        """
        Deletes a post identified by postid

        Args:
            postid = post identified by postid.
            Publish = Publish status.
        
        """
        return self.Execute('metaWeblog.deletePost', postid, self.username, self.password, publish)

    def EditPost(self,postid,newpost,pubish=True):
        """
        Edits a post identified by postid with content passed in newpost

        Args:
            postid = post identified by postid.
            newpost = dictionary with content details about the new post.
            Publish = Publish status.        
        """
        return self.Execute('metaWeblog.editPost', postid, self.username, self.password, newpost, publish)

    def Execute(self, methodname, *args):
        
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
    
def main():
    pass

if __name__ == '__main__':
    main()
