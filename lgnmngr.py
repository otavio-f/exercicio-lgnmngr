import os
import tkinter
from util import link, database

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

class edit_view(tkinter.Toplevel):
	"""classe view do editor de links"""
	def __init__(self, link_instance):
		"""Inicializa a classe com a instância de link."""
		tkinter.Toplevel.__init__(self)
		self.link = link_instance
		self.has_changes = False
		self.main_frame = tkinter.Frame(self)
		self.toolbar = tkinter.Frame(self)
		self.config_toolbar()
		self.config_main()
		self.focus_set()
		self.wait_window()

	def config_toolbar(self):
		"""Configura a barra de ferramentas."""
		'''icones'''
		self.ico_save = tkinter.PhotoImage(file=os.path.join("icons", "save.gif"))
		self.ico_cancel = tkinter.PhotoImage(file=os.path.join("icons", "cancel.gif"))
		tkinter.Button(self.toolbar, image=self.ico_save, command=self.done).pack(side=tkinter.TOP)
		tkinter.Button(self.toolbar, image=self.ico_cancel, command=self.cancel).pack(side=tkinter.BOTTOM)
		'''empacota no frame principal'''
		self.toolbar.pack(side=tkinter.RIGHT)
		
	def config_main(self):
		"""Configura o painel principal."""
		'''vars'''
		self.name_entry = tkinter.StringVar()
		self.login_entry = tkinter.StringVar()
		self.password_entry = tkinter.StringVar()
		self.description_entry = tkinter.StringVar()
		'''preencher vars com dados da instancia'''
		self.name_entry.set(self.link.name)
		self.login_entry.set(self.link.user)
		self.password_entry.set(self.link.password)
		self.description_entry.set(self.link.description)
		'''entradas'''
		tkinter.Label(self.main_frame, text="Nome")
		tkinter.Entry(self.main_frame, textvariable=self.name_entry).pack()
		tkinter.Entry(self.main_frame, textvariable=self.login_entry).pack()
		tkinter.Entry(self.main_frame, show="*", textvariable=self.password_entry).pack()
		tkinter.Entry(self.main_frame, textvariable=self.description_entry).pack()
		'''empacotar no frame principal'''
		self.main_frame.pack(side=tkinter.LEFT)

	def done(self):
		"""Finaliza a edição e salva os dados do formulário na instância ativa."""
		#TODO : ver depois, talvez refazer
		'''mudancas?'''
		self.has_changes = (self.link.name != self.name_entry.get()
			or self.link.user != self.login_entry.get()
			or self.link.password != self.password_entry.get()
			or self.link.description != self.description_entry.get())
		'''recuperar dados das vars, se mudados'''
		if(self.has_changes):
			self.link.name = self.name_entry.get()
			self.link.user = self.login_entry.get()
			self.link.password = self.password_entry.get()
			self.link.description = self.description_entry.get()
		'''finaliza a edicao'''
		self.destroy()

	def cancel(self):
		"""Cancela e finaliza a edição."""
		self.has_changes = False
		self.destroy()

class main_view(tkinter.Tk):
	"""Classe de vizualização."""
	def __init__(self, db_file):
		tkinter.Tk.__init__(self)
		self.control = control(db_file)
		self.main_frame = tkinter.Frame(self)
		self.toolbar = tkinter.Frame(self)
		'''procedimentos'''
		self.title("Meus Sites")
		self.protocol("WM_DELETE_WINDOW", self.quit)
		self.main_config()
		self.toolbar_config()
		self.mainloop()

	def main_config(self):
		"""Configura a janela principal."""
		self.listbox = tkinter.Listbox(self.main_frame, selectmode=tkinter.SINGLE)
		'''recuperar e preencher dados'''
		self.link_list = self.control.all
		for link in self.link_list:
			self.listbox.insert(tkinter.END, link.name)
		'''definir selecao para o primeiro'''
		try:
			self.listbox.select_set(0)
		except:
			pass
		'''clique duplo'''
		self.listbox.bind("<Double-Button-1>", lambda f:self.edit())
		'''empacotar'''
		self.listbox.pack(fill=tkinter.BOTH)
		self.main_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH)

	def toolbar_config(self):
		"""Configura a barra de ferramentas e ações de janela e teclado."""
		'''icones dos botoes (iconsdb)'''
		self.ico_new = tkinter.PhotoImage(file=os.path.join("icons","add.gif"))
		self.ico_edit = tkinter.PhotoImage(file=os.path.join("icons", "edit.gif"))
		self.ico_login = tkinter.PhotoImage(file=os.path.join("icons", "login.gif"))
		self.ico_password = tkinter.PhotoImage(file=os.path.join("icons", "password.gif"))
		'''botoes'''
		tkinter.Button(self.toolbar, image=self.ico_new, command=self.new).pack()
		'''se um item estiver selecionado, entao os botoes ficam disponiveis'''
		if len(self.listbox.curselection())>0:
			#tkinter.Button(self.toolbar, text="Editar", command=self.edit).pack()
			tkinter.Button(self.toolbar, image=self.ico_edit, command=self.edit).pack()
			tkinter.Button(self.toolbar, image=self.ico_login, command=self.copy_login).pack()
			tkinter.Button(self.toolbar, image=self.ico_password, command=self.copy_pass).pack()
		else:
			tkinter.Button(self.toolbar, image=self.ico_edit, state=tkinter.DISABLED).pack()
			tkinter.Button(self.toolbar, image=self.ico_login, state=tkinter.DISABLED).pack()
			tkinter.Button(self.toolbar, image=self.ico_password, state=tkinter.DISABLED).pack()
		'''empacotar'''
		self.toolbar.pack(side=tkinter.RIGHT)

	@property
	def active_link(self):
		'''Retorna o link equivalente a selecao na interface.'''
		index = self.listbox.curselection()[0]
		return self.link_list[index]

	def new(self):
		"""Cria e salva um novo item."""
		editpanel = edit_view(link())
		self.control.save(editpanel.link)
		self.refresh()

	def edit(self):
		"""Edita um item."""
		editpanel = edit_view(self.active_link)
		if editpanel.has_changes:
			'''if has changed, then save it'''
			self.control.save(editpanel.link)
			self.refresh()

	def copy_login(self):
		"""Copia o login do item selecionado para a área de transferência."""
		self.clipboard_clear()
		self.clipboard_append(self.active_link.user)
		self.update()

	def copy_pass(self):
		"""Copia a senha do link selecionado para a área de transferência."""
		self.clipboard_clear()
		self.clipboard_append(self.active_link.password)
		self.update()

	def quit(self):
		"""Encerra o aplicativo."""
		self.control.quit()
		self.destroy()

	def refresh(self):
		"""Recarrega a tela inicial."""
		'''Destruir'''
		self.main_frame.destroy()
		self.toolbar.destroy()
		'''Reconstruir'''
		self.main_frame = tkinter.Frame(self)
		self.toolbar = tkinter.Frame(self)
		'''Reconfigurar'''
		self.main_config()
		self.toolbar_config()

if __name__=="__main__":
	DB_FILE = "db.db"
	main_view(DB_FILE)