#!/usr/bin/python

import os
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
	Base class for all blog objects.
	"""
	def __init__(self, serverapi, username, password, default_blog_id=None, appkey='0x001'):
		"""
		Args:
			serverapi = URL to the XML-RPC API.
			username  = Username for the Blog account.
			password  = Password for the Blog account.
		"""
		self.username = username
		self.password = password
		self.appkey = appkey    
		self.methods = []
		if default_blog_id is not None:
			self.default_blog_id = default_blog_id

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
		
	def is_method_available(self, methodname):
		"""Returns if a method is supported by the XML-RPC server"""
		if methodname in self.methods:
			return True
		else:
			return False


class MetaWeblog(Blog):
	"""
	Python interface to Metaweblog API
	This class extends Blog to implement metaWeblog API
	"""

	def __init__(self, serverapi, username, password, default_blog_id, appkey='0x001'):
		Blog.__init__(self, serverapi, username, password, appkey, default_blog_id)
		
	def get_recent_posts(self, numposts=10, blog_id=None):
		"""
		Returns 'numposts' number of recent posts for the blog identified by 'blog_id'
		
		Args:
			blog_id (int): Blog ID
			numposts (int): Number of posts to be returned [optional]
		"""
		if blog_id is None:
			if self.default_blog_id is None:
				raise BlogError("No blog_id passed")
			blog_id = self.default_blog_id
		return self.execute('metaWeblog.getRecentPosts', blog_id, self.username, self.password, numposts)
	
	def get_post(self, post_id):
		"""
		Returns dictionary based post content corresponding to post_id.
		
		Args:
			post_id = Unique identifier for the post
		"""
		return self.execute('metaWeblog.getPost', post_id, self.username, self.password)
		
	def new_post(self, content, publish=False, blog_id=None):
		"""
		New post

		Args:
			content (dict): Dictionary containing post data.
			publish (bool): Publish status.
			blog_id (int): Blog ID
		
		"""
		if blog_id is None:
			if self.default_blog_id is None:
				raise BlogError("No blog_id passed")
			blog_id = self.default_blog_id
		return self.execute('metaWeblog.newPost', blog_id, self.username, self.password, content, publish)

	def edit_post(self, post_id, new_post, publish=True):
		"""
		Edits a post identified by post_id with content passed in new_post

		Args:
			post_id (int): post identified by post_id.
			new_post (dict): dictionary with content details about the new post.
			publish (bool): Publish status.        
		"""
		return self.execute('metaWeblog.editPost', post_id, self.username, self.password, newpost, publish)

	def delete_post(self, post_id, publish=True):
		"""
		Deletes a post identified by post_id

		Args:
			post_id = post identified by post_id.
			publish = Publish status.

		"""
		return self.execute('metaWeblog.deletePost', self.appkey, post_id, self.username, self.password, publish)

	def get_categories(self, blog_id=None):
		"""
		Returns a list of categories.

		Args:
			blog_id (int): Blog ID
		"""
		if blog_id is None:
			if self.default_blog_id is None:
				raise BlogError("No blog_id passed")
			blog_id = self.default_blog_id
		
		return self.execute('metaWeblog.getCategories', blog_id, self.username, self.password)

	def get_users_blogs(self):
		"""
		Returns a list of blogs associated with the user.

		"""
		return self.execute('metaWeblog.getUsersBlogs', self.appkey, self.username, self.password)

	def new_media_object(self, new_object, name=None, blog_id=None):
		"""
		Args:
			new_object (dict): Dict with the following keys
				bits (str): base64-encoded contents of the file
				name (str): the name of the file
			blog_id (int): Blog ID
			
		Returns:
			URL to the uploaded file

		"""
		if blog_id is None:
			if self.default_blog_id is None:
				raise BlogError("No blog_id passed")
			blog_id = self.default_blog_id
		
		if isinstance(new_object, str) or isinstance(new_object, unicode):
			try:
				if os.path.exists(new_object):
					media_bits = xmlrpclib.Binary(open(new_object).read())
					if name is not None:
						media_name = name
					else:
						media_name = os.path.basename(new_object)
					new_object = {'bits': media_bits, 'name': media_name}
			except ValueError:
				pass
		# See if the new_object implements file methods
		elif type(getattr(new_object, 'read', None)).__name__ == 'function':
			media_bits = xmlrpclib.Binary(new_object.read())
			if name is not None:
				media_name = name
			else:
				media_name = os.path.basename(new_object.name)
			new_object = {'bits': media_bits, 'name': media_name}
		elif isinstance(new_object, dict):
			if name is not None:
				new_object['name'] = name
		
		return self.execute('metaWeblog.newMediaObject', blog_id, self.username, self.password, new_object)
		
	def get_template(self, template_type, blog_id=None):
		"""
		Returns the template type identifed by template_type
		"""
		if blog_id is None:
			if self.default_blog_id is None:
				raise BlogError("No blog_id passed")
			blog_id = self.default_blog_id
		
		return self.execute("metaWeblog.getTemplate", self.appkey, blog_id, self.username, self.password, template_type)
		
	def set_template(self, template, template_type, blog_id=None):
		"""
		Sets the new template value for template_type
		"""
		if blog_id is None:
			if self.default_blog_id is None:
				raise BlogError("No blog_id passed")
			blog_id = self.default_blog_id
		
		return self.execute("metaWeblog.setTemplate", self.appkey, blog_id, self.username, self.password, template, template_type)        
		
class WordPress(MetaWeblog):
	"""
	Python interface to Wordpress API
	Wordpress basically implements all MetaWebLog and extends it by providing it with its methods.
	"""
	
	default_blog_id = 1
	
	def __init__(self, serverapi, username, password, default_blog_id=1):
		MetaWeblog.__init__(self, serverapi, username, password, default_blog_id=default_blog_id)
		
	def get_post_status_list(self, blog_id=None):
		"""
		Returns a dict of all the valid post statuses ( draft, pending, private, publish ) and their descriptions 
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.getPostStatusList', blog_id, self.username, self.password)

	def get_authors(self, blog_id=None):
		"""
		Get a list of users for the blog.
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.getAuthors', blog_id, self.username, self.password)
		
	def new_page(self, content, publish=True, blog_id=None):
		"""
		Args:
			content - Dictionary of new content
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.newPage', blog_id, self.username, self.password, content, publish)
		
	def edit_page(self, page_id, content, publish=True, blog_id=None):
		"""
		Args:
			page_id (int): Page to edit
			content (dict): Dictionary of new content
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.editPage', blog_id, page_id, self.username, self.password, content, publish)

	def delete_page(self, page_id, blog_id=None):
		"""
		Args:
			page_id (int): Page to delete
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.deletePage', blog_id, self.username, self.password, page_id)

	def get_pages(self, blog_id=None):
		"""
		Returns a list of the most recent pages in the system.
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.getPages', blog_id, self.username, self.password)

	def get_page(self, page_id, blog_id=None):
		"""
		Returns the content of page identified by page_id
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.getPage', blog_id, page_id, self.username, self.password)
		
	def get_page_list(self, blog_id=None):
		"""
		Get an list of all the pages on a blog. Just the minimum details, lighter than wp.getPages.
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.getPageList', blog_id, self.username, self.password)
		
	def get_page_status_list(self, blog_id=None):
		"""
		Returns a dict of all the valid page statuses ( draft, private, publish ) and their
		descriptions ( Draft, Private, Published)
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.getPageStatusList', blog_id, self.username, self.password)        
		
	def new_category(self, content, blog_id=None):
		"""
		Args:
			content (dict): Dictionary content having data for new category.
			
		Returns id of new value
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.newCategory', blog_id, self.username, self.password, content)

	def delete_category(self, cat_id, blog_id=None):
		"""
		Args:
			cat_id (int): Category ID
			blog_id (int): Blog ID

		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.deleteCategory', blog_id, self.username, self.password, cat_id)
		
	def get_comment_count(self, post_id=0, blog_id=None):
		"""
		Provides a struct of all the comment counts ( approved, awaiting_moderation, spam, total_comments ) for a given post_id.
		The post_id parameter is optional (or can be set to zero), if it is not provided then the same struct is returned, but for the 
		entire blog instead of just one post
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		return self.execute('wp.getCommentCount', blog_id, self.username, self.password, post_id)
		
	def get_users_blogs(self):
		"""
		Returns a list of blogs associated by the user.
		"""
		return self.execute('wp.getUsersBlogs', self.username, self.password)

	def get_options(self, options=[], blog_id=None):
		"""
		Return option details.
		
		The parameter options, list, is optional. If it is not included then it will return all of the option info that we have. 
		With a populated list, each field is an option name and only those options asked for will be returned.
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.getOptions', blog_id, self.username, self.password, options)

	def set_options(self, option, blog_id=None):
		"""
		That option parameter is option name/value pairs. The return value is same as if you called wp.getOptions asking for the those option names, 
		only they'll include the new value. If you try to set a new value for an option that is read-only, it will silently fail and you'll get the original
		value back instead of the new value you attempted to set.
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.setOptions', blog_id, self.username, self.password, option)
		
	def suggest_categories(self, category, max_results=10, blog_id=None):
		"""
		Returns a list of dictionaries of categories that start with a given string.
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.suggestCategories', blog_id, self.username, self.password, category, max_results)
		
	def upload_file(self, data, blog_id=None):
		"""
		Upload a file.
		
		Data contains values as documented at http://codex.wordpress.org/XML-RPC_wp#wp.getCategories
		"""
		if blog_id is None:
			blog_id = self.default_blog_id
		
		return self.execute('wp.uploadFile', blog_id, self.username, self.password, data)

