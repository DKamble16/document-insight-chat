import os
import re
import sys
from importlib import import_module


def find_root_module():
    cwd = os.path.abspath(os.getcwd())
    sys.path.append(cwd)
    os.listdir()
    files = [f for f in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, f)) and f.endswith('.py')]
    for file in files:
        with open(file, 'r') as f:
            text = f.read()
            if 'from rag import Application' in text or 'rag.Application' in text:
                return file[:-3] # remove .py
    return None

def import_root_module():
    module = find_root_module()
    if not module:
        raise RuntimeError('No root application module specified and unable to find module.')
    return import_module(module)

def find_asgi_path():
    root = find_root_module()
    with open(f'{root}.py', 'r') as f:
        text = f.read()
    app = re.search(r'(?P<app>\w+)\W=\W(?:Application)', text).group('app')
    if not app:
        raise RuntimeError(f'Unable to find root Rag application. Searched: {root}')
    return f'{root}:{app}.router'
