
from grammar import Grammar, Production

from collections import deque

default_alphabet = list( "abcdefghijklmnopqrstuvwxyz0123456789 _()" )


# Earley Items (with added error cost)

class Item:

    __slots__ = (
        'nonterminal',
        'production',
        'dot_position',
        'origin',
        'errors',
        'pointers'
    )

    def __init__( self, production, dot_position, origin, errors, pointers = None ):

        self.production   = production
        self.dot_position = dot_position
        self.origin       = origin
        self.errors       = errors
        self.pointers     = pointers if pointers != None else []

    def finished( self ):

        return self.dot_position >= len( self.production.right )
    
    def next_symbol( self ):

        if self.finished():

            return None

        return self.production.right[ self.dot_position ]

    def tail( self ):

        return self.production.right[ : self.dot_position ]

    def bump_state( self, cost = 0 ):

        return Item (
            self.production, 
            self.dot_position+1, 
            self.origin,
            self.errors + cost
        )
    
    def to_string( self, show_pointers = True ):

        ret = f'{self.production.left} -> '

        for i, tok in enumerate( self.production.right ):

            if i == self.dot_position:

                ret += ' . '

            ret += f' {tok} '

        if self.dot_position == len( self.production.right ):

            ret += ' . '

        if show_pointers:
        
            return f'{ret}   ({self.origin}) (k={self.errors})  ~~ {"|".join( map( lambda p : p.to_string(False), self.pointers ) )}'
                
        return ret + f'   ({self.origin}) (k={self.errors})'

    __repr__ = __str__ = lambda s : s.to_string( True )


# ----- Algorithm 1 - Error Productions -----

def covering_grammar( grammar, Wi = 1.0, Wr = 1.0, Wd = 1.0 ):

    alphabet = grammar.alphabet if grammar.alphabet != None else default_alphabet

    productions = [ ]

    nonterminals = [ n for n in grammar.nonterminals ]

    # - A1.2

    H = 'H'
    while H in nonterminals: 
        H += '\''
    nonterminals.append( H )

    I = 'I'
    while I in nonterminals:
        I += '\''
    nonterminals.append( I )

    E = {}

    for a in alphabet:

        Ea = f'E_{a}'
        while Ea in nonterminals: 
            Ea += '\''
        E[a] = Ea
        nonterminals.append( Ea )

        for b in alphabet:
            
            if a == b:
                productions.append( Production( Ea, [b] ) )
            else:
                productions.append( Production( Ea, [b], Wr ) )

        productions.append( Production( Ea, [H,a]     ) )
        productions.append( Production( I,  [ a ], Wi ) )
        productions.append( Production( Ea, [   ], Wd ) )

    # - A1.3
    
    start = 'S'
    while start in nonterminals:
        start += '\''
    nonterminals.append( start )

    productions.append( Production( start, [grammar.start] ) )

    productions.append( Production( start, [grammar.start, H] ) )

    productions.append( Production( H, [H, I] ) )

    productions.append( Production( H, [I] ) )

    # - A1.1

    for production in grammar.productions:

        alpha_runs = []
        beta_items = []

        curr_run  = []

        for item in production.right:

            if item in alphabet:
                alpha_runs.append( curr_run )
                beta_items.append( item     )
                curr_run = []
            else:
                curr_run.append( item )

        alpha_runs.append( curr_run )

        new_rhs = []
        for i in range( len( beta_items ) ):
            
            new_rhs += alpha_runs[i]
            new_rhs.append( E[beta_items[i]] )

        new_rhs += alpha_runs[-1]

        productions.append( Production( production.left, new_rhs ) )

    return Grammar( nonterminals, start, productions, alphabet )


