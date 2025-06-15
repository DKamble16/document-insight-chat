import sys
from pathlib import Path
from poetry.factory import Factory
from poetry.utils.env import EnvManager

def run_script(env, script, args):
    module, callable_ = script.split(":")
    # src_in_sys_path = "sys.path.append('src'); " if self._module.is_in_src() else ""
    cmd = ["python", "-c"]
    cmd += [
        "import sys; "
        "from importlib import import_module; "
        "sys.argv = {!r};"
        "import_module('{}').{}()".format(args, module, callable_)
    ]
    return env.execute(*cmd)

def proxy(script, args):
    poetry = Factory().create_poetry(Path.cwd())
    env = EnvManager(poetry).get()
    return run_script(env, script, args)

def main():
    proxy('rag.cli.main:main', sys.argv)

# should this function even without poetry? we could load rag without it.
# check that we have poetry installed?
# check that rag is installed in poetry env?
