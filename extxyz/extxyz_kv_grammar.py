'''extxyz key=value Grammar.'''
from pyleri import (Ref, Choice, Grammar, Regex, Keyword, Optional,
                    Repeat, Sequence, List)

# These regexs are defined outside grammar so they can be reused
properties_val_re = '([a-zA-Z_][a-zA-Z_0-9]*):([RILS]):([0-9]+)'
simplestring_re = r'\S*'
quotedstring_re = r'(")(?:(?=(\\?))\2.)*?\1'
barestring_re = r"""(?:[^\s='",}{\]\[\\]|(?:\\[\s='",}{\]\]\\]))+"""
float_re = r'[+-]?(?:[0-9]+[.]?[0-9]*|\.[0-9]+)(?:[dDeE][+-]?[0-9]+)?'
integer_re = r'[+-]?[0-9]+'
bool_re = r'[TF]'
whitespace_re = r'\s*'

class ExtxyzKVGrammar(Grammar):
    # string without quotes, some characters must be escaped 
    # <whitespace>='",}{][\
    r_barestring = Regex(barestring_re)
    r_quotedstring = Regex(quotedstring_re)
    r_string = Choice(r_barestring, r_quotedstring)

    r_integer = Regex(integer_re)
    r_float = Regex(float_re)

    k_true = Keyword('T')
    k_false = Keyword('F')

    ints = List(r_integer, mi=1)
    floats = List(r_float, mi=1)
    bools = List(Choice(k_true, k_false), mi=1)
    strings = List(r_string, mi=1)

    ints_sp = Repeat(r_integer, mi=1)
    floats_sp = Repeat(r_float, mi=1)
    bools_sp = Repeat(Choice(k_true, k_false), mi=1)
    strings_sp = Repeat(r_string, mi=1)

    old_one_d_array = Choice(Sequence('"', Choice(ints_sp, floats_sp, bools_sp), '"'),
                             Sequence('{', Choice(ints_sp, floats_sp, bools_sp, strings_sp), '}'))
    one_d_array = Sequence('[', Choice(ints, floats, strings, bools), ']')
    one_d_arrays = List(one_d_array, mi=1)
    two_d_array = Sequence('[', one_d_arrays, ']')

    key_item = Choice(r_string)

    val_item = Choice(
        r_integer,
        r_float,
        k_true,
        k_false,
        old_one_d_array,
        one_d_array,
        two_d_array,
        r_string)

    kv_pair = Sequence(key_item, '=', val_item, Regex(r'\s*'))
   
    properties = Keyword('Properties', ign_case=True)
    properties_val_str = Regex(rf'^{properties_val_re}(:{properties_val_re})*')
    properties_kv_pair = Sequence(properties, '=', 
                                  properties_val_str, Regex(r'\s*'))
    
    all_kv_pair = Choice(properties_kv_pair, kv_pair, most_greedy=False)

    START = Repeat(all_kv_pair)

if __name__ == '__main__':
    src, hdr = ExtxyzKVGrammar().export_c( target='extxyz_kv_grammar', c_indent=' ' * 4)
    with open('extxyz_kv_grammar.c', 'w') as fsrc, open('extxyz_kv_grammar.h', 'w') as fhdr:
        fsrc.write(src)
        fhdr.write(hdr)