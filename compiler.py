""" [Ghazal Ahanjan, Ali Golmohammadi] [400104772, 400105206] پروژه کامپایلر """

import sys
from enum import Enum ,auto

class TokenType (Enum ):
    NUM =auto ()
    ID =auto ()
    KEYWORD =auto ()
    SYMBOL =auto ()
    COMMENT =auto ()
    WHITESPACE =auto ()

class Scanner :

    KEYWORDS ={
    'if','else','void','int','while','break',
    'return','goto','switch','case','default','for'
    }

    SINGLE_CHAR_SYMBOLS ={
    ';',':',',','[',']','(',')','{','}',
    '+','-','*','<'
    }

    ID_START =set ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    ID_CHAR =set ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')

    DIGITS =set ('0123456789')

    WHITESPACE_CHARS ={' ','\n','\r','\t','\v','\f'}

    def __init__ (self ,input_file ='input.txt'):
        self .input_file =input_file
        self .source_code =""
        self .position =0
        self .line_number =1
        self .tokens =[]
        self .lexical_errors =[]
        self .symbol_table ={}
        self .next_symbol_index =1

        keyword_order =[
        'break','else','for','if','int','return','void',
        'goto','switch','case','default','while'
        ]
        for keyword in keyword_order :
            if keyword in self .KEYWORDS :
                self ._add_to_symbol_table (keyword )

    def _add_to_symbol_table (self ,lexeme ):
        if lexeme not in self .symbol_table :
            self .symbol_table [lexeme ]=self .next_symbol_index
            self .next_symbol_index +=1
        return self .symbol_table [lexeme ]

    def read_input (self ):
        try :
            with open (self .input_file ,'r',encoding ='utf-8')as file :
                self .source_code =file .read ()
        except FileNotFoundError :
            print (f"Error: Input file '{self .input_file }' not found.")
            sys .exit (1 )
        except Exception as e :
            print (f"Error reading input file: {e }")
            sys .exit (1 )

    def get_current_char (self ):
        if self .position <len (self .source_code ):
            return self .source_code [self .position ]
        return None

    def advance (self ):
        if self .position <len (self .source_code ):
            char =self .source_code [self .position ]
            self .position +=1
            if char =='\n':
                self .line_number +=1
            return char
        return None

    def is_separator (self ,char ):
        if char is None :
            return True
        if char in self .WHITESPACE_CHARS :
            return True
        if char in self .SINGLE_CHAR_SYMBOLS :
            return True
        if char in {'/','*','='}:
            return True
        return False

    def can_start_token (self ,char ):
        if char is None :
            return False
        if char in self .DIGITS :
            return True
        if char in self .ID_START :
            return True
        if char in self .SINGLE_CHAR_SYMBOLS :
            return True
        if char in {'/','*','='}:
            return True
        return False

    def scan_token (self ):
        while self .position <len (self .source_code ):
            current =self .get_current_char ()
            token_line =self .line_number

            if current in self .WHITESPACE_CHARS :
                self .advance ()
                continue

            if current in self .DIGITS :
                return self ._scan_number ()

            if current in self .ID_START :
                return self ._scan_identifier_or_keyword ()

            if current =='/':
                return self ._handle_slash ()

            if current =='*':
                return self ._handle_star ()

            if current =='=':
                return self ._handle_equal ()

            if current in self .SINGLE_CHAR_SYMBOLS :
                self .advance ()
                return (token_line ,TokenType .SYMBOL ,current )

            return self ._handle_invalid_start ()

        return None

    def _scan_number (self ):
        lexeme =[]
        token_line =self .line_number

        while self .position <len (self .source_code ):
            current =self .get_current_char ()
            if current in self .DIGITS :
                lexeme .append (self .advance ())
            else :
                break

        num_str =''.join (lexeme )

        if len (num_str )>1 and num_str [0 ]=='0':

            if self .position <len (self .source_code ):
                next_char =self .get_current_char ()
                if next_char in self .ID_START or next_char =='_':
                    lexeme .append (self .advance ())
                    while self .position <len (self .source_code ):
                        current =self .get_current_char ()
                        if current in self .ID_CHAR :
                            lexeme .append (self .advance ())
                        else :
                            break

            error_str =''.join (lexeme )
            self .lexical_errors .append ({
            'line':token_line ,
            'text':error_str ,
            'message':'Invalid number'
            })
            return None

        if self .position <len (self .source_code ):
            next_char =self .get_current_char ()
            if next_char in self .ID_START or next_char =='_':

                lexeme .append (self .advance ())

                while self .position <len (self .source_code ):
                    current =self .get_current_char ()
                    if current in self .ID_CHAR :
                        lexeme .append (self .advance ())
                    else :
                        break

                error_str =''.join (lexeme )
                self .lexical_errors .append ({
                'line':token_line ,
                'text':error_str ,
                'message':'Invalid number'
                })
                return None

        return (token_line ,TokenType .NUM ,num_str )

    def _scan_identifier_or_keyword (self ):
        lexeme =[]
        token_line =self .line_number

        while self .position <len (self .source_code ):
            current =self .get_current_char ()
            if current in self .ID_CHAR :
                lexeme .append (self .advance ())
            else :
                break

        ident_str =''.join (lexeme )

        if self .position <len (self .source_code ):
            current =self .get_current_char ()

            if not self .is_separator (current ):

                lexeme .append (self .advance ())

                while self .position <len (self .source_code ):
                    current =self .get_current_char ()
                    if self .is_separator (current ):
                        break
                    lexeme .append (self .advance ())

                error_str =''.join (lexeme )
                self .lexical_errors .append ({
                'line':token_line ,
                'text':error_str ,
                'message':'Invalid input'
                })
                return None

        if ident_str in self .KEYWORDS :
            token_type =TokenType .KEYWORD
        else :
            token_type =TokenType .ID

        self ._add_to_symbol_table (ident_str )

        return (token_line ,token_type ,ident_str )

    def _handle_slash (self ):
        token_line =self .line_number
        self .advance ()

        next_char =self .get_current_char ()

        if next_char =='/':

            self .advance ()
            self ._scan_line_comment ()
            return None
        elif next_char =='*':

            self .advance ()
            self ._scan_block_comment (token_line )
            return None
        else :

            return (token_line ,TokenType .SYMBOL ,'/')

    def _handle_star (self ):
        token_line =self .line_number
        self .advance ()

        next_char =self .get_current_char ()

        if next_char =='/':

            self .advance ()
            self .lexical_errors .append ({
            'line':token_line ,
            'text':'*/',
            'message':'Unmatched comment'
            })
            return None
        else :

            return (token_line ,TokenType .SYMBOL ,'*')

    def _handle_equal (self ):
        token_line =self .line_number
        self .advance ()

        next_char =self .get_current_char ()

        if next_char =='=':
            self .advance ()
            return (token_line ,TokenType .SYMBOL ,'==')
        else :
            return (token_line ,TokenType .SYMBOL ,'=')

    def _scan_line_comment (self ):
        while self .position <len (self .source_code ):
            char =self .get_current_char ()
            if char =='\n':
                break
            self .advance ()

    def _scan_block_comment (self ,start_line ):

        comment_start =self .position -2

        while self .position <len (self .source_code ):
            char =self .advance ()
            if char =='*'and self .get_current_char ()=='/':
                self .advance ()
                return

        comment_end =min (comment_start +9 ,len (self .source_code ))
        comment_text =self .source_code [comment_start :comment_end ]

        if len (self .source_code )>comment_start +9 :
            error_text =comment_text +'...'
        else :
            error_text =comment_text +'...'

        self .lexical_errors .append ({
        'line':start_line ,
        'text':error_text ,
        'message':'Unclosed comment'
        })

    def _handle_invalid_start (self ):
        token_line =self .line_number
        error_char =self .advance ()

        self .lexical_errors .append ({
        'line':token_line ,
        'text':error_char ,
        'message':'Invalid input'
        })

        return None

    def tokenize (self ):
        self .read_input ()

        while self .position <len (self .source_code ):
            token =self .scan_token ()
            if token :
                self .tokens .append (token )

        return self .tokens

    def write_tokens (self ,filename ='tokens.txt'):
        lines ={}
        for line_num ,token_type ,token_string in self .tokens :
            if line_num not in lines :
                lines [line_num ]=[]
            lines [line_num ].append ((token_type ,token_string ))

        try :
            with open (filename ,'w',encoding ='utf-8')as file :
                for line_num in sorted (lines .keys ()):
                    file .write (f"{line_num }.\t")
                    token_pairs =[]
                    for token_type ,token_string in lines [line_num ]:
                        token_pairs .append (f"({token_type .name }, {token_string })")
                    file .write (' '.join (token_pairs ))
                    file .write (' \n')
        except Exception as e :
            print (f"Error writing tokens file: {e }")

    def write_symbol_table (self ,filename ='symbol_table.txt'):
        try :
            with open (filename ,'w',encoding ='utf-8')as file :
                sorted_table =sorted (self .symbol_table .items (),key =lambda x :x [1 ])
                for lexeme ,index in sorted_table :
                    file .write (f"{index }.\t{lexeme }\n")
        except Exception as e :
            print (f"Error writing symbol table: {e }")

    def write_lexical_errors (self ,filename ='lexical_errors.txt'):
        try :
            with open (filename ,'w',encoding ='utf-8')as file :
                if not self .lexical_errors :
                    file .write ("There is no lexical error.\n")
                else :
                    for error in self .lexical_errors :
                        file .write (f"{error ['line']}.\t({error ['text']}, {error ['message']})\n")
        except Exception as e :
            print (f"Error writing lexical errors: {e }")

    def get_next_token (self ):
        if self .position <len (self .source_code ):
            return self .scan_token ()
        return None

