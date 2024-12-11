
from lark import Lark, tree, Token
from lark import Transformer
import re


class SQLQueryTransformer(Transformer):
    def __init__(self, get="id", limit=None, offset=None, xlate_table=[]):
        self.get = get
        self.limit = limit
        self.offset = offset
        self.xlate_table = xlate_table

    def _xlate(self, attr):
        """translate the table names if found, else none.

        Args:
            attr (_type_): _description_

        Returns:
            _type_: _description_
        """
        if attr.lower() in self.xlate_table:
            r = self.xlate_table[attr.lower()]
        else:
            r = attr
        return r
    
    def title_expression(self, items):
        
        data = re.sub(r"[\"']",'',items[0])
        return("searchname like '%%%s%%'"  % data)

    def sport_expression(self, items):
        return("kind = %s" % items[0])
    
    def equipment_expression(self, items):
        return("equipment = %s" % items[0])

    def device_expression(self, items):
        return("device = %s" % items[0])
            
    def custom_expression(self, items):
        return("%s" % items[0])

    def bool_expression(self, items):
        return items[0]

    def timestamp_expression(self, items):
        return items[0]

    def date_func(self, items):
        
        if len(items) >= 2:
            args = " ,".join(items[1:])
            return "date(%s,%s)" % (items[0],args)
     
        return "date('%s')" % items[0]

    def datetime_func(self, items):
        
        if len(items) >= 3:
            args = " ,".join(items[2:])
            return "datetime('%s %s',%s)" % (items[0],items[1], args)
     
        return "datetime('%s %s')" % (items[0],items[1])


    def trackdate_func(self, items):
        
        if len(items) > 0:
            args = " ,".join(items)
            return "date(stamp,'unixepoch',%s)" % args
        return "date(stamp,'unixepoch')" 
    
    def tracktime_func(self, items):
        
        if len(items) > 0:
            args = " ,".join(items)
            return "time(stamp,'unixepoch',%s)" % args
        return "time(stamp,'unixepoch')" 

    def trackdatetime_func(self, items):
        
        if len(items) > 0:
            args = " ,".join(items)
            return "datetime(stamp,'unixepoch',%s)" % args
        return "datetime(stamp,'unixepoch')" 

    def time_func(self, items):
        if len(items) >= 2:
            args = " ,".join(items[1:])
            return "time(%s,%s)" % (items[0],args)
         
        return "time(%s)" % items[0]


     


    def date_today(self, items):
        if len(items):
            args = " ,".join(items)
            return "date('now', %s)" % args

        return "date('now')"


    def NUMBER(self, items):
        return "%3.2f" % float(items)

    def number(self, items):
        return items[0]

    def name(self, items):
        return items[0]
    
    def date(self, items):
        # YYYY-DD-MM
        return "%s-%s-%s" % (items[0],items[1],items[2])
    
    def time(self, items):
        # HH:MM;SS
        return "%s:%s:%s" % (items[0],items[1],items[2])

    def equals(self, items):
        return "%s = %s" % (items[0], items[1])
    
    def not_equals(self, items):
        return "%s != %s" % (items[0], items[1])

    def greater_than(self, items):
        return "%s > %s" % (items[0], items[1])

    def less_than(self, items):
        return "%s < %s" % (items[0], items[1])
    
    def greater_than_or_equal(self, items):
        return "%s >= %s" % (items[0], items[1])

    def less_than_or_equal(self, items):
        return "%s <= %s" % (items[0], items[1])

    def between(self, items):
        return "%s between %s and %s" % (items[0], items[1], items[2])

    def is_null(self, items):
        return "%s is null" % (items[0])

    def is_not_null(self, items):
        return "%s is not null" % (items[0])

    def comparison_type(self, items):
        return items[0]
    
    def number_with_prefix(self, items):
        if len(items) == 1:
            return items[0]
        return float(items[0])*items[1]
    
    def km_prefix(self, items):
        return 1000.0
    
    def order_asc(self, items):
        return "%s ASC" % self._xlate(items[0])

    def order_desc(self, items):
        return "%s DESC" % self._xlate(items[0])

    def order_by_expression(self, items):
        return "".join(items)

    def m_prefix(self, items):
        return 1

    def integer_(self, items):
        return int(items[0].value)

    def comparison_type(self, items):
        return items[0]
    
    def bool_parentheses(self, items):
        return items[0]

    def bool_or(self, items):
        return "%s or %s" % (items[0], items[1])

    def bool_and(self, items):
        return "%s and %s" % (items[0], items[1])    

    def column_name(self, items):
        # do some translations.

        r = self._xlate(items[0])
        return "%s" % r

    def CNAME(self, items):
        return items.value

    def string(self, items):
        return items[0].value

    def limit_count(self, items):
        if len(items) == 1:
            return "limit %d" % int(items[0])

    def skip_rows(self, items):
        if len(items) == 1:
            return "offset %d" % int(items[0])

    def custom_sport(self, items):
        return "'%s'" % re.sub(r"[\"']",'',items[0].value)
        
    def custom_device(self, items):
        return "'%s'" % re.sub(r"[\"']",'',items[0].value)

    def custom_equipment(self, items):
        return "'%s'" % re.sub(r"[\"']",'',items[0].value)        
    

    def select(self, items):
        
        s = "select %s from tracks where %s" % (self.get, items[0])
        items.pop(0)
        if items[0] is None:
            items.pop(0)
            order = ""
        else:
            # asc or desc
            order = []
            while True:
                if items[0].lower().endswith(" desc") or items[0].lower().endswith(" asc"):
                    order.append(items[0])
                    items.pop(0)
                    if items[0] is None: 
                        break
                else:
                    break
            order = "order by " + ", ".join(order)
        
        s = "%s %s" % (s, order)

        # limit and offset
        if self.limit or self.offset:
            if self.limit:
                s += " limit %d" % self.limit
            if self.offset:
                s += " offset %d" % self.offset
        else:
            # don't override the query if found
            for i in items:
                if i is not None:
                    s += " %s" % i

        return s



