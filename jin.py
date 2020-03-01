from jinja2 import Environment
from jinja2.lexer import TokenStream, Token, TOKEN_DATA, TOKEN_VARIABLE_BEGIN, TOKEN_NAME, TOKEN_VARIABLE_END
from jinja2.ext import Extension
import re
# --meta prefix=X
DEF_PREFIX = '!'
ARG_RE_TMPL = r'''
    (?<!!)(:?
        \s*
            (:?{prefix})
        \s*
    )
    (?P<name>\w+) # name of arg after prefix
    |
    (?P<double>{prefix}\s*{prefix}) # or double prefix for escape
'''
DEF_ARG_RE = re.compile(ARG_RE_TMPL.format(prefix=DEF_PREFIX), re.VERBOSE)

class SQL(Extension):
    arg_re = DEF_ARG_RE
    def arg_tokenizer(self, token:Token):
        for mo in DEF_ARG_RE.finditer(token.value):
            print(mo)
            print(mo['name'], mo['double'])

        yield token
        return

        if not mo:
            yield token
            return
        while mo:
            if mo.lastgroup == 'double':
                yield Token(token.lineno, TOKEN_DATA, DEF_PREFIX)
            else:
                yield from (
                    Token(token.lineno, TOKEN_VARIABLE_BEGIN, "{{"),
                    Token(token.lineno, TOKEN_NAME, mo['name']),
                    Token(token.lineno, TOKEN_VARIABLE_END, "}}"),
                )
            mo = DEF_ARG_RE.search(token.value, mo.endpos)

    def filter_stream(self, stream:TokenStream):
        """
        jinja stream hook
        """
        return TokenStream(
            self._arg_substitute(stream),
            stream.name,
            stream.filename
        )

    def _arg_substitute(self, stream):
        """
        stream gen
        """
        for token in stream:
            if token.type == TOKEN_DATA:
                yield from self.arg_tokenizer(token)
            else:
                yield token
            

env = Environment(extensions=[SQL])
tmpl  = """SELECT !a1, !b1, !!a2"""
template = env.from_string(tmpl)
s=template.render(a=1, b=2)
print(s)