class ParseTreeNode :
    def __init__ (self ,name ):
        self .name =name
        self .children =[]

    def add_child (self ,child ):
        if isinstance (child ,str ):
            self .children .append (ParseTreeNode (child ))
        else :
            self .children .append (child )
        return child

def _build_tree (node ,lines ,is_last_stack ,is_root ):
    if is_root :
        lines .append (node .name )
    else :
        prefix =""
        for i in range (len (is_last_stack )-1 ):
            if is_last_stack [i ]:
                prefix +="    "
            else :
                prefix +="│   "

        if is_last_stack [-1 ]:
            connector ="└── "
        else :
            connector ="├── "

        lines .append (prefix +connector +node .name )

    for i ,child in enumerate (node .children ):
        child_is_last =(i ==len (node .children )-1 )
        _build_tree (child ,lines ,is_last_stack +[child_is_last ],False )

def generate_parse_tree_string (node ):
    lines =[]
    _build_tree (node ,lines ,[],True )
    return "\n".join (lines )

class ParserScanner (Scanner ):

    def read_input (self ):
        super ().read_input ()
        self .source_code =self .source_code .replace ('//','/ /')

class Parser :

    def __init__ (self ,input_file ='input.txt'):
        self .scanner =ParserScanner (input_file )
        self .scanner .read_input ()
        self .current_token =None
        self .syntax_errors =[]
        self .root =None
        self .relaxed_statement_expression =False
        self .eof_error_line =None
        self ._advance ()

    def _advance (self ):
        self .current_token =self .scanner .get_next_token ()
        while self .current_token is None and self .scanner .position <len (self .scanner .source_code ):
            self .current_token =self .scanner .get_next_token ()

    def eat (self ):
        self ._advance ()

    def error (self ,message ):
        if self .current_token :
            line =self .current_token [0 ]
        elif self .eof_error_line is not None :
            line =self .eof_error_line
        else :
            line =self .scanner .line_number
        self .syntax_errors .append ("#{} : syntax error, {}".format (line ,message ))

    def _skip_to (self ,follow_set ):
        while self .current_token is not None :
            if self .current_token [2 ]in follow_set or self .current_token [1 ]in follow_set :
                return
            self .eat ()

    def _lookahead_symbol (self ):
        if self .current_token is None :
            return '$'
        if self .current_token [1 ]==TokenType .ID :
            return 'ID'
        if self .current_token [1 ]==TokenType .NUM :
            return 'NUM'
        return self .current_token [2 ]

    def _report_illegal_current (self ):
        if self .current_token is None :
            return
        if self .current_token [1 ]==TokenType .NUM :
            self .error ("illegal NUM")
        elif self .current_token [1 ]==TokenType .ID :
            self .error ("illegal ID")
        else :
            self .error ("illegal {}".format (self .current_token [2 ]))

    def _panic_to_first_or_follow (self ,first_set ,follow_set ):
        sync_set =set (first_set )|set (follow_set )
        while self .current_token is not None and self ._lookahead_symbol ()not in sync_set :
            self ._report_illegal_current ()
            self .eat ()

    def _is_statement_start (self ):
        if self .current_token is None :
            return False
        first_statement ={'if','(','+','-',';','{','while','return','break','goto','switch',':'}
        return (self .current_token [2 ]in first_statement or
        self .current_token [1 ]in {TokenType .ID ,TokenType .NUM })

    def _append_statement_list (self ,target_node ,source_node ):
        current =target_node
        while True :
            if len (current .children )==1 and current .children [0 ].name =="epsilon":
                current .children =list (source_node .children )
                return
            if current .children and current .children [-1 ].name =="StatementList":
                current =current .children [-1 ]
            else :
                current .children .extend (source_node .children )
                return

    def _format_label_identifier (self ,lexeme ):
        if '_'in lexeme :
            return lexeme .split ('_')[-1 ]
        return lexeme

    def _peek_next_token (self ):
        scanner =self .scanner
        saved_position =scanner .position
        saved_line =scanner .line_number
        saved_errors =list (scanner .lexical_errors )
        saved_table =dict (scanner .symbol_table )
        saved_next_index =scanner .next_symbol_index

        token =scanner .get_next_token ()
        while token is None and scanner .position <len (scanner .source_code ):
            token =scanner .get_next_token ()

        scanner .position =saved_position
        scanner .line_number =saved_line
        scanner .lexical_errors =saved_errors
        scanner .symbol_table =saved_table
        scanner .next_symbol_index =saved_next_index
        return token

    def _recover_to_num_before_rparen (self ):
        while self .current_token is not None :
            if self .current_token [1 ]==TokenType .NUM :
                next_token =self ._peek_next_token ()
                if next_token and next_token [2 ]==')':
                    return
                self ._report_illegal_current ()
                self .error ("missing ;")
                self .eat ()
                continue
            self ._report_illegal_current ()
            self .eat ()

    def _drop_trailing_statementlist_epsilon (self ,node ):
        if not node .children :
            return
        last_child =node .children [-1 ]
        if last_child .name =="StatementList":
            if len (last_child .children )==1 and last_child .children [0 ].name =="epsilon":
                node .children .pop ()
            else :
                self ._drop_trailing_statementlist_epsilon (last_child )

    def _prune_trailing_expression_epsilons (self ,expression_node ):
        if expression_node is None or not expression_node .children :
            return
        simple_expr =expression_node .children [0 ]
        if simple_expr .name !="SimpleExpressionZegond"or len (simple_expr .children )<2 :
            return

        additive_expr =simple_expr .children [0 ]
        c_node =simple_expr .children [1 ]
        if c_node .name =="C"and len (c_node .children )==1 and c_node .children [0 ].name =="epsilon":
            simple_expr .children .pop ()

        if additive_expr .name !="AdditiveExpressionZegond"or len (additive_expr .children )<2 :
            return
        term_zegond =additive_expr .children [0 ]
        d_node =additive_expr .children [1 ]
        if d_node .name =="D"and len (d_node .children )==1 and d_node .children [0 ].name =="epsilon":
            additive_expr .children .pop ()

        if term_zegond .name !="TermZegond"or len (term_zegond .children )<2 :
            return
        g_node =term_zegond .children [1 ]
        if g_node .name =="G"and len (g_node .children )==1 and g_node .children [0 ].name =="epsilon":
            term_zegond .children .pop ()

    def parse (self ):
        self .root =self .parse_program ()
        return self .root

    def parse_program (self ):
        node =ParseTreeNode ("Program")
        node .add_child (self .parse_declaration_list ())
        if self .current_token is not None :
            self ._report_illegal_current ()
            self .eat ()
        node .add_child (ParseTreeNode ("$"))
        return node

    def parse_declaration_list (self ):
        node =ParseTreeNode ("DeclarationList")
        if self .current_token and self .current_token [2 ]in {'int','void'}:
            node .add_child (self .parse_declaration ())
            node .add_child (self .parse_declaration_list ())
        else :
            node .add_child (ParseTreeNode ("epsilon"))
        return node

    def parse_declaration (self ):
        node =ParseTreeNode ("Declaration")
        node .add_child (self .parse_declaration_initial ())
        if self .current_token and self .current_token [2 ]in {'(',';','[','='}:
            node .add_child (self .parse_declaration_prime ())
        else :

            if self .current_token and self .current_token [2 ]in {'int','void'}:
                self .error ("missing DeclarationPrime")

            elif self .current_token :
                self .error ("missing DeclarationPrime")
        return node

    def parse_declaration_initial (self ):
        node =ParseTreeNode ("DeclarationInitial")
        node .add_child (self .parse_type_specifier ())
        if self .current_token and self .current_token [1 ]==TokenType .ID :
            node .add_child (ParseTreeNode ("(ID, {}) ".format (self .current_token [2 ])))
            self .eat ()
        elif self .current_token and self .current_token [2 ]!=';':
            self .error ("missing ID")
            self ._skip_to ({';','[','(','=',',',')','}','$'})
        return node

    def parse_declaration_prime (self ):
        node =ParseTreeNode ("DeclarationPrime")
        if self .current_token and self .current_token [2 ]=='(':
            node .add_child (self .parse_fun_declaration_prime ())
        else :
            node .add_child (self .parse_var_declaration_prime ())
        return node

    def parse_var_declaration_prime (self ):
        node =ParseTreeNode ("VarDeclarationPrime")

        if self .current_token and self .current_token [2 ]==';':
            node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
            self .eat ()
        elif self .current_token and self .current_token [2 ]=='[':
            node .add_child (ParseTreeNode ("(SYMBOL, [) "))
            self .eat ()
            if self .current_token and self .current_token [1 ]==TokenType .NUM :
                node .add_child (ParseTreeNode ("(NUM, {}) ".format (self .current_token [2 ])))
                self .eat ()
            else :
                self .error ("illegal NUM")
                self ._skip_to ({']',';','='})
            if self .current_token and self .current_token [2 ]==']':
                node .add_child (ParseTreeNode ("(SYMBOL, ]) "))
                self .eat ()
            else :
                self .error ("missing ]")
                self ._skip_to ({';','='})
            node .add_child (self .parse_var_decl_array_prime ())
        elif self .current_token and self .current_token [2 ]=='=':
            node .add_child (ParseTreeNode ("(SYMBOL, =) "))
            self .eat ()
            node .add_child (self .parse_expression ())
            if self .current_token and self .current_token [2 ]==';':
                node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
                self .eat ()
            else :
                self .error ("missing ;")
                self ._skip_to ({'}','int','void','$'})
        else :
            self .error ("missing DeclarationPrime")

            while self .current_token is not None and self .current_token [2 ]not in {'int','void','}','$'}:
                if self .current_token [1 ]==TokenType .NUM :
                    self .error ("illegal NUM")
                elif self .current_token [1 ]==TokenType .ID :
                    self .error ("illegal ID")
                else :
                    self .error ("illegal {}".format (self .current_token [2 ]))
                self .eat ()
        return node

    def parse_var_decl_array_prime (self ):
        node =ParseTreeNode ("VarDeclArrayPrime")

        if self .current_token and self .current_token [2 ]==';':
            node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
            self .eat ()
        elif self .current_token and self .current_token [2 ]=='=':
            node .add_child (ParseTreeNode ("(SYMBOL, =) "))
            self .eat ()
            node .add_child (self .parse_expression ())
            if self .current_token and self .current_token [2 ]==';':
                node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
                self .eat ()
            else :
                self .error ("missing ;")
                self ._skip_to ({'}','int','void','$'})
        else :
            self .error ("missing ; or =")
            self ._skip_to ({'}','int','void','$'})
        return node

    def parse_fun_declaration_prime (self ):
        node =ParseTreeNode ("FunDeclarationPrime")

        if self .current_token and self .current_token [2 ]=='(':
            node .add_child (ParseTreeNode ("(SYMBOL, () "))
            self .eat ()
        else :
            self .error ("missing (")
            self ._skip_to ({')','{','int','void'})
            if self .current_token and self .current_token [2 ]=='(':
                self .eat ()

        node .add_child (self .parse_params ())

        if self .current_token and self .current_token [2 ]==')':
            node .add_child (ParseTreeNode ("(SYMBOL, )) "))
            self .eat ()
        else :
            while self .current_token is not None and self .current_token [2 ]not in {')','{','$'}:
                self ._report_illegal_current ()
                self .eat ()
            if self .current_token and self .current_token [2 ]==')':
                node .add_child (ParseTreeNode ("(SYMBOL, )) "))
                self .eat ()
            elif self .current_token and self .current_token [2 ]=='{':
                node .add_child (ParseTreeNode ("(SYMBOL, )) "))

        node .add_child (self .parse_compound_stmt ())
        return node

    def parse_type_specifier (self ):
        node =ParseTreeNode ("TypeSpecifier")
        if self .current_token and self .current_token [2 ]in {'int','void'}:
            node .add_child (ParseTreeNode ("(KEYWORD, {}) ".format (self .current_token [2 ])))
            self .eat ()
        else :
            self .error ("illegal int")
            self ._skip_to ({'$','ID',';'})
        return node

    def parse_params (self ):
        node =ParseTreeNode ("Params")

        if self .current_token and self .current_token [2 ]=='int':
            node .add_child (ParseTreeNode ("(KEYWORD, int) "))
            self .eat ()
            if self .current_token and self .current_token [1 ]==TokenType .ID :
                node .add_child (ParseTreeNode ("(ID, {}) ".format (self .current_token [2 ])))
                self .eat ()
            elif self .current_token and self .current_token [2 ]=='{':
                self .error ("missing ID")
                self .error ("illegal {")
                self .eat ()
            else :
                self .error ("illegal int")
                self ._skip_to ({']',',',')'})
            node .add_child (self .parse_param_prime ())
            node .add_child (self .parse_param_list ())
        elif self .current_token and self .current_token [2 ]=='void':
            node .add_child (ParseTreeNode ("(KEYWORD, void) "))
            self .eat ()
        else :
            self .error ("illegal int")
            self ._skip_to ({')',',',']'})
        return node

    def parse_param_list (self ):
        node =ParseTreeNode ("ParamList")

        if self .current_token and self .current_token [2 ]==',':
            node .add_child (ParseTreeNode ("(SYMBOL, ,) "))
            self .eat ()
            node .add_child (self .parse_param ())
            node .add_child (self .parse_param_list ())
        else :
            node .add_child (ParseTreeNode ("epsilon"))
        return node

    def parse_param (self ):
        node =ParseTreeNode ("Param")
        node .add_child (self .parse_declaration_initial ())
        node .add_child (self .parse_param_prime ())
        return node

    def parse_param_prime (self ):
        node =ParseTreeNode ("ParamPrime")

        if self .current_token and self .current_token [2 ]=='[':
            node .add_child (ParseTreeNode ("(SYMBOL, [) "))
            self .eat ()
            if self .current_token and self .current_token [2 ]==']':
                node .add_child (ParseTreeNode ("(SYMBOL, ]) "))
                self .eat ()
            else :
                self .error ("missing ]")
                self ._skip_to ({',',')'})
        else :
            node .add_child (ParseTreeNode ("epsilon"))
        return node

    def parse_compound_stmt (self ):
        node =ParseTreeNode ("CompoundStmt")
        if self .current_token and self .current_token [2 ]=='{':
            node .add_child (ParseTreeNode ("(SYMBOL, {) "))
            self .eat ()
        else :

            if self .current_token :
                self ._report_illegal_current ()
                self .eat ()
                while self .current_token is not None and self .current_token [2 ]not in {';','}','$','case','default','{'}:
                    self ._report_illegal_current ()
                    self .eat ()
            else :
                self .error ("missing {")

        node .add_child (self .parse_declaration_list ())
        statement_list_node =self .parse_statement_list ()
        node .add_child (statement_list_node )

        while self .current_token is not None and self .current_token [2 ]!='}':
            if self .current_token [2 ]in {'int','void'}:
                self .error ("illegal int")
                self .eat ()
            elif self ._is_statement_start ():
                more_stmts =self .parse_statement_list ()
                self ._append_statement_list (statement_list_node ,more_stmts )
            else :
                self ._report_illegal_current ()
                self .eat ()

        if self .current_token and self .current_token [2 ]=='}':
            node .add_child (ParseTreeNode ("(SYMBOL, }) "))
            self .eat ()
        else :
            self ._drop_trailing_statementlist_epsilon (statement_list_node )
            self .error ("missing StatementList")
            self .error ("missing }")
        return node

    def parse_statement_list (self ):
        node =ParseTreeNode ("StatementList")

        first_statement ={'if','(','+','-',';','{','while','return','break','goto','switch',':'}
        if self .current_token and (self .current_token [2 ]in first_statement or self .current_token [1 ]in {TokenType .ID ,TokenType .NUM }):
            node .add_child (self .parse_statement ())
            node .add_child (self .parse_statement_list ())
        else :
            node .add_child (ParseTreeNode ("epsilon"))
        return node

    def parse_statement (self ):
        node =ParseTreeNode ("Statement")

        if self .current_token and self .current_token [2 ]=='if':
            node .add_child (ParseTreeNode ("(KEYWORD, if) "))
            self .eat ()
            if self .current_token and self .current_token [2 ]=='(':
                node .add_child (ParseTreeNode ("(SYMBOL, () "))
                self .eat ()
            else :
                self .error ("missing (")
                self ._skip_to ({')','{',';'})
                if self .current_token and self .current_token [2 ]=='(':
                    self .eat ()

            node .add_child (self .parse_expression ())

            if self .current_token and self .current_token [2 ]==')':
                node .add_child (ParseTreeNode ("(SYMBOL, )) "))
                self .eat ()
            else :

                while self .current_token and self .current_token [2 ]not in {')','{','$'}:
                    if self .current_token [1 ]==TokenType .NUM :
                        self .error ("illegal NUM")
                        self .eat ()
                        break
                    elif self .current_token [1 ]==TokenType .ID :
                        self .error ("illegal ID")
                        self .eat ()
                        break
                    self .eat ()
                if self .current_token and self .current_token [2 ]==')':
                    node .add_child (ParseTreeNode ("(SYMBOL, )) "))
                    self .eat ()

            node .add_child (self .parse_statement ())
            node .add_child (self .parse_else_opt ())
        else :
            node .add_child (self .parse_other_stmt ())

        return node

    def parse_else_opt (self ):
        node =ParseTreeNode ("ElseOpt")

        if self .current_token and self .current_token [2 ]=='else':
            node .add_child (ParseTreeNode ("(KEYWORD, else) "))
            self .eat ()
            node .add_child (self .parse_statement ())
        else :
            node .add_child (ParseTreeNode ("epsilon"))
        return node

    def parse_other_stmt (self ):
        node =ParseTreeNode ("OtherStmt")

        if self .current_token and self .current_token [2 ]==':':
            node .add_child (ParseTreeNode ("(SYMBOL, :) "))
            self .eat ()
            node .add_child (self .parse_statement ())
        elif self .current_token and self .current_token [1 ]==TokenType .ID :
            identifier =self .current_token [2 ]
            self .eat ()
            if self .current_token and self .current_token [2 ]==':':
                identifier =self ._format_label_identifier (identifier )
            node .add_child (ParseTreeNode ("(ID, {}) ".format (identifier )))
            prime_node =self .parse_id_statement_prime ()
            if prime_node is not None :
                node .add_child (prime_node )
        elif self .current_token and self .current_token [2 ]==';':
            node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
            self .eat ()
        elif self .current_token and self .current_token [2 ]=='{':
            node .add_child (self .parse_compound_stmt ())
        elif self .current_token and self .current_token [2 ]=='while':
            node .add_child (self .parse_iteration_stmt ())
        elif self .current_token and self .current_token [2 ]=='return':
            node .add_child (self .parse_return_stmt ())
        elif self .current_token and self .current_token [2 ]=='break':
            node .add_child (self .parse_break_stmt ())
        elif self .current_token and self .current_token [2 ]=='goto':
            node .add_child (self .parse_goto_stmt ())
        elif self .current_token and self .current_token [2 ]=='switch':
            node .add_child (self .parse_switch_stmt ())
        else :
            previous_relaxed_state =self .relaxed_statement_expression
            self .relaxed_statement_expression =True
            node .add_child (self .parse_simple_expression_zegond ())
            self .relaxed_statement_expression =previous_relaxed_state
            if self .current_token and self .current_token [2 ]==';':
                node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
                self .eat ()
            elif self .current_token and self .current_token [2 ]=='if':
                self ._recover_to_num_before_rparen ()
                return node
            elif self .current_token and self .current_token [2 ]==')':
                self .error ("missing ;")
                self ._report_illegal_current ()
                self .eat ()
            elif self .current_token and self .current_token [2 ]in {'while','return','break','goto','switch','int','void','else','case','default','$','}'}:
                return node
            else :

                while self .current_token is not None and self .current_token [2 ]not in {';','}','$'}:
                    self ._report_illegal_current ()
                    self .eat ()
                if self .current_token and self .current_token [2 ]==';':
                    node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
                    self .eat ()

        return node

    def parse_id_statement_prime (self ):
        node =ParseTreeNode ("IdStatementPrime")

        if self .current_token and self .current_token [2 ]==':':
            node .add_child (ParseTreeNode ("(SYMBOL, :) "))
            self .eat ()
            node .add_child (self .parse_statement ())
            return node

        if self .current_token and (
        self .current_token [1 ]==TokenType .ID or
        self .current_token [2 ]in {'if','while','return','break','goto','switch','{','}','$','int','void','else','case','default'}
        ):
            self .error ("missing IdStatementPrime")
            return None

        b_node =self .parse_b ()
        node .add_child (b_node )
        if self .current_token and self .current_token [2 ]==';':
            node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
            self .eat ()
        elif b_node .children and b_node .children [0 ].name .startswith ("(SYMBOL, [)"):
            self .error ("missing ;")
            while (self .current_token is not None and
            self .current_token [1 ]!=TokenType .NUM and
            self .current_token [2 ]not in {';','}','$'}):
                if self .current_token [1 ]==TokenType .NUM :
                    self .error ("illegal NUM")
                elif self .current_token [1 ]==TokenType .ID :
                    self .error ("illegal ID")
                else :
                    self .error ("illegal {}".format (self .current_token [2 ]))
                self .eat ()
            if self .current_token and self .current_token [2 ]==';':
                node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
                self .eat ()
        elif b_node .children and b_node .children [0 ].name .startswith ("(SYMBOL, =)"):
            if self .current_token and self .current_token [2 ]=='}':
                self ._report_illegal_current ()
                self .eat ()
                if self .current_token is None :
                    self .eof_error_line =self .scanner .line_number +1
                    if len (b_node .children )>1 :
                        self ._prune_trailing_expression_epsilons (b_node .children [1 ])
                    self .error ("missing G")
                    self .error ("missing D")
                    self .error ("missing C")
                    self .error ("missing ;")
            elif self .current_token and self .current_token [2 ]!=';':
                self .error ("missing ;")
                while (self .current_token is not None and
                self .current_token [1 ]!=TokenType .NUM and
                self .current_token [2 ]not in {';','}','$'}):
                    self ._report_illegal_current ()
                    self .eat ()
                if self .current_token and self .current_token [2 ]==';':
                    node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
                    self .eat ()
        elif self .current_token and self .current_token [1 ]==TokenType .NUM :
            if self .current_token and self .current_token [2 ]==';':
                node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
                self .eat ()
        else :
            self .error ("missing ;")
            while self .current_token is not None and self .current_token [2 ]not in {';','}','$'}:
                if self .current_token [1 ]==TokenType .NUM :
                    self .error ("illegal NUM")
                elif self .current_token [1 ]==TokenType .ID :
                    self .error ("illegal ID")
                else :
                    self .error ("illegal {}".format (self .current_token [2 ]))
                self .eat ()
            if self .current_token and self .current_token [2 ]==';':
                node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
                self .eat ()
        return node

    def parse_break_stmt (self ):
        node =ParseTreeNode ("BreakStmt")
        node .add_child (ParseTreeNode ("(KEYWORD, break) "))
        self .eat ()

        if self .current_token and self .current_token [2 ]==';':
            node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
            self .eat ()
        else :
            self .error ("missing ;")
            self ._skip_to ({'}','$'})
        return node

    def parse_iteration_stmt (self ):
        node =ParseTreeNode ("IterationStmt")
        node .add_child (ParseTreeNode ("(KEYWORD, while) "))
        self .eat ()

        if self .current_token and self .current_token [2 ]=='(':
            node .add_child (ParseTreeNode ("(SYMBOL, () "))
            self .eat ()
        else :
            self .error ("missing (")
            self ._skip_to ({')','{'})
            if self .current_token and self .current_token [2 ]=='(':
                self .eat ()

        node .add_child (self .parse_expression ())

        if self .current_token and self .current_token [2 ]==')':
            node .add_child (ParseTreeNode ("(SYMBOL, )) "))
            self .eat ()
        else :
            if self .current_token and self .current_token [1 ]==TokenType .NUM :
                self .error ("illegal NUM")
            elif self .current_token and self .current_token [1 ]==TokenType .ID :
                self .error ("illegal ID")
            elif self .current_token and self .current_token [2 ]:
                self .error ("illegal {}".format (self .current_token [2 ]))
            else :
                self .error ("missing )")
            self ._skip_to ({')','{'})
            if self .current_token and self .current_token [2 ]==')':
                self .eat ()

        node .add_child (self .parse_statement ())
        return node

    def parse_return_stmt (self ):
        node =ParseTreeNode ("ReturnStmt")
        node .add_child (ParseTreeNode ("(KEYWORD, return) "))
        self .eat ()

        node .add_child (self .parse_return_stmt_prime ())
        return node

    def parse_return_stmt_prime (self ):
        node =ParseTreeNode ("ReturnStmtPrime")

        if self .current_token and self .current_token [2 ]==';':
            node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
            self .eat ()
        else :
            node .add_child (self .parse_expression ())
            if self .current_token and self .current_token [2 ]==';':
                node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
                self .eat ()
            else :
                self .error ("missing ;")
                while (self .current_token is not None and
                self .current_token [2 ]not in {'}','int','void'}):
                    self ._report_illegal_current ()
                    self .eat ()
        return node

    def parse_expression (self ):
        node =ParseTreeNode ("Expression")

        if self .current_token and self .current_token [1 ]==TokenType .ID :
            node .add_child (ParseTreeNode ("(ID, {}) ".format (self .current_token [2 ])))
            self .eat ()
            node .add_child (self .parse_b ())
        else :
            node .add_child (self .parse_simple_expression_zegond ())

        return node

    def parse_b (self ):
        node =ParseTreeNode ("B")

        first_set ={'=','[','(','*','/','+','-','<','=='}
        follow_set ={';',')',']',',','}','$'}
        self ._panic_to_first_or_follow (first_set ,follow_set )

        if self .current_token and self .current_token [2 ]=='=':
            node .add_child (ParseTreeNode ("(SYMBOL, =) "))
            self .eat ()
            if self .current_token and (self .current_token [1 ]in {TokenType .ID ,TokenType .NUM }
            or self .current_token [2 ]in {'(','+','-'}):
                node .add_child (self .parse_expression ())
            else :
                while self .current_token is not None and self ._lookahead_symbol ()not in {'ID','NUM','(','+','-',';',')',']',',','}','$'}:
                    self ._report_illegal_current ()
                    self .eat ()
                if self .current_token and (self .current_token [1 ]in {TokenType .ID ,TokenType .NUM }
                or self .current_token [2 ]in {'(','+','-'}):
                    node .add_child (self .parse_expression ())
        elif self .current_token and self .current_token [2 ]=='[':
            node .add_child (ParseTreeNode ("(SYMBOL, [) "))
            self .eat ()
            node .add_child (self .parse_expression ())
            if self .current_token and self .current_token [2 ]==']':
                node .add_child (ParseTreeNode ("(SYMBOL, ]) "))
                self .eat ()
            else :
                self .error ("missing ]")
                self ._skip_to ({'=',';',')',']','+','-','*','/','<','=='})
            node .add_child (self .parse_h ())
        else :
            node .add_child (self .parse_simple_expression_prime ())

        return node

    def parse_h (self ):
        node =ParseTreeNode ("H")

        first_set ={'=','*','/','+','-','<','=='}
        follow_set ={';',')',']',',','}','$','ID','NUM','if','while','return','break','goto','switch','int','void','else','case','default'}
        self ._panic_to_first_or_follow (first_set ,follow_set )

        if self .current_token and self .current_token [2 ]=='=':
            node .add_child (ParseTreeNode ("(SYMBOL, =) "))
            self .eat ()
            node .add_child (self .parse_expression ())
        else :
            node .add_child (self .parse_g ())
            node .add_child (self .parse_d ())
            node .add_child (self .parse_c ())

        return node

    def parse_simple_expression_zegond (self ):
        node =ParseTreeNode ("SimpleExpressionZegond")
        node .add_child (self .parse_additive_expression_zegond ())
        node .add_child (self .parse_c ())
        return node

    def parse_simple_expression_prime (self ):
        node =ParseTreeNode ("SimpleExpressionPrime")
        node .add_child (self .parse_additive_expression_prime ())
        node .add_child (self .parse_c ())
        return node

    def parse_c (self ):
        node =ParseTreeNode ("C")

        first_set ={'<','=='}
        follow_set ={';',')',']',',','}','$'}
        if self .relaxed_statement_expression :
            follow_set =set (follow_set )|{'ID','NUM','if','while','return','break','goto','switch','int','void','else','case','default'}
        self ._panic_to_first_or_follow (first_set ,follow_set )

        if self .current_token and self .current_token [2 ]in {'<','=='}:
            node .add_child (self .parse_relop ())
            node .add_child (self .parse_additive_expression ())
        else :
            node .add_child (ParseTreeNode ("epsilon"))
        return node

    def parse_relop (self ):
        node =ParseTreeNode ("Relop")
        node .add_child (ParseTreeNode ("(SYMBOL, {}) ".format (self .current_token [2 ])))
        self .eat ()
        return node

    def parse_additive_expression (self ):
        node =ParseTreeNode ("AdditiveExpression")
        node .add_child (self .parse_term ())
        node .add_child (self .parse_d ())
        return node

    def parse_additive_expression_prime (self ):
        node =ParseTreeNode ("AdditiveExpressionPrime")
        node .add_child (self .parse_term_prime ())
        node .add_child (self .parse_d ())
        return node

    def parse_additive_expression_zegond (self ):
        node =ParseTreeNode ("AdditiveExpressionZegond")
        node .add_child (self .parse_term_zegond ())
        node .add_child (self .parse_d ())
        return node

    def parse_d (self ):
        node =ParseTreeNode ("D")

        first_set ={'+','-'}
        follow_set ={'<','==',';',')',']',',','}','$'}
        if self .relaxed_statement_expression :
            follow_set =set (follow_set )|{'ID','NUM','if','while','return','break','goto','switch','int','void','else','case','default'}
        self ._panic_to_first_or_follow (first_set ,follow_set )

        if self .current_token and self .current_token [2 ]in {'+','-'}:
            node .add_child (self .parse_addop ())
            node .add_child (self .parse_term ())
            node .add_child (self .parse_d ())

        if not node .children :
            node .add_child (ParseTreeNode ("epsilon"))
        return node

    def parse_addop (self ):
        node =ParseTreeNode ("Addop")
        node .add_child (ParseTreeNode ("(SYMBOL, {}) ".format (self .current_token [2 ])))
        self .eat ()
        return node

    def parse_term (self ):
        node =ParseTreeNode ("Term")
        node .add_child (self .parse_signed_factor ())
        node .add_child (self .parse_g ())
        return node

    def parse_term_prime (self ):
        node =ParseTreeNode ("TermPrime")
        node .add_child (self .parse_signed_factor_prime ())
        node .add_child (self .parse_g ())
        return node

    def parse_term_zegond (self ):
        node =ParseTreeNode ("TermZegond")
        node .add_child (self .parse_signed_factor_zegond ())
        node .add_child (self .parse_g ())
        return node

    def parse_g (self ):
        node =ParseTreeNode ("G")

        first_set ={'*','/'}
        follow_set ={'+','-','<','==',';',')',']',',','}','$'}
        if self .relaxed_statement_expression :
            follow_set =set (follow_set )|{'ID','NUM','if','while','return','break','goto','switch','int','void','else','case','default'}
        self ._panic_to_first_or_follow (first_set ,follow_set )

        if self .current_token and self .current_token [2 ]in {'*','/'}:
            node .add_child (self .parse_mulop ())
            if self .current_token and self .current_token [2 ]in {'*','/','<','==',';',')',']',',','}','$'}:
                self .error ("missing SignedFactor")
            else :
                node .add_child (self .parse_signed_factor ())
            node .add_child (self .parse_g ())

        if not node .children :
            node .add_child (ParseTreeNode ("epsilon"))
        return node

    def parse_mulop (self ):
        node =ParseTreeNode ("Mulop")
        node .add_child (ParseTreeNode ("(SYMBOL, {}) ".format (self .current_token [2 ])))
        self .eat ()
        return node

    def parse_signed_factor (self ):
        node =ParseTreeNode ("SignedFactor")

        if self .current_token and self .current_token [2 ]=='+':
            node .add_child (ParseTreeNode ("(SYMBOL, +) "))
            self .eat ()
            node .add_child (self .parse_factor ())
        elif self .current_token and self .current_token [2 ]=='-':
            node .add_child (ParseTreeNode ("(SYMBOL, -) "))
            self .eat ()
            node .add_child (self .parse_factor ())
        else :
            node .add_child (self .parse_factor ())

        return node

    def parse_signed_factor_prime (self ):
        node =ParseTreeNode ("SignedFactorPrime")
        node .add_child (self .parse_factor_prime ())
        return node

    def parse_signed_factor_zegond (self ):
        node =ParseTreeNode ("SignedFactorZegond")

        if self .current_token and self .current_token [2 ]=='+':
            node .add_child (ParseTreeNode ("(SYMBOL, +) "))
            self .eat ()
            node .add_child (self .parse_factor ())
        elif self .current_token and self .current_token [2 ]=='-':
            node .add_child (ParseTreeNode ("(SYMBOL, -) "))
            self .eat ()
            node .add_child (self .parse_factor ())
        else :
            node .add_child (self .parse_factor_zegond ())

        return node

    def parse_factor (self ):
        node =ParseTreeNode ("Factor")

        if self .current_token and self .current_token [2 ]=='(':
            node .add_child (ParseTreeNode ("(SYMBOL, () "))
            self .eat ()
            node .add_child (self .parse_expression ())
            if self .current_token and self .current_token [2 ]==')':
                node .add_child (ParseTreeNode ("(SYMBOL, )) "))
                self .eat ()
            else :
                self .error ("missing )")
                self ._skip_to ({'+','-','*','/',';','<','==',']',')'})
        elif self .current_token and self .current_token [1 ]==TokenType .ID :
            node .add_child (ParseTreeNode ("(ID, {}) ".format (self .current_token [2 ])))
            self .eat ()
            node .add_child (self .parse_var_call_prime ())
        elif self .current_token and self .current_token [1 ]==TokenType .NUM :
            node .add_child (ParseTreeNode ("(NUM, {}) ".format (self .current_token [2 ])))
            self .eat ()
        else :
            self .error ("illegal ID")
            self ._skip_to ({'+','-','*','/',';','<','==',']',')',','})

        return node

    def parse_var_call_prime (self ):
        node =ParseTreeNode ("VarCallPrime")

        while self .current_token and self .current_token [2 ]not in {'(','[',';',')',']',',','+','-','*','/','<','==','$'}:
            self ._report_illegal_current ()
            self .eat ()

        if self .current_token and self .current_token [2 ]=='(':
            node .add_child (ParseTreeNode ("(SYMBOL, () "))
            self .eat ()
            node .add_child (self .parse_args ())
            if self .current_token and self .current_token [2 ]==')':
                node .add_child (ParseTreeNode ("(SYMBOL, )) "))
                self .eat ()
            else :
                self .error ("missing )")
                self ._skip_to ({';','}'})
        else :
            node .add_child (self .parse_var_prime ())

        return node

    def parse_var_prime (self ):
        node =ParseTreeNode ("VarPrime")

        if self .current_token and self .current_token [2 ]=='[':
            node .add_child (ParseTreeNode ("(SYMBOL, [) "))
            self .eat ()
            node .add_child (self .parse_expression ())
            if self .current_token and self .current_token [2 ]==']':
                node .add_child (ParseTreeNode ("(SYMBOL, ]) "))
                self .eat ()
            else :
                self .error ("missing ]")
                self ._skip_to ({';','}','+','-','*','/'})
        else :
            node .add_child (ParseTreeNode ("epsilon"))

        return node

    def parse_factor_prime (self ):
        node =ParseTreeNode ("FactorPrime")

        if self .current_token and self .current_token [2 ]=='(':
            node .add_child (ParseTreeNode ("(SYMBOL, () "))
            self .eat ()
            node .add_child (self .parse_args ())
            if self .current_token and self .current_token [2 ]==')':
                node .add_child (ParseTreeNode ("(SYMBOL, )) "))
                self .eat ()
            else :
                self .error ("missing )")
                self ._skip_to ({';','}'})
        else :
            node .add_child (ParseTreeNode ("epsilon"))

        return node

    def parse_factor_zegond (self ):
        node =ParseTreeNode ("FactorZegond")

        if self .current_token and self .current_token [2 ]=='(':
            node .add_child (ParseTreeNode ("(SYMBOL, () "))
            self .eat ()
            node .add_child (self .parse_expression ())
            if self .current_token and self .current_token [2 ]==')':
                node .add_child (ParseTreeNode ("(SYMBOL, )) "))
                self .eat ()
            else :
                self .error ("missing )")
                self ._skip_to ({'+','-','*','/',';','<','==',']'})
        elif self .current_token and self .current_token [1 ]==TokenType .NUM :
            node .add_child (ParseTreeNode ("(NUM, {}) ".format (self .current_token [2 ])))
            self .eat ()
        else :
            if self .current_token [1 ]==TokenType .ID :
                self .error ("illegal ID")
            elif self .current_token [1 ]==TokenType .KEYWORD :
                self .error ("illegal {}".format (self .current_token [2 ]))
            else :
                self .error ("illegal {}".format (self .current_token [2 ]))

            self .eat ()

        return node

    def parse_args (self ):
        node =ParseTreeNode ("Args")

        if self .current_token and self .current_token [2 ]not in {')','$'}:
            if (self .current_token [1 ]in {TokenType .ID ,TokenType .NUM }or
            self .current_token [2 ]in {'(','+','-'}):
                node .add_child (self .parse_arg_list ())
            else :
                self ._report_illegal_current ()
                self .eat ()
                node .add_child (ParseTreeNode ("epsilon"))
        else :
            node .add_child (ParseTreeNode ("epsilon"))

        return node

    def parse_arg_list (self ):
        node =ParseTreeNode ("ArgList")
        node .add_child (self .parse_expression ())
        node .add_child (self .parse_arg_list_prime ())
        return node

    def parse_arg_list_prime (self ):
        node =ParseTreeNode ("ArgListPrime")

        if self .current_token and self .current_token [2 ]==',':
            node .add_child (ParseTreeNode ("(SYMBOL, ,) "))
            self .eat ()
            node .add_child (self .parse_expression ())
            node .add_child (self .parse_arg_list_prime ())

        if not node .children :
            node .add_child (ParseTreeNode ("epsilon"))
        return node

    def parse_goto_stmt (self ):
        node =ParseTreeNode ("GotoStmt")
        node .add_child (ParseTreeNode ("(KEYWORD, goto) "))
        self .eat ()

        if self .current_token and self .current_token [1 ]==TokenType .ID :
            node .add_child (ParseTreeNode ("(ID, {}) ".format (self ._format_label_identifier (self .current_token [2 ]))))
            self .eat ()
        else :
            self .error ("missing ID")
            if self .current_token and self .current_token [2 ]!=';':
                self .error ("missing ;")
            return node

        if self .current_token and self .current_token [2 ]==';':
            node .add_child (ParseTreeNode ("(SYMBOL, ;) "))
            self .eat ()
        else :
            self .error ("missing ;")
            self ._skip_to ({'}','$'})

        return node

    def parse_switch_stmt (self ):
        node =ParseTreeNode ("SwitchStmt")
        node .add_child (ParseTreeNode ("(KEYWORD, switch) "))
        self .eat ()

        if self .current_token and self .current_token [2 ]=='(':
            node .add_child (ParseTreeNode ("(SYMBOL, () "))
            self .eat ()
        else :
            self .error ("missing (")
            self ._skip_to ({')','{','$'})

        node .add_child (self .parse_expression ())

        if self .current_token and self .current_token [2 ]==')':
            node .add_child (ParseTreeNode ("(SYMBOL, )) "))
            self .eat ()
        else :
            if self .current_token is None :
                self .error ("missing )")
                self .error ("missing {")
            elif self .current_token [2 ]in {';','default','}'}:
                self .error ("missing )")
                self .error ("missing {")
                while self .current_token is not None and self .current_token [2 ]not in {'default','}'}:
                    self ._report_illegal_current ()
                    self .eat ()
            else :
                self ._report_illegal_current ()
                self .eat ()

                found_id =False
                while self .current_token is not None and self .current_token [2 ]not in {'default','}'}:
                    if self .current_token [1 ]==TokenType .ID and not found_id :
                        self .error ("illegal ID")
                        found_id =True
                        self .error ("missing )")
                        self .error ("missing {")
                        self .eat ()
                    elif found_id and self .current_token [1 ]==TokenType .ID :
                        self .eat ()
                    elif found_id and self .current_token [1 ]==TokenType .NUM :
                        self .eat ()
                    elif found_id and self .current_token [2 ]in {'+','-','*','/','<','==','[',']','(',')','='}:
                        self .eat ()
                    else :
                        self ._report_illegal_current ()
                        self .eat ()

            node .add_child (self .parse_case_list ())
            node .add_child (self .parse_default_opt ())

            if self .current_token and self .current_token [2 ]=='}':
                node .add_child (ParseTreeNode ("(SYMBOL, }) "))
                self .eat ()
            else :
                self .error ("missing }")
                self ._skip_to ({'$'})
            return node

        if self .current_token and self .current_token [2 ]=='{':
            node .add_child (ParseTreeNode ("(SYMBOL, {) "))
            self .eat ()
        else :
            self .error ("missing {")
            self ._skip_to ({'case','default','$'})
            if self .current_token and self .current_token [2 ]=='{':
                self .eat ()

        node .add_child (self .parse_case_list ())
        node .add_child (self .parse_default_opt ())

        if self .current_token and self .current_token [2 ]=='}':
            node .add_child (ParseTreeNode ("(SYMBOL, }) "))
            self .eat ()
        else :
            self .error ("missing }")
            self ._skip_to ({'$'})

        return node

    def parse_case_list (self ):
        node =ParseTreeNode ("CaseList")

        if self .current_token and self .current_token [2 ]=='case':
            node .add_child (self .parse_case ())
            node .add_child (self .parse_case_list ())
        else :
            node .add_child (ParseTreeNode ("epsilon"))
        return node

    def parse_case (self ):
        node =ParseTreeNode ("Case")
        node .add_child (ParseTreeNode ("(KEYWORD, case) "))
        self .eat ()
        node .add_child (self .parse_constant ())

        if self .current_token and self .current_token [2 ]==':':
            node .add_child (ParseTreeNode ("(SYMBOL, :) "))
            self .eat ()
        else :
            self .error ("illegal :")
            self ._skip_to ({'$'})

        node .add_child (self .parse_statement_list ())
        return node

    def parse_constant (self ):
        node =ParseTreeNode ("Constant")

        if self .current_token and self .current_token [1 ]==TokenType .NUM :
            node .add_child (ParseTreeNode ("(NUM, {}) ".format (self .current_token [2 ])))
            self .eat ()
        else :
            self .error ("illegal NUM")
            self ._skip_to ({':'})
            if self .current_token and self .current_token [1 ]==TokenType .NUM :
                node .add_child (ParseTreeNode ("(NUM, {}) ".format (self .current_token [2 ])))
                self .eat ()

        return node

    def parse_default_opt (self ):
        node =ParseTreeNode ("DefaultOpt")

        if self .current_token and self .current_token [2 ]=='default':
            node .add_child (ParseTreeNode ("(KEYWORD, default) "))
            self .eat ()

            if self .current_token and self .current_token [2 ]==':':
                node .add_child (ParseTreeNode ("(SYMBOL, :) "))
                self .eat ()
            else :
                self .error ("illegal :")
                self ._skip_to ({'}'})

            node .add_child (self .parse_statement_list ())
        else :
            node .add_child (ParseTreeNode ("epsilon"))

        return node