def minimum_distance_parse( G, x ):

    # ----- Algorithm 2 - Minimum Distance Parser -----

    # - Initial Conditions

    n = len( x )

    l = [ [] for _ in range( n+1 ) ]

    # - A2.1

    for start_production in G.productions_from[G.start]:

        l[0].append( Item( start_production, 0, 0, 0 ) )

    # - A2.4

    q = deque( l[0] )

    while q:

        item = q.pop()
        
        # - A2.2

        B = item.next_symbol()

        if B != [] and B in G.nonterminals:

            for b_prod in G.productions_from[ B ]:

                new_item = Item( b_prod, 0, 0, 0 )

                skip = False
                for i in l[0]:

                    if ( i.production   == new_item.production   and 
                         i.dot_position == new_item.dot_position and
                         new_item.errors <= i.errors ):

                        skip = True

                if not skip:

                    l[0].append( new_item )
                    q   .append( new_item )

        # - A2.3

        for item2 in l[0]:

            # Note: We need to check if item  matches either side of the search

            if B == item2.production.left and item2.finished():

                new_item = item.bump_state( item2.production.cost )
                new_item.errors += item2.errors

                new_item.pointers.append( item  )
                new_item.pointers.append( item2 )

            elif item2.next_symbol() == item.production.left and item.finished():

                new_item = item2.bump_state( item.production.cost )
                new_item.errors += item.errors

                new_item.pointers.append( item2 )
                new_item.pointers.append( item )

            else:

                continue

            skip = False
            for i in l[0]:

                if ( i.production   == new_item.production   and 
                     i.dot_position == new_item.dot_position and 
                     i.origin       == new_item.origin ):
                   
                    if i.errors <= new_item.errors:
                        skip = True
                    else:
                        l[0].remove( i )
                    break

            if not skip:

                l[0].append( new_item )
                q   .append( new_item )

    # Construct remaining lists inductively

    for j in range(1,n+1):

        # - A2.5

        for item in l[j-1]:

            if item.next_symbol() == x[j-1]:

                new_item = item.bump_state( 0 )
                new_item.pointers.append( item  )
                l[j].append( new_item )

        # - A2.8:

        q = deque( l[j] )

        while q:
            
            item = q.pop()

            # - A2.6

            for item2 in l[item.origin]:

                if item.finished() and item.production.left == item2.next_symbol():

                    new_item = item2.bump_state( item.production.cost )
                    new_item.errors += item.errors

                    new_item.pointers.append( item2 )
                    new_item.pointers.append( item  )

                else:

                    continue

                skip = False
                for i in l[j]:

                    if ( i.production   == new_item.production   and 
                         i.dot_position == new_item.dot_position and 
                         i.origin       == new_item.origin ):
                       
                        if i.errors <= new_item.errors:
                            skip = True
                        else:
                            l[j].remove( i )
                        break

                if not skip:

                    l[j].append( new_item )
                    q   .append( new_item )

            # - A2.7

            if not item.finished():

                sym = item.next_symbol()

                if sym in G.nonterminals:
                
                    for production in G.productions_from[ sym ]:

                        new_item = Item( production, 0, j, 0 )

                        if not any( ( x.production   == production and 
                                      x.dot_position == 0 and 
                                      x.origin == j and 
                                      x.errors == 0 ) for x in l[j] ):

                            l[j].append( new_item )
                            q   .append( new_item )

    # ----- Algorithm 3 - Backpointer Network Tracing -----

    # - A3.0

    best_pick = None

    for item in l[n]:

        if item.origin == 0 and item.production.left == G.start and item.finished():

            if best_pick == None or item.errors < best_pick.errors:

                best_pick = item

    pi = []

    def parse_helper( item, j ):

        # - A3.1

        if item.finished():

            pi.append( item )

        # - A3.2

        if item.dot_position != 0:

            # A3.2a

            if item.tail()[-1] in G.alphabet:

                parse_helper( item.pointers[0], j-1 )

            # A3.2b

            else:

                for pointer in item.pointers:

                    if pointer.finished():

                        pointer1 = pointer

                    else:

                        pointer2 = pointer
                
                parse_helper( pointer1, j )
                parse_helper( pointer2, pointer1.origin )


    parse_helper( best_pick, n )

    return pi, best_pick.errors