class QueryParser:
    # https://github.com/zbrookle/sql_to_ibis/blob/main/sql_to_ibis/grammar/sql.lark
    #regex_lit             : /\/((?:.(?!(?<![\\\\])\/))*.?)\//
    #string_lit            : /'((?:.(?!(?<![\\\\])'))*.?)'/
    #QUOTED_IDENTIFIER     : /"((?:.(?!(?<![\\\\])"))*.?)"/

    grammar = """

    select                  : bool_expression [ "ORDER"i "BY"i (order_by_expr ",")*  order_by_expr] [ "LIMIT"i limit_count [ "OFFSET"i skip_rows ] ]

    order_by_expr           : order -> order_by_expression

    order                   : (name) ["ASC"i] -> order_asc
                            | (name) "DESC"i -> order_desc

    limit_count             : integer_ -> limit_count
    skip_rows               : integer_

    custom_expression       : title_expression 
                            | sport_expression
                            | equipment_expression
                            | device_expression

    title_expression        : "TITLE"i string_term
    sport_expression        : "SPORT"i custom_sports
    equipment_expression    : "EQUIPMENT"i custom_equipment
    device_expression       : "DEVICE"i custom_device

    bool_expression         : bool_parentheses
                            | custom_expression
                            | bool_expression "AND"i bool_parentheses -> bool_and
                            | bool_expression "OR"i bool_parentheses -> bool_or

    bool_parentheses        : comparison_type
                            | "(" bool_expression "AND"i comparison_type ")" -> bool_and
                            | "(" bool_expression "OR"i comparison_type ")" -> bool_or

    comparison_type         : equals 
                            | not_equals 
                            | greater_than 
                            | less_than 
                            | greater_than_or_equal
                            | less_than_or_equal 
                            | between 
                            | is_null 
                            | is_not_null

    equals                  : expression "=" expression
    not_equals              : expression ("<>" | "!=") expression
    greater_than            : expression ">" expression
    less_than               : expression "<" expression
    greater_than_or_equal   : expression ">=" expression
    less_than_or_equal      : expression "<=" expression
    between                 : expression "BETWEEN"i expression "AND"i expression
    is_null                 : expression "is"i "null"i
    is_not_null             : expression "is"i "not"i "null"i

    string_term             : ESCAPED_STRING -> string
                            | /'((?:.(?!(?<![\\\\])'))*.?)'/ -> string

    ?expression             : (name) -> column_name
                            | literal
                            | "TRACK_DATETIME"i "("  ( date_param ",")*  date_param? ")" -> trackdatetime_func
                            | "TRACK_DATE"i "("  ( date_param ",")*  date_param? ")" -> trackdate_func
                            | "TRACK_TIME"i "("  ( date_param ",")*  date_param? ")" -> tracktime_func
                            | "DATE"i "(" (name| "'" date "'") ("," date_param )*  ")" -> date_func
                            | "TIME"i "(" (name| "'" time "'") ("," date_param )*  ")" -> time_func
                            | "DATETIME"i "(" (name| "'" date time "'") ("," date_param )*  ")" -> datetime_func
                            
    ?literal                : boolean -> bool
                            | number_expr -> number
                            | /'([^']|\s)+'|''/ -> string
                            | ESCAPED_STRING -> string
                            | timestamp_expression -> timestamp_expression

    date_param              : /'([^']|\s)+'|''/ -> string
                            | ESCAPED_STRING -> string

    custom_sports           : /['"]?BIKE['"]?/i -> custom_sport
                            | /['"]?RUN['"]?/i -> custom_sport
                            | /['"]?MTB['"]?/i -> custom_sport
                            | /['"]?ROAD['"]?/i -> custom_sport
                            | /['"]?TREKKING['"]?/i -> custom_sport
                            | /['"]?KAYAK['"]?/i -> custom_sport

    custom_equipment        : /['"]?RASE23['"]?/i  -> custom_equipment
                            | /['"]?RASE24['"]?/i -> custom_equipment

    custom_device           : /['"]?FENIX3['"]?/i  -> custom_device
                            | /['"]?EDGE1000['"]?/i  -> custom_device



    boolean                 : "true"i -> true
                            | "false"i -> false

    ?number_expr            : product

    ?product                : number_with_prefix

    number_with_prefix      : NUMBER
                            | NUMBER number_prefix

    integer_                : /[1-9][0-9]*/
    number_prefix           : "km"i -> km_prefix
                            | "m"i -> m_prefix

    timestamp_expression    : "NOW"i "(" ( date_param ",")*  date_param? ")" -> date_today
                            | "TODAY"i "(" ( date_param ",")*  date_param? ")" -> date_today

    date                    : YEAR "-" MONTH "-" DAY
    YEAR                    : /[0-9]{4}/
    MONTH                   : /[0-9]{2}/
    DAY                     : /[0-9]{2}/
    time                    : HOURS ":" MINUTES ":" SECONDS
    HOURS                   : /[0-9]{2}/
    MINUTES                 : /[0-9]{2}/
    SECONDS                 : /[0-9]{2}/
    name                    : CNAME 
                           

    %import common.ESCAPED_STRING
    %import common.CNAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
    """

    def __init__(self, get_attr="id", limit=None, offset=None, verbose=False):
        
        self.get_attr = get_attr
        self.limit = limit
        self.offset = offset
        self.verbose = verbose

        self.xlate_table = {
            'length': 'length_2d',
            'distance': 'length_2d',
            'altitude': 'uphill_climb',
            'elevation': 'uphill_climb',
            'title': 'searchname',
            'name': 'searchname',
            'sport': 'kind',
        }
        
        self.parser = Lark(self.grammar, strict=True, start='select', ambiguity='explicit')
        self.transformer = SQLQueryTransformer(get=self.get_attr, 
                                               limit=self.limit, 
                                               offset=offset, 
                                               xlate_table=self.xlate_table)
       

    def run(self, query):
        try:
           
            data = self.parser.parse(query)
            if self.verbose:
                print(data.pretty())
            result = self.transformer.transform(data)
        except Exception as e:
            return ( False, e)
    
        return (True, result)





