import sys
import argparse
import re








# Try to parse simple queries, to map then into selects from SQL. No so much
# complicated, but try to create it well.
#
# - three SQL ENTRIES.
#     TRACKS
#     PLACES
#     TRACK_IN_PLACES
#
#     examples
#
#         * navas del rey
#         * KANADIA
#         * MTB
#         * "this text goes together"
#         * DISTANCE>20Km
#         * ELEVATION<30m
#         * MTB and ELEVATION<30m or DISTANCE>10Km
#         * PASSES by PLACE
#
#         rules
#             by default, is parsed as text in the title of the TRACK. (select * where title like '%q%')
#             you need to specify class.attribute when generating things like filters.
#             things grouped by " " goes together.
#
#         if error, fails silently and don't return anything
#

# nested queries based on ID.
# places goes in another way
# 
# select id from tracks where id in (
# 
#     select id from tracks where distance< 20000 or id in (
#         select id from tracks where elevation > 1000
#         )
# 
# )


class TokenBase:
    def __init__(self, literal, opcode):
        self.literal = literal
        self.opcode = opcode
        
    def __repr__(self):
        return "T[%s]" % (self.literal)
        #return "TOKEN[%s,%s]" % (self.literal, self.opcode)

    def repr(self):
        return self.__repr__()

    def __str__(self):
        return self.repr()
    
    def __eq__(self, obj):
        return self.__class__ == obj
    

class TokenGE(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,">=", '__GE__')
        
class TokenLE(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,"<=", '__LE__')        
        
class TokenNE(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,"!=", '__NE__')           

class TokenScope(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,":", '__SCOPE__')           

class TokenSelector(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,".", '__SELECTOR__')           


class TokenLT(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,"<", '__LT__')  

class TokenGT(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,">", '__GT__')  

class TokenEQ(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,"=", '__EQ__')  

class TokenLP(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,"(", '__LP__')  

class TokenRP(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,")", '__RP__')  


class TokenLiteral(TokenBase):
    
    def __repr__(self):
        return "Tl[%s]" % (self.literal)
        
    def __init__(self, literal):
        TokenBase.__init__(self,literal, '__LITERAL__')

class TokenAND(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,"AND", '__AND__')    

class TokenOR(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,"OR", '__OR__')    
    
class TokenPLACE(TokenBase):
    def __init__(self):
        TokenBase.__init__(self,"PLACE", '__PLACE__')    

class TokenLIMIT(TokenBase):
    def __init__(self, literal):
        TokenBase.__init__(self, literal, '__LIMIT__')    

class TokenASC(TokenBase):
    def __init__(self):
        TokenBase.__init__(self, "ASC", '__ASC__')    

class TokenDESC(TokenBase):
    def __init__(self):
        TokenBase.__init__(self, "DESC", '__DESC__')    


########## syntax parsing (rules)




class ExpresionBase:
        def __init__(self):
            pass
        
        

            
            


