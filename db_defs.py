from google.appengine.ext import ndb

class Item(ndb.Model):
    name = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    price = ndb.IntegerProperty(required=True)
    location = ndb.StringProperty(required=True)
    seller = ndb.StringProperty(required=True)
    
    def to_dict(self):
        d = super(Item, self).to_dict()
        d['key'] = self.key.id()
        return d

class Account(ndb.Model):
    email = ndb.StringProperty(required=True, indexed=True)
    password = ndb.StringProperty(required=True)
    nickname = ndb.StringProperty(required=True)
    
    # Items the user is selling
    items = ndb.StructuredProperty(Item, repeated=True)
    
    def to_dict(self):
        d = super(Account, self).to_dict()
        d['key'] = self.key.id()
        return d
   