class MovableType(MetaWeblog):
	"""
	A Python interface to the MovableType API.
	"""
	
	appkey = '0x001'
	methods = []
	
	mt_fields = [
		"title",
		"description",
		"dateCreated",
		"mt_allow_comments",
		"mt_allow_pings",
		"mt_convert_breaks",
		"mt_text_more",
		"mt_basename",
		"wp_slug",
		"mt_excerpt",
		"mt_keywords",
		"mt_tb_ping_urls",
		"publish",
		"mt_tags",
	]
	
	def __init__(self, serverapi, username, password, default_blog_id=None):
		self.username = username
		self.password = password
		
		if default_blog_id is not None:
			self.default_blog_id = default_blog_id

		# Check if URL exists
		if not checkURL(serverapi):
			raise BlogError('XML-RPC API URL not found.')

		# Connect to the api. Call mt.supportedMethods to keep a dictionary of available methods
		self.server = xmlrpclib.ServerProxy(serverapi)
		self.list_methods()
	
	def list_methods(self):
		if not len(self.methods):
			try:
				self.methods = self.server.mt.supportedMethods()
			except xmlrpclib.Fault, fault:
				raise BlogError(fault.faultString)

		return self.methods.sort()
	
	def execute(self, methodname, *args):
		if not methodname in self.methods:
			raise BlogError(BlogError.METHOD_NOT_SUPPORTED)
		
		try:
			r = getattr(self.server, methodname)(*args)
		except xmlrpclib.Fault, fault:
			raise BlogError(fault.faultString)
		
		return r
	
	def _parse_custom_fields(self, content):
		if not isinstance(content, dict):
			raise BlogError(
				"Invalid type for field 'content': excepted dict, got %s" \
				% type(content).__name_
			)
		
		custom_fields = []
		
		for key in content.keys():
			if key not in self.mt_fields:
				val = content.pop(key)
				custom_fields.append("%s=%s" % (key, val))
		
		# This is the format that CustomFields::XMLRPCServer uses to encode custom fields
		if len(custom_fields) > 0:
			if 'mt_text_more' not in content:
				content['mt_text_more'] = ''
			content['mt_text_more'] += "\n" + "\n".join(custom_fields)
		
		return content
	
	def get_template(self, template_type, blog_id=None):
		raise BlogError("This method is not implemented")
	
	def set_template(self, template, template_type, blog_id=None):
		raise BlogError("This method is not implemented")
	
	def get_user_info(self, username=None, password=None):
		"""
		Returns information about an author in the system.
		
		Returns:
			dict. Contains the key/values:
				userid (int)
				lastname (str)
				firstname (str)
				nickname (str)
				email (str)
				url (str)
				
		"""
		if username is None or password is None:
			username = self.username
			password = self.password
		
		return self.execute('blogger.getUserInfo', self.appkey, username, password)
	
	def get_category_list(self, blog_id=None):
		"""
		Returns a list of all categories defined in the weblog.
		
		Args:
			blog_id (int): Blog ID
		
		Returns:
			list. An array of structs containing str categoryId and str categoryName.
		"""
		if blog_id is None:
			if self.default_blog_id is None:
				raise BlogError("No blog_id passed")
			blog_id = self.default_blog_id
		
		return self.execute('mt.getCategoryList', blog_id, self.username, self.password)
	
	def set_post_categories(self, post_id, categories):
		"""
		Sets the categories for a post.
		
		Args:
			post_id (int): Post ID
			categories (list): A list of category dicts with the following keys
				categoryId (int): The ID of the category
				isPrimary (bool): Whether this is the primary category; optional
		"""
		return self.execute('mt.setPostCategories', post_id, self.username, self.password, categories)
	
	def get_post_categories(self, post_id):
		"""
		Args:
			post_id (int): Post ID
		
		Returns:
			list. an array of dicts containing categoryName (string), categoryId (string),
			      and isPrimary (boolean).
		"""
		return self.execute('mt.getPostCategories', post_id, self.username, self.password)
	
	def get_recent_post_titles(self, blog_id=None):
		"""
		Args:
			blog_id (int): Blog ID
		
		Returns:
			list. an array of structs containing dateCreated, userid (string), postid (string),
			      and title (string)
		"""
		if blog_id is None:
			if self.default_blog_id is None:
				raise BlogError("No blog_id passed")
			blog_id = self.default_blog_id
		
		return self.execute('mt.getRecentPostTitles', blog_id, self.username, self.password)
	
	def publish_post(self, post_id):
		"""
		Publish (rebuild) all of the static files related to an entry from your weblog.
		Equivalent to saving an entry in the system (but without the ping).
		
		Args:
			post_id (int): Post ID
		
		Returns:
			boolean. True on success, fault on failure
		"""
		return self.execute('mt.publishPost', post_id, self.username, self.password)
	
	
	def edit_post(self, post_id, content, publish):
		"""
		Args:
			post_id (int)
			content (dict) - can contain the following standard keys:
				title - for the title of the entry
				description - for the body of the entry
				dateCreated - the created-on date of the entry in ISO8601 format.
				mt_allow_comments (int) - the value for the allow_comments field
				mt_allow_pings (int) - the value for the allow_pings field
				mt_convert_breaks (string) - the value for the convert_breaks field
				mt_tags (string) - the value for the tags field
				mt_text_more (string) - the value for the additional entry text
				mt_excerpt (string) - the value for the excerpt field
				mt_keywords (string) - the value for the keywords field
				mt_tb_ping_urls (list) - the list of TrackBack ping URLs for this entry
				publish (boolean) - whether to publish
				** - Any custom fields
		"""
		content = self._parse_custom_fields(content)
		if 'publish' not in content:
			content['publish'] = publish
		
		return self.execute('metaWeblog.editPost', post_id, self.username, self.password, content, publish)
	
	def get_recent_posts(self, numposts=10, blog_id=None):
		"""
		Returns 'numposts' number of recent posts for the blog identified by 'blog_id'

		Args:
			blog_id (int): Blog ID
			numposts (int): Number of posts to be returned [optional]

		Returns:
			list. An array of dicts containing the following key/values:
				dateCreated (str) - ISO8601 date
				userid (str)
				postid (str)
				title (str)
				link (str)
				permaLink (str)
				mt_excerpt (str)
				mt_text_more (str)
				mt_allow_comments (str)
				mt_allow_pings (str)
				mt_convert_breaks (str)
				mt_keywords (str)

		"""
		if blog_id is None:
			if self.default_blog_id is None:
				raise BlogError("No blog_id passed")
			blog_id = self.default_blog_id
		
		return self.execute('metaWeblog.getRecentPosts', blog_id, self.username, self.password, numposts)
	
	def new_post(self, content, publish=False, blog_id=None):
		"""
		New post

		Args:
		content (dict) - can contain the following standard keys:
			title - for the title of the entry
			description - for the body of the entry
			dateCreated - the created-on date of the entry in ISO8601 format.
			mt_allow_comments (int) - the value for the allow_comments field
			mt_allow_pings (int) - the value for the allow_pings field
			mt_convert_breaks (string) - the value for the convert_breaks field
			mt_tags (string) - the value for the tags field
			mt_text_more (string) - the value for the additional entry text
			mt_excerpt (string) - the value for the excerpt field
			mt_keywords (string) - the value for the keywords field
			mt_tb_ping_urls (list) - the list of TrackBack ping URLs for this entry
			publish (boolean) - whether to publish
			** - Any custom fields
		publish (bool): Publish status.
		blog_id (int): Blog ID

		Returns:
			str. The new blog post id.
		"""
		if blog_id is None:
			if self.default_blog_id is None:
				raise BlogError("No blog_id passed")
			blog_id = self.default_blog_id
		
		content = self._parse_custom_fields(content)
		if 'publish' not in content and publish==False:
			content['publish'] = False
		
		return self.execute('metaWeblog.newPost', blog_id, self.username, self.password, content, publish)
	
def main():
	pass
	
if __name__ == '__main__':
	main()
