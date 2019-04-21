

class Production:

	__slots__ = ('left','right','cost')

	def __init__( self, left, right, cost = 0.0 ):

		self.left  = left
		self.right = right
		self.cost  = cost

	def __str__( self ):

		return f'{self.left} -> {self.right}'




class Grammar ( ):

	def __init__( self, nonterminals = None, start = None, productions = None, alphabet = None ):

		self.nonterminals = nonterminals if nonterminals != None else []
		self.start        = start
		self.productions  = productions  if productions  != None else []
		self.alphabet     = alphabet

		self.productions_from = {}

		for n in self.nonterminals:

			self.productions_from[n] = []

		for p in self.productions:

			self.productions_from[p.left].append( p )


	def add_production( self, production ):

		self.productions.append( production )

		if production.left not in self.productions_from:

			self.productions_from[production.left] = []

		self.productions_from[production.left].append( production )


	def __str__( self ):

		ret  = f'N := {", ".join( self.nonterminals) }\n\n'
		ret += f'S := {self.start}\n\nP:=\n'
		ret += '\n'.join( map( lambda p : f'  {str(p)}', self.productions ) )
		
		return ret