class QueryParser:
    def __init__(self):
        self.is_places = False
        self.orderby = []
        
    def _tokenize(self, q):
        tokens = []
        intoken = False
        curtoken = ""
        j=0
        
        def _reserved_word(token):
        
         
            if token == TokenLiteral and token.literal.upper() == 'AND':
                return TokenAND()
    
            if token == TokenLiteral and token.literal.upper() == 'OR':
                return TokenOR()

            if token == TokenLiteral and token.literal.upper() == 'PLACE':
                return TokenPLACE()

            if token == TokenLiteral and token.literal.upper() == 'LIMIT':
                return TokenLIMIT("")
            
            if token == TokenLiteral and token.literal.upper() == 'ASC':
                return TokenASC()
            
            if token == TokenLiteral and token.literal.upper() == 'DESC':
                return TokenDESC()

            return token
        
        while j < len(q):
            i = q[j]
            
            if i.isspace() and not intoken:
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken)))
                    curtoken = ""
                j += 1
                continue

            if i == '"' and not intoken:
                intoken = True
                j += 1
                continue

            if i == '"' and intoken:
                intoken = False
                tokens.append( _reserved_word(TokenLiteral(curtoken)))
                curtoken = ""
                j += 1
                continue

            # operators and some mandanga.
            
            if i == '>' and j<len(q) and q[j+1] == '=':
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken))) 
                tokens.append( TokenGE() )
                curtoken = ""
                j += 2
                continue
            
            if i == '<' and j<len(q) and q[j+1] == '=':
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken))) 
                tokens.append( TokenLE() )
                curtoken = ""
                j += 2
                continue
            
            if i == '!' and j<len(q) and q[j+1] == '=':
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken))) 
                tokens.append( TokenNE() )
                curtoken = ""
                j += 2
                continue

            if i == ':':
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken)))
                tokens.append( TokenScope() )
                curtoken = ""
                j = j+1
                continue

            if i == '.':
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken)))
                tokens.append( TokenSelector() )
                curtoken = ""
                j = j+1
                continue

            if i == '<':
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken)))
                tokens.append( TokenLT() )
                curtoken = ""
                j = j+1
                continue

            if i == '>':
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken)))
                tokens.append( TokenGT() )
                curtoken = ""
                j = j+1
                continue

            if i == '=':
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken)))
                tokens.append( TokenEQ() )
                curtoken = ""
                j = j+1
                continue

            if i == '(':
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken)))
                tokens.append( TokenLP() )
                curtoken = ""
                j = j+1
                continue

            if i == ')':
                if curtoken != "":
                    tokens.append( _reserved_word(TokenLiteral(curtoken)))
                tokens.append( TokenRP() )
                curtoken = ""
                j = j+1
                continue            
            
            
            curtoken += i
            j += 1

        # trailing one

        if curtoken != "":
            tokens.append( _reserved_word(TokenLiteral(curtoken) ))

        return tokens


            
            
            
        
        

    def _expressions(self, tokenlist):
        
        r = []
        
        #
        # expressions are joined with AND, OR, ( and )
        # build the expressions, as [ TOKENLIST ] JOIN [ TOKENLIST ] ...
        # when JOIN is one of the AND, OR, (, )
        #
        expr = []
        for t in tokenlist:
            if t == TokenAND or t == TokenOR:
                r.append(expr)
                r.append([t])
                expr = []
            else:
                expr.append(t)
        
        if len(expr) > 0:
            r.append(expr)
            
        return r
    

            
        
    
 
                
    def _code(self, expressionlist):
        
        self.orderby = []
        LIMIT = None
        ORDER = None # ASC = 0, DESC = 1
        
        code = "select id from tracks where "
        r = []
        for e in expressionlist:
            attrs = []
            tables = []
            conditions = []
            orderby = []
            
            
            i = 0
            while i < len(e):
                t = e[i]
                if t == TokenAND:
                    r.append( TokenAND() )
                    break
                
                if t == TokenOR:
                    r.append( TokenOR() )
                    break
                
                if t == TokenLP:
                    r.append( TokenLP() )
                    break
                
                if t == TokenRP:
                    r.append( TokenRP() )
                    break
                
                # Literal:QueryString (check the tables)
                # for now just work for places.
                
                if t == TokenLiteral and i+2<len(e) and e[i+1] == TokenScope and e[i+2] == TokenLiteral:
                    
                    fname = 'title'
                    if t.literal.upper() == 'PLACES': 
                        fname = 'name'
                        self.is_places = True
                        r = "select id from PLACES where name like '%%%s%%'" % e[i+2].literal
                        return r, LIMIT, ORDER
                    
                        
                    if t.literal.upper() == 'TRACKS': 
                        fname = 'title'
                        return [], LIMIT, ORDER

                    i += 3
                    continue
                
                # Literal.attribute (add required table, t)
                if t == TokenLiteral and i+2<len(e) and e[i+1] == TokenSelector and e[i+2] == TokenLiteral:
                    
                    # mangle some attributes.
                    attr = e[i+2].literal
                    if attr.lower() == 'sport': attr = 'kind' 
                    if attr.lower() == 'with': attr = 'equipment'
                    
                    conditions.append( "%s.%s" % (t.literal, attr))
                    
                    
                    #self.orderby.append("%s.%s desc" % (t.literal, attr ))
                    self.orderby.append("%s.%s" % (t.literal, attr ))
                    
                    i += 3
                    continue
                
                if t in [ TokenGT, TokenLT, TokenEQ, TokenNE, TokenGE, TokenLE ] and i+1<len(e) and e[i+1] == TokenLiteral:
                    
                    # mangle some comparators
                    attr = e[i+1].literal
                    attrmap = [ 'run', 'mtb', 'road', 'trekking', 'duatlon', 'kayak', 'rodillo', 'trav' ]
                    
                    if attr.lower() in attrmap:
                        attr = "'%s'" % attr.upper()
                    
                    # map Km elements to the value.
                    if attr.lower().find('km') != -1:
                        tmpattr = attr.lower().replace('km','')
                        try:
                            tmpattr_f = float(tmpattr)
                            tmpattr_f *= 1000
                            tmpattr = "%3.3f" % tmpattr_f
                            attr = tmpattr
                        except:
                            pass
                    if attr.lower() in [ 'yes', 'true' ]: attr = "1"
                    if attr.lower() in [ 'no', 'false' ]: attr = "0"
                    
                    
                    conditions.append("%s %s" % (t.literal, attr))
                    i += 2
                    continue
                
                
                # LIMIT
                if t == TokenLIMIT and i+1<len(e) and e[i+1] == TokenLiteral:
                    
                    # mangle some comparators
                   
                    val = e[i+1].literal
                    
                    LIMIT = TokenLIMIT("%s" % val)
                    
                    i += 2
                    continue

                # ASC
                if t == TokenASC:
                    ORDER = TokenASC()
                    i+=1 

                # DESC
                if t == TokenDESC:
                    ORDER = TokenDESC()
                    i+=1 

                # PLACE xxx
                if t == TokenPLACE and i+1<len(e) and e[i+1] == TokenLiteral:
                    
                    q = "select track_in_places.id_track from track_in_places, places where track_in_places.id_place = places.id and places.name like '%%%s%%'" % (e[i+1].literal)
                    r.append( TokenLiteral(q))
                    i += 3
                    continue
                
                
                if t == TokenLiteral and len(e)==1:
                    q= "select tracks.id from tracks where title like '%%%s%%'" % (t.literal)
                    
                    r.append( TokenLiteral(q))
                    i+=1
                    continue
                
                if t == TokenLiteral and len(e)>1:
                    
                    attr = t.literal
                    if attr.lower() == 'sport': attr = 'kind' 
                    if attr.lower() == 'with': attr = 'equipment'
                    
                    conditions.append("tracks.%s" % attr)
                    i+=1
                    continue
                
                i += 1
                
            # build the query, add it to r.
            #if len(attrs) == 0: attrs = [ 'tracks.id' ]
            #if len(tables) == 0: tables = [ 'tracks' ]

                       
            attrs = list(set(attrs))
            tables = list(set(tables))
           
            
                    
            if conditions:
                q =   "SELECT id from TRACKS where " + ",".join(attrs)  
                q +=  " ".join(conditions)
                    
                r.append(TokenLiteral(q))
            
        
        return r, LIMIT, ORDER
        
        
        
    def _run_r(self,code):
        
        head,tail = code[0],code[1:]
        #print "head ", head
        #print "tail ", tail
        if tail == []:
            return head.literal

        msg = ""
        trail = ""
        if head in [ TokenAND, TokenOR, TokenLP, TokenRP ]:
            msg = " %s id in (" % head.literal
            trail = ')'
        else:
            msg = head.literal


        return msg + "" + self._run_r(tail) + trail
        
        
        
    def _runtracks(self ,code, limit, order):
     
        q = self._run_r(code);
        
        # do some adjusts here to force the cloned tracks.
        # by default, get only "original" tracks in search
        
           
        # order elements.
        self.orderby = list(set(self.orderby))        

        
        if order:
            self.orderby = map(lambda x: "%s %s" % (x, order.literal), self.orderby)
        
        if self.orderby:
            o = " order by " + ",".join(self.orderby)
            q += o

        if limit:
            q += " LIMIT %s" % limit.literal       
        
        #print q
        return { 'type': 'tracks', 'query': q }
            
    def _runplaces(self, code, limit, order):
   
        if limit:
            code += "LIMIT %s" % limit.literal
        
        if order:
            code += "%s" % order.literal
            
        return { 'type': 'places', 'query': code }
      

        

                 
        

    def Parse(self,query):
        #print "Query: [%s]" % query
        tokens = self._tokenize(query)

        #print "DEBUG_TOKENS: ", tokens
        expressions = self._expressions(tokens)
        #print "DEBUG EXPRESSIONS: "
        #for e in expressions: print e
        #print "-" * 80    
        # with the expressions, generate "code"
        
        code, limit,order = self._code(expressions)

       
        if self.is_places:
            retval = self._runplaces(code, limit, order)
        else:
            retval = self._runtracks(code, limit, order)

        return retval
    

if __name__ == "__main__":


    
    parser = argparse.ArgumentParser()

    #parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    #parser.add_argument("-c", "--create", help="Create the database", action="store_true")
    #parser.add_argument("-a", "--altitude", help="Create Altitude PNG")
    parser.add_argument("query", help="Query to parse")
    #parser.add_argument("dbfile", help="DatabaseFile")
    args = parser.parse_args()


    qparser = QueryParser()
    result = qparser.Parse(args.query)
    print(result)
    