class _TacLabel :
    def __init__ (self ,owner ) :
        self .owner =owner
        self .index =None

class _TacRetAddr :
    def __init__ (self ,owner ,local ) :
        self .owner =owner
        self .local =local

class CodeGenerator :
    ALLOWED_OPS =set (['ADD','MULT','SUB','DIV','EQ','LT','ASSIGN','JPF','JP','PRINT'])

    def __init__ (self ,input_file ='input.txt',output_file ='output.txt') :
        self .input_file =input_file
        self .output_file =output_file
        self .tokens =[]
        self .pos =0
        self .globals ={}
        self .functions ={}
        self .global_next =100
        self .addr_counter =100
        self .lists ={}
        self .owner_order =[]
        self .current_owner =None
        self .current_list =None
        self .current_func =None
        self .local_vars ={}
        self .labels ={}
        self .break_stack =[]
        self .last_op =None
        self .offset ={}

    def cur_type (self ) :
        if self .pos <len (self .tokens ) :
            return self .tokens [self .pos ][0 ]
        return None

    def cur (self ) :
        if self .pos <len (self .tokens ) :
            return self .tokens [self .pos ][1 ]
        return None

    def peek_type (self ) :
        if self .pos +1 <len (self .tokens ) :
            return self .tokens [self .pos +1 ][0 ]
        return None

    def peek (self ) :
        if self .pos +1 <len (self .tokens ) :
            return self .tokens [self .pos +1 ][1 ]
        return None

    def adv (self ) :
        self .pos +=1

    def expect (self ,lex ) :
        if self .cur ()==lex :
            self .adv ()

    def emit (self ,op ,a =None ,b =None ,c =None) :
        self .current_list .append ([op ,a ,b ,c ])
        self .last_op =op

    def new_label (self ) :
        return _TacLabel (self .current_owner )

    def bind (self ,label ) :
        label .index =len (self .current_list )

    def alloc (self ,n ) :
        a =self .addr_counter
        self .addr_counter +=n
        return a

    def new_temp (self ) :
        return self .alloc (1 )

    def push_break (self ,label ) :
        self .break_stack .append (label )

    def pop_break (self ) :
        if self .break_stack :
            self .break_stack .pop ()

    def get_label (self ,name ) :
        if name not in self .labels :
            self .labels [name ]=self .new_label ()
        return self .labels [name ]

    def lookup (self ,name ) :
        if name in self .local_vars :
            return self .local_vars [name ]
        if name in self .globals :
            return self .globals [name ]
        raise ValueError (name )

    def var_value_operand (self ,info ) :
        if info ['kind']=='array' :
            if info ['param'] :
                return str (info ['addr'])
            return '#'+str (info ['addr'])
        return str (info ['addr'])

    def compute_elem_addr (self ,info ,idxop ) :
        if info ['param'] :
            t0 =self .new_temp ()
            self .emit ('ASSIGN' ,str (info ['addr']),t0 )
            base =str (t0 )
        else :
            base ='#'+str (info ['addr'])
        t1 =self .new_temp ()
        self .emit ('MULT' ,idxop ,'#1' ,t1 )
        t2 =self .new_temp ()
        self .emit ('ADD' ,base ,str (t1 ) ,t2 )
        return t2

    def gen_assign (self ,target ,value ) :
        if target [0 ]=='var' :
            name =target [1 ]
            info =self .lookup (name )
            self .emit ('ASSIGN' ,value ,str (info ['addr']))
        else :
            name =target [1 ]
            idx =target [2 ]
            info =self .lookup (name )
            idxop =self .gen_expr (idx )
            addr =self .compute_elem_addr (info ,idxop )
            self .emit ('ASSIGN' ,value ,'@'+str (addr ))

    def gen_expr (self ,e ) :
        tag =e [0 ]
        if tag=='const' :
            return '#'+str (e [1 ])
        if tag=='var' :
            info =self .lookup (e [1 ])
            return self .var_value_operand (info )
        if tag=='elem' :
            info =self .lookup (e [1 ])
            idxop =self .gen_expr (e [2 ])
            addr =self .compute_elem_addr (info ,idxop )
            return '@'+str (addr )
        if tag=='unary' :
            operand =self .gen_expr (e [2 ])
            if e [1 ]=='-' :
                t =self .new_temp ()
                self .emit ('SUB' ,'#0' ,operand ,t )
                return str (t )
            return operand
        if tag=='bin' :
            mop ={'+':'ADD','-':'SUB','*':'MULT','/':'DIV','<':'LT','==':'EQ'} [e [1 ]]
            left =self .gen_expr (e [2 ])
            right =self .gen_expr (e [3 ])
            t =self .new_temp ()
            self .emit (mop ,left ,right ,t )
            return str (t )
        if tag=='call' :
            return self .gen_call (e [1 ] ,e [2 ])
        if tag=='assign' :
            value =self .gen_expr (e [2 ])
            self .gen_assign (e [1 ] ,value )
            return value
        raise ValueError (tag )

    def gen_call (self ,name ,args ) :
        if name=='output' :
            value =self .gen_expr (args [0 ])
            self .emit ('PRINT' ,value )
            return None
        f =self .functions [name ]
        arg_vals =[]
        for a in args :
            arg_vals .append (self .gen_expr (a ))
        for i ,pc in enumerate (f ['param_cells']) :
            self .emit ('ASSIGN' ,arg_vals [i ] ,str (pc ))
        ret_local =len (self .current_list )+2
        self .emit ('ASSIGN' ,_TacRetAddr (self .current_owner ,ret_local ) ,str (f ['return_slot']))
        self .emit ('JP' ,f ['entry'])
        if f ['rettype']=='int' :
            tmp =self .new_temp ()
            self .emit ('ASSIGN' ,str (f ['output_slot']) ,tmp )
            return str (tmp )
        return None

    def gen_local_decl (self ,ld ) :
        name =ld [1 ]
        kind =ld [2 ]
        size =ld [3 ]
        init =ld [4 ]
        if kind=='array' :
            base =self .alloc (size )
            self .local_vars [name ]={'kind':'array','addr':base,'size':size,'param':False }
            for k in range (size ) :
                self .emit ('ASSIGN' ,'#0' ,str (base +k ))
            if init is not None :
                value =self .gen_expr (init )
                addr =self .compute_elem_addr (self .local_vars [name ],'#0' )
                self .emit ('ASSIGN' ,value ,'@'+str (addr ))
        else :
            cell =self .alloc (1 )
            self .local_vars [name ]={'kind':'scalar','addr':cell,'size':1,'param':False }
            self .emit ('ASSIGN' ,'#0' ,str (cell ))
            if init is not None :
                value =self .gen_expr (init )
                self .emit ('ASSIGN' ,value ,str (cell ))

    def gen_stmts (self ,stmts ) :
        for s in stmts :
            self .gen_stmt (s )

    def gen_stmt (self ,s ) :
        tag =s [0 ]
        if tag=='block' :
            for ld in s [1 ] :
                self .gen_local_decl (ld )
            self .gen_stmts (s [2 ])
        elif tag=='expr' :
            self .gen_expr (s [1 ])
        elif tag=='assign' :
            value =self .gen_expr (s [2 ])
            self .gen_assign (s [1 ] ,value )
        elif tag=='if' :
            cond =self .gen_expr (s [1 ])
            if s [3 ] is not None :
                else_lbl =self .new_label ()
                end_lbl =self .new_label ()
                self .emit ('JPF' ,cond ,else_lbl )
                self .gen_stmt (s [2 ])
                self .emit ('JP' ,end_lbl )
                self .bind (else_lbl )
                self .gen_stmt (s [3 ])
                self .bind (end_lbl )
            else :
                end_lbl =self .new_label ()
                self .emit ('JPF' ,cond ,end_lbl )
                self .gen_stmt (s [2 ])
                self .bind (end_lbl )
        elif tag=='while' :
            loop_lbl =self .new_label ()
            end_lbl =self .new_label ()
            self .bind (loop_lbl )
            cond =self .gen_expr (s [1 ])
            self .emit ('JPF' ,cond ,end_lbl )
            self .push_break (end_lbl )
            self .gen_stmt (s [2 ])
            self .pop_break ()
            self .emit ('JP' ,loop_lbl )
            self .bind (end_lbl )
        elif tag=='break' :
            self .emit ('JP' ,self .break_stack [-1 ])
        elif tag=='return' :
            ret =self .current_func ['return_slot']
            if s [1 ] is None :
                self .emit ('JP' ,'@'+str (ret ))
            else :
                value =self .gen_expr (s [1 ])
                self .emit ('ASSIGN' ,value ,str (self .current_func ['output_slot']))
                self .emit ('JP' ,'@'+str (ret ))
        elif tag=='goto' :
            self .emit ('JP' ,self .get_label (s [1 ]))
        elif tag=='label' :
            self .bind (self .get_label (s [1 ]))
        elif tag=='switch' :
            self .gen_switch (s )
        elif tag=='null' :
            pass

    def gen_switch (self ,s ) :
        cond =self .gen_expr (s [1 ])
        cases =s [2 ]
        default_stmts =s [3 ]
        switch_end =self .new_label ()
        self .push_break (switch_end )
        n =len (cases )
        case_tests =[self .new_label () for _ in range (n )]
        case_bodies =[self .new_label () for _ in range (n )]
        default_lbl =self .new_label ()
        self .bind (case_tests [0 ])
        for i in range (n ) :
            tmp =self .new_temp ()
            self .emit ('EQ' ,cond ,'#'+str (cases [i ][0 ]) ,tmp )
            nxt =case_tests [i +1 ] if i +1 <n else default_lbl
            self .emit ('JPF' ,str (tmp ) ,nxt )
            self .bind (case_bodies [i ])
            self .gen_stmts (cases [i ][1 ])
            if self .last_op !='JP' :
                fallto =case_bodies [i +1 ] if i +1 <n else default_lbl
                self .emit ('JP' ,fallto )
            if i +1 <n :
                self .bind (case_tests [i +1 ])
        self .bind (default_lbl )
        if default_stmts :
            self .gen_stmts (default_stmts )
        self .pop_break ()
        self .bind (switch_end )

    def parse_args (self ) :
        args =[]
        if self .cur ()!=')' :
            args .append (self .parse_expression ())
            while self .cur ()==',' :
                self .adv ()
                args .append (self .parse_expression ())
        return args

    def parse_factor (self ) :
        if self .cur ()=='(' :
            self .adv ()
            e =self .parse_expression ()
            self .expect (')')
            return e
        if self .cur_type ()==TokenType .NUM :
            v =int (self .cur ())
            self .adv ()
            return ('const' ,v )
        if self .cur_type ()==TokenType .ID :
            name =self .cur ()
            self .adv ()
            if self .cur ()=='(' :
                self .adv ()
                args =self .parse_args ()
                self .expect (')')
                return ('call' ,name ,args )
            if self .cur ()=='[' :
                self .adv ()
                idx =self .parse_expression ()
                self .expect (']')
                return ('elem' ,name ,idx )
            return ('var' ,name )
        raise ValueError (self .cur ())

    def parse_unary (self ) :
        if self .cur ()=='+' :
            self .adv ()
            return self .parse_factor ()
        if self .cur ()=='-' :
            self .adv ()
            operand =self .parse_factor ()
            return ('unary' ,'-' ,operand )
        return self .parse_factor ()

    def parse_term (self ) :
        left =self .parse_unary ()
        while self .cur ()in {'*','/'} :
            op =self .cur ()
            self .adv ()
            right =self .parse_unary ()
            left =('bin' ,op ,left ,right )
        return left

    def parse_additive (self ) :
        left =self .parse_term ()
        while self .cur ()in {'+','-'} :
            op =self .cur ()
            self .adv ()
            right =self .parse_term ()
            left =('bin' ,op ,left ,right )
        return left

    def parse_relational (self ) :
        left =self .parse_additive ()
        if self .cur ()in {'<','=='} :
            op =self .cur ()
            self .adv ()
            right =self .parse_additive ()
            left =('bin' ,op ,left ,right )
        return left

    def continue_binary (self ,left ) :
        while self .cur ()in {'*','/'} :
            op =self .cur ()
            self .adv ()
            right =self .parse_unary ()
            left =('bin' ,op ,left ,right )
        while self .cur ()in {'+','-'} :
            op =self .cur ()
            self .adv ()
            right =self .parse_term ()
            left =('bin' ,op ,left ,right )
        if self .cur ()in {'<','=='} :
            op =self .cur ()
            self .adv ()
            right =self .parse_additive ()
            left =('bin' ,op ,left ,right )
        return left

    def parse_expression (self ) :
        if self .cur_type ()==TokenType .ID :
            name =self .cur ()
            nxt =self .peek ()
            if nxt=='=' :
                self .adv ()
                self .adv ()
                rhs =self .parse_expression ()
                return ('assign' ,('var' ,name ) ,rhs )
            if nxt=='(' :
                self .adv ()
                self .adv ()
                args =self .parse_args ()
                self .expect (')')
                left =('call' ,name ,args )
                return self .continue_binary (left )
            if nxt=='[' :
                self .adv ()
                self .adv ()
                idx =self .parse_expression ()
                self .expect (']')
                if self .cur ()=='=' :
                    self .adv ()
                    rhs =self .parse_expression ()
                    return ('assign' ,('elem' ,name ,idx ) ,rhs )
                left =('elem' ,name ,idx )
                return self .continue_binary (left )
            self .adv ()
            left =('var' ,name )
            return self .continue_binary (left )
        return self .parse_relational ()

    def parse_statement (self ) :
        c =self .cur ()
        if c=='if' :
            self .adv ()
            self .expect ('(')
            cond =self .parse_expression ()
            self .expect (')')
            then =self .parse_statement ()
            els =None
            if self .cur ()=='else' :
                self .adv ()
                els =self .parse_statement ()
            return ('if' ,cond ,then ,els )
        if c=='{' :
            return self .parse_compound ()
        if c=='while' :
            self .adv ()
            self .expect ('(')
            cond =self .parse_expression ()
            self .expect (')')
            body =self .parse_statement ()
            return ('while' ,cond ,body )
        if c=='return' :
            self .adv ()
            if self .cur ()==';' :
                self .adv ()
                return ('return' ,None )
            e =self .parse_expression ()
            if self .cur ()==';' :
                self .adv ()
            return ('return' ,e )
        if c=='break' :
            self .adv ()
            if self .cur ()==';' :
                self .adv ()
            return ('break' ,)
        if c=='goto' :
            self .adv ()
            name =self .cur ()
            self .adv ()
            if self .cur ()==';' :
                self .adv ()
            return ('goto' ,name )
        if c=='switch' :
            return self .parse_switch ()
        if c==';' :
            self .adv ()
            return ('null' ,)
        if c==':' :
            self .adv ()
            return self .parse_statement ()
        if self .cur_type ()==TokenType .ID :
            if self .peek ()==':' :
                name =self .cur ()
                self .adv ()
                self .adv ()
                return ('label' ,name )
            e =self .parse_expression ()
            if self .cur ()==';' :
                self .adv ()
            return ('expr' ,e )
        e =self .parse_expression ()
        if self .cur ()==';' :
            self .adv ()
        return ('expr' ,e )

    def parse_compound (self ) :
        self .expect ('{')
        locals_decl =[]
        while self .cur ()in {'int','void'} :
            locals_decl .append (self .parse_local_decl ())
        stmts =[]
        while self .cur ()!='}' and self .cur ()is not None :
            stmts .append (self .parse_statement ())
        self .expect ('}')
        return ('block' ,locals_decl ,stmts )

    def parse_local_decl (self ) :
        self .adv ()
        name =self .cur ()
        self .adv ()
        if self .cur ()=='[' :
            self .adv ()
            size =int (self .cur ())
            self .adv ()
            self .expect (']')
            init =None
            if self .cur ()=='=' :
                self .adv ()
                init =self .parse_expression ()
            if self .cur ()==';' :
                self .adv ()
            return ('localvar' ,name ,'array' ,size ,init )
        init =None
        if self .cur ()=='=' :
            self .adv ()
            init =self .parse_expression ()
        if self .cur ()==';' :
            self .adv ()
        return ('localvar' ,name ,'scalar' ,1 ,init )

    def parse_switch (self ) :
        self .adv ()
        self .expect ('(')
        cond =self .parse_expression ()
        self .expect (')')
        self .expect ('{')
        cases =[]
        while self .cur ()=='case' :
            self .adv ()
            cval =int (self .cur ())
            self .adv ()
            self .expect (':')
            body =[]
            while self .cur ()not in {'case','default','}'} and self .cur ()is not None :
                body .append (self .parse_statement ())
            cases .append ((cval ,body ))
        default_stmts =[]
        if self .cur ()=='default' :
            self .adv ()
            self .expect (':')
            while self .cur ()!='}' and self .cur ()is not None :
                default_stmts .append (self .parse_statement ())
        self .expect ('}')
        return ('switch' ,cond ,cases ,default_stmts )

    def parse_param_list (self ) :
        params =[]
        if self .cur ()=='void' :
            self .adv ()
            return params
        while self .cur ()=='int' :
            self .adv ()
            name =self .cur ()
            self .adv ()
            kind ='scalar'
            if self .cur ()=='[' :
                self .adv ()
                self .expect (']')
                kind ='array'
            params .append ((name ,kind ))
            if self .cur ()==',' :
                self .adv ()
                continue
            break
        return params

    def parse_declaration_list (self ) :
        decls =[]
        while self .cur ()in {'int','void'} :
            self .adv ()
            name =self .cur ()
            self .adv ()
            if self .cur ()=='(' :
                rettype =self .tokens [self .pos -2 ][1 ]
                self .adv ()
                params =self .parse_param_list ()
                self .expect (')')
                body =self .parse_compound ()
                decls .append (('func' ,name ,rettype ,params ,body ))
            else :
                if self .cur ()=='[' :
                    self .adv ()
                    size =int (self .cur ())
                    self .adv ()
                    self .expect (']')
                    init =None
                    if self .cur ()=='=' :
                        self .adv ()
                        init =self .parse_expression ()
                    if self .cur ()==';' :
                        self .adv ()
                    decls .append (('globalvar' ,name ,'array' ,size ,init ))
                else :
                    init =None
                    if self .cur ()=='=' :
                        self .adv ()
                        init =self .parse_expression ()
                    if self .cur ()==';' :
                        self .adv ()
                    decls .append (('globalvar' ,name ,'scalar' ,1 ,init ))
        return decls

    def generate_function (self ,fname ) :
        f =self .functions [fname ]
        self .current_owner =fname
        self .current_list =self .lists [fname ]
        self .current_func =f
        self .local_vars ={}
        self .labels ={}
        for (pname ,pkind ) ,pc in zip (f ['params'] ,f ['param_cells']) :
            self .local_vars [pname ]={'kind':pkind ,'addr':pc ,'size':1 ,'param':True }
        self .bind (f ['entry'])
        body =f ['body']
        for ld in body [1 ] :
            self .gen_local_decl (ld )
        self .break_stack =[]
        self .gen_stmts (body [2 ])
        if not f ['is_main'] :
            self .emit ('JP' ,'@'+str (f ['return_slot']))

    def resolve_operand (self ,o ) :
        if o is None :
            return ''
        if isinstance (o ,_TacLabel ) :
            return str (self .offset [o .owner ]+o .index )
        if isinstance (o ,_TacRetAddr ) :
            return '#'+str (self .offset [o .owner ]+o .local )
        return str (o )

    def run (self ) :
        sc =Scanner (self .input_file )
        sc .read_input ()
        while True :
            t =sc .get_next_token ()
            if t is None :
                break
            self .tokens .append ((t [1 ] ,t [2 ]))
        decls =self .parse_declaration_list ()
        for d in decls :
            if d [0 ]=='globalvar' :
                _,name ,kind ,size ,init =d
                if kind=='array' :
                    self .globals [name ]={'kind':'array','addr':self .global_next ,'size':size ,'param':False }
                    self .global_next +=size
                else :
                    self .globals [name ]={'kind':'scalar','addr':self .global_next ,'size':1 ,'param':False }
                    self .global_next +=1
            else :
                _,name ,rettype ,params ,body =d
                ret_slot =self .global_next
                self .global_next +=1
                out_slot =self .global_next
                self .global_next +=1
                param_cells =[]
                for (pname ,pkind ) in params :
                    pc =self .global_next
                    self .global_next +=1
                    param_cells .append (pc )
                entry =_TacLabel (name )
                self .functions [name ]={'name':name ,'rettype':rettype ,'params':params ,'param_cells':param_cells ,
                'return_slot':ret_slot ,'output_slot':out_slot ,'body':body ,'entry':entry ,
                'is_main':(name =='main')}
        self .addr_counter =self .global_next
        self .lists ['__global__']=[]
        self .owner_order =['__global__']
        self .current_owner ='__global__'
        self .current_list =self .lists ['__global__']
        for d in decls :
            if d [0 ]=='globalvar' and d [1 ]not in self .functions :
                info =self .globals [d [1 ]]
                if info ['kind']=='array' :
                    for k in range (info ['size']) :
                        self .emit ('ASSIGN' ,'#0' ,str (info ['addr']+k ))
                else :
                    self .emit ('ASSIGN' ,'#0' ,str (info ['addr']))
        for d in decls :
            if d [0 ]=='globalvar' :
                if d [4 ] is not None :
                    name =d [1 ]
                    if d [3 ]=='scalar' :
                        value =self .gen_expr (d [4 ])
                        self .emit ('ASSIGN' ,value ,str (self .globals [name ]['addr']))
                    else :
                        value =self .gen_expr (d [4 ])
                        addr =self .compute_elem_addr (self .globals [name ],'#0' )
                        self .emit ('ASSIGN' ,value ,'@'+str (addr ))
        self .emit ('JP' ,self .functions ['main']['entry'])
        for fname in self .functions :
            if fname !='main' :
                self .owner_order .append (fname )
                self .lists [fname ]=[]
        self .owner_order .append ('main')
        self .lists ['main']=[]
        for fname in self .owner_order :
            if fname !='__global__' :
                self .generate_function (fname )
        self .assemble ()

    def assemble (self ) :
        cur =0
        for own in self .owner_order :
            self .offset [own ]=cur
            cur +=len (self .lists [own ])
        final =[]
        for own in self .owner_order :
            for row in self .lists [own ] :
                op ,a ,b ,c =row
                final .append ((op ,
                self .resolve_operand (a ),
                self .resolve_operand (b ),
                self .resolve_operand (c )))
        lines =[]
        for i ,row in enumerate (final ) :
            lines .append ("{}\t({}, {}, {}, {})".format (i ,row [0 ] ,row [1 ] ,row [2 ] ,row [3 ]))
        with open (self .output_file ,'w' ,encoding ='utf-8') as f :
            f .write ("\n".join (lines )+"\n")

def write_output_files (parse_tree_root ,syntax_errors ,parse_tree_file ='parse_tree.txt',errors_file ='syntax_errors.txt'):
    tree_string =generate_parse_tree_string (parse_tree_root )
    with open (parse_tree_file ,'w',encoding ='utf-8',newline ='')as f :
        f .write (tree_string +"\n")

    with open (errors_file ,'w',encoding ='utf-8',newline ='')as f :
        if not syntax_errors :
            f .write ("There is no syntax error.\n")
        else :
            for error in syntax_errors :
                f .write (error +"\n")

def main ():
    parser =Parser ('input.txt')
    parser .parse ()
    write_output_files (parser .root ,parser .syntax_errors )
    try :
        cg =CodeGenerator ('input.txt')
        cg .run ()
    except Exception as e :
        print ("Code generation error: {}".format (e ))
    print ("Compilation completed successfully.")
    print ("Syntax errors: {}".format (len (parser .syntax_errors )))

if __name__ =="__main__":
    main ()
