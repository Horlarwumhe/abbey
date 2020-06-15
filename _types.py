#subsclass python builting types to add more methods

class List(list):

	def lenght(self,*args):
		return self.__len__()

	def length(self,*args):
		return self.__len__()

class Dict(dict):

	def lenght(self,*args):
		return self.__len__()

	def length(self,*args):
		return self.__len__()

	def __getattr__(self,name):
		return self.get(name,'')

class String(str):

	def lenght(self,*args):
		return self.__len__()

	def length(self,*args):
		return self.__len__()

	def begins(self,name,*args):
		return self.startswith(name)

class Int(int):
	def tostring(self):
		return str(self)
	def lenght(self,*args):
		return len(str(self))

	def length(self,*args):
		return len(str(self))