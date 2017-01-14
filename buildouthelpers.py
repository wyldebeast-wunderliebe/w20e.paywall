WSGISCRIPT_TEMPLATE = """\
# -*- coding: utf-8 -*-
import sys
import os
sys.path[0:0] = [
{0}
]
_application = None
def application(environ, start_response):
    global _application
    # Potential app environment setup
    if _application is None:
        from {1} import {2} as _application
    return _application(environ, start_response)
"""

def make_wsgi_script(recipe, buildout):
    """Build the script for Apache/mod_wsgi
    """
    # Late import: zc.recipe.egg may not be installed when executing 1st
    # function
    from zc.recipe.egg.egg import Eggs
    app_egg = recipe['egg']
    wsgi_filepath = recipe['script']
    app_mod, app_obj = recipe['app'].rsplit('.', 1)  # 'a.b.c.d' -> 'a.b.c', 'd'

    reqs, ws = Eggs(buildout, app_egg, recipe).working_set()
    egg_paths = [pkg.location for pkg in ws]
    src_egg_paths = ',\n'.join(["    '{0}'".format(path) for path in egg_paths])
    with open(wsgi_filepath, 'w') as fh:
        fh.write(WSGISCRIPT_TEMPLATE.format(src_egg_paths, app_mod, app_obj))
    return
