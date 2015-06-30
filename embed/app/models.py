import simplejson as json

from exceptions import NoItemInDb, ErrorItemImport
from db_wrapper import DatabaseWrapper

db = DatabaseWrapper()


class Item():
	def __init__(self, id, data=None):
		self.id = id
		self.title = ''
		self.creator = ''
		self.source = ''
		self.institution = ''
		self.institution_link = ''
		self.license = ''
		self.description = ''
		self.url = []
		self.image_meta = {}
		self.lock = False
		self.timestamp = ''
		
		if data:
			try:
				data = json.loads(json.JSONEncoder().encode(data))
			except:
				raise ErrorItemImport('There is an error in the item`s model representation %s' % data)
		else:
			data = db.get('item_id@%s' % id)
			
			if not data:
				raise NoItemInDb('No item with specified id stored in db')
			else:
				try:
					data = json.loads(data)
				except:
					raise ErrorItemImport('There is an error in the item`s model representation %s' % data)	
					
		if data.has_key('url'):
			self.url = data['url']
			
			if type(self.url) != list:
				raise ErrorItemImport('There is an error in the batch`s model representation %s' % data)
			
			for i,u in enumerate(self.url):
				self.url[i] = str(u)
		else:
			raise ErrorItemImport('The item doesn`t have all required params')
					
		if data.has_key('title'):
			self.title = data['title']
		if data.has_key('creator'):
			self.creator = data['creator']
		if data.has_key('source'):
			self.source = data['source']
		if data.has_key('institution'):
			self.institution = data['institution']
		if data.has_key('institution_link'):
			self.institution_link = data['institution_link']
		if data.has_key('license'):
			self.license = data['license']
		if data.has_key('description'):
			self.description = data['description']
		if data.has_key('image_meta'):
			self.image_meta = data['image_meta']
		if data.has_key('lock'):
			if data['lock'] == 'True':
				self.lock = True
			else:
				self.lock = False
		if data.has_key('timestamp'):
			self.timestamp = data['timestamp']

	def save(self):
		if self.lock is True:
			lock = 'True'
		else:
			lock = 'False'
		
		db.set('item_id@%s' % self.id, json.dumps({'url': self.url, 'title': self.title, 'creator': self.creator, 'institution': self.institution, 'institution_link': self.institution_link, 'license': self.license, 'description': self.description, 'image_meta': self.image_meta, 'lock': lock, 'timestamp': self.timestamp}))
		
	def delete(self):
		db.delete('item_id@%s' % self.id)
		
		
class Batch():
	def __init__(self, id=None):
		self.items = {}
		self.data = []

		if id is None:
			self.id = db.incr('batch@id', 1)
		else:
			self.id = id
			
			data = db.get('batch@id@%s' % id)

			if not data:
				raise NoItemInDb('No batch with specified id stored in db')
			else:
				try:
					data = json.loads(data)
					
					if data.has_key('items'):
						self.items = data['items']
						
						if type(self.items) != dict:
							raise ErrorItemImport('There is an error in the batch`s model representation %s' % data)
					
					if data.has_key('data'):
						self.data = data['data']
						
						if type(self.data) != list:
							raise ErrorItemImport('There is an error in the batch`s model representation %s' % data)
											
				except:
					raise ErrorItemImport('There is an error in the batch`s model representation %s' % data)
	
	def save(self):
		db.set('batch@id@%s' % self.id, json.dumps({'items': self.items, 'data': self.data}))

	def increment_finished_items(self):
		return db.incr('batch@id@%s@finished_items' % (self.id), 1)

class Task():
	def __init__(self, batch_id, item_id, task_id, data=None):
		self.task_id = task_id
		self.batch_id = batch_id
		self.item_id = item_id
		self.status = 'pending'
		self.url = ''
		self.url_order = 0
		self.image_meta = ''
		self.attempts = 0
		self.type = 'mod'
		self.item_data = {}
		self.item_tasks_count = 0
		
		safe = True
		
		if data is None:
			data = db.get('batch@id@%s@item@id%s@task@id@%s' % (self.batch_id, self.item_id, self.task_id))

			if not data:
				raise NoItemInDb('No task with specified id stored in db')
			else:
				try:
					data = json.loads(data)
					safe = False
						
				except:
					raise ErrorItemImport('There is an error in the batch`s model representation %s' % data)
		
		if data.has_key('status'):
			self.status = data['status']
		if data.has_key('url'):
			self.url = data['url']
		if data.has_key('url_order'):
			self.url_order = data['url_order']
		if data.has_key('image_meta'):
			self.image_meta = data['image_meta']
		if data.has_key('attempts'):
			self.attempts = data['attempts']
		if data.has_key('type'):
			self.type = data['type']
		if data.has_key('item_data'):
			self.item_data = data['item_data']
		if data.has_key('item_tasks_count'):
			self.item_tasks_count = data['item_tasks_count']
		
		if safe:
			self.save()
	
	def save(self):
		db.set('batch@id@%s@item@id%s@task@id@%s' % (self.batch_id, self.item_id, self.task_id), json.dumps({'status': self.status, 'url': self.url, 'url_order': self.url_order, 'image_meta': self.image_meta, 'attempts': self.attempts, 'type': self.type, 'item_data': self.item_data, 'item_tasks_count': self.item_tasks_count}))
	
	def increment_finished_item_tasks(self):
		if self.item_id != '':
			return db.incr('batch@id@%s@item@id%s' % (self.batch_id, self.item_id), 1)
