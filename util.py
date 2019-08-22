import sqlite3

class link(object):
	"""Classe Modelo, com nome, descrição, status, senha e usuário."""
	def __init__(self, id=None, name="", user="", password="", description=""):
		self.id = id
		self.name = name
		self.description = description
		self.password = password
		self.user = user

	@property
	def id(self):
		return self._id
	
	@id.setter
	def id(self, id_num):
		"""Altera o id do link"""
		if id_num is None:
			'''None: novo item'''
			self._id = None
		elif id_num>0:
			'''> 0: existente'''
			self._id = id_num

	def __str__(self):
		"""Retorna o objeto em forma de texto."""
		return "|||{NAME}:{ID}\n{PASSW}:{USER}\n{DESC}\n|||".format(NAME=self.name, ID=self.id, PASSW=self.password, USER=self.user, DESC=self.description)

	def __eq__(self, other):
		"""Compara o objeto com outro e retorna True se os dois forem iguais ou False se diferentes."""
		if isinstance(other, link):
			return (other.id==self.id
					and other.name==self.name
					and other.password==self.password
					and other.user==self.user
					and other.desc==self.desc)
		
	def __ne__(self, other):
		"""Compara o objeto com outro e retorna True se os dois forem diferentes ou False se iguais."""
		return not self.__eq__(other)

class database(object):
	"""Classe de DAO. Executa funções sobre a base de dados contida em um arquivo."""
	def __init__(self, filename):
		self.file = filename
		self._is_connected = False
		self.initialize()

	@property
	def _cursor(self):
		"""Retorna o cursor do sqlite."""
		if not self._is_connected:
			self.connect()
		return self._ecursor

	def connect(self):
		"""Conecta com a base de dados."""
		self._connection = sqlite3.connect(self.file)
		self._ecursor = self._connection.cursor()
		self._is_connected = True

	def initialize(self):
		"""Inicializa o esquema de tabelas da base."""
		self._cursor.execute('''CREATE TABLE IF NOT EXISTS links(
							id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
							name TEXT NOT NULL,
							user TEXT NOT NULL,
							password TEXT NOT NULL,
							description TEXT
							);''')

	def commit_and_close(self):
		"""Salva as alterações na base de dados e enceerra a conexão."""
		self._connection.commit()
		self._connection.close()
		self.connected = False
		
	def add_or_replace_one(self, link_instance):
		"""Adiciona ou altera uma entrada na base de dados."""
		self._cursor.execute("INSERT OR REPLACE INTO links VALUES (?,?,?,?,?);",
							 (link_instance.id, link_instance.name, link_instance.user, link_instance.password, link_instance.description))

	def get_one_by_id(self, link_id):
		"""Recupera um item da base de dados a partir de um id numérico. Retorna uma instância de link."""
		self._cursor.execute("SELECT id,name,user,password,description FROM links WHERE id=?;", (link_id,)) #Sim, 2o arg é uma tupla.
		link_repr = self._cursor.fetchone()
		link_generated = link(id=link_repr[0], name=link_repr[1], user=link_repr[2], password=link_repr[3], description=link_repr[4])
		return link_generated
	
	def get_all(self):
		"""Recupera todas as entradas da base de dados. Retorna uma lista contendo links."""
		link_list = []
		for link_repr in self._cursor.execute("SELECT id,name,user,password,description FROM links;"):
			link_list.append(link(id=link_repr[0], name=link_repr[1], user=link_repr[2], password=link_repr[3], description=link_repr[4]))
		return link_list

	def delete_one_by_id(self, link_id):
		"""Remove uma entrada da base de dados a partir de um id numérico."""
		self._cursor.execute("DELETE FROM links WHERE id=?;", (link_id,)) #2o arg é uma tupla

	def delete_one(self, link_obj):
		"""Remove uma entrada da base de dados a partir de um objeto."""
		self.delete_one_by_id(link_obj.id)
		
	def wipe(self):
		"""Destroi a tabela, limpa os registros e otimiza o tamanho do arquivo."""
		self._cursor.execute("DROP TABLE links;")
		self._cursor.execute("VACUUM;")
		self.initialize()


class control(object):
	"""Classe responsável pela interface entre a view e a base de dados."""
	def __init__(self, db_file):
		"""Inicia uma conexão com uma base de dados contida no arquivo."""
		self.db = database(db_file)

	@property
	def all(self):
		"""Retorna todos os elementos contidos na base de dados."""
		return self.db.get_all()

	def one(self, id):
		"""Retorna um elemento cujo id corresponda ao informado."""
		return self.db.get_one_by_id(id)
	
	def save(self, link_instance):
		"""Salva uma instância na base de dados."""
		self.db.add_or_replace_one(link_instance)

	def delete(self, link_instance):
		"""Remove uma instância da base de dados."""
		self.db.delete_one_by_id(link_instance.id)

	def quit(self):
		"""Finaliza as transações com a base de dados."""
		self.db.commit_and_close()