if __name__ == "__main__":
    import sqlite3
    parser = QueryParser(get_attr="id", limit=10, offset=0)

    sentences = []

    # sentences.append('title "navas del rey"')
    # sentences.append("title 'navas del rey'")
    sentences.append('sport \'BIKE\'')
    sentences.append('sport "BIKE"')
    sentences.append('sport BIKE')
    sentences.append('sport RUN order by length')
    sentences.append('device FENIX3 order by length')
    
    sentences.append('distance > 100 or kind = "run"')
    sentences.append('distance between 100 and 200')
    sentences.append('distance >= 100 or length_2d <= 100 or elevation is null')
    sentences.append('(length_2d > 20000.0 and distance < 1000 KM) or stamp = NOW()')
    sentences.append('(length_2d > 20000.0 and distance < 1000 KM) or DATE(stamp) = TODAY()')
    sentences.append('sport "BIKE"')
    sentences.append('title "navas del rey" and elevation > 30')
    sentences.append('(kind = "xxx" or kind = "run")')
    sentences.append('sport BIKE and ELEVATION<30m or DISTANCE>10Km')
    sentences.append('sport BIKE and ELEVATION<30m or DISTANCE>10Km limit 10 offset 5')
    sentences.append('sport BIKE and ELEVATION<30m or DISTANCE>10Km order by stamp, length_2d desc, stamp asc limit 10 offset 5')
    sentences.append('this is an error')

    for s in sentences:
    
        db = sqlite3.connect("../db/trackdb.db", check_same_thread=False)
        db.row_factory = sqlite3.Row
    
        result, sql = parser.run(s)
        print("-" * 80)
        print(s)
        print(sql)
        if result:
            cursor = db.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
            data = map(lambda x: dict(x), data)
            for i in data:
                pprint(i)
        print("-" * 80)
        # make_png(sys.argv[1])
        # make_dot(sys.argv[1])