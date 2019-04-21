
from grammar      import Grammar, Production
from aho_peterson import covering_grammar, minimum_distance_parse


if __name__ == '__main__':
	

	cfg = Grammar()

	# Nonterminal States

	cfg.nonterminals.append( 'S' )

	# Production Rules

	cfg.add_production( Production( 'S', ('(',')'        )  ) )
	cfg.add_production( Production( 'S', ('(',')','S'    )  ) )
	cfg.add_production( Production( 'S', ('(','S',')'    )  ) )
	cfg.add_production( Production( 'S', ('(','S',')','S')  ) )

	# Start State

	cfg.start = 'S'

	# Alphabet

	cfg.alphabet = list('()')

	# Source String

	x = "((("


	print( 'Original Grammar: \n' )

	print( cfg )

	print( '\n------------------------------------------------------------------------\n' )


	print( 'Covering Grammar: \n' )

	cover = covering_grammar(cfg, Wi = 1.0, Wr = 1.0, Wd = 1.0 ) # Set costs of each operation here

	print( cover )

	print( '\n------------------------------------------------------------------------\n' )


	print( f"Source String: {x}\n" )

	parse, k = minimum_distance_parse( cover, x )

	print( f"Edit Cost: {k}\n" )

	print( "Rightmost Derivation Productions:" )

	# Display Rightmost derivation of parse

	width = max( map( lambda i : len(str(i.production)), parse ) )

	for p in parse:

		print( str(p.production).ljust(width), f"  k_acc = {p.errors}" )