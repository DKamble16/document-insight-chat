from django_extensions.management.shells import *


def patched_import_objects(options, style):
    from django.apps import apps
    from django import setup

    if not apps.ready:
        setup()

    from django.conf import settings

    dont_load_cli = options.get('dont_load', [])
    dont_load_conf = getattr(settings, 'SHELL_PLUS_DONT_LOAD', [])
    dont_load = dont_load_cli + dont_load_conf
    dont_load_any_models = '*' in dont_load
    quiet_load = options.get('quiet_load')
    model_aliases = getattr(settings, 'SHELL_PLUS_MODEL_ALIASES', {})
    app_prefixes = getattr(settings, 'SHELL_PLUS_APP_PREFIXES', {})
    SHELL_PLUS_PRE_IMPORTS = getattr(settings, 'SHELL_PLUS_PRE_IMPORTS', {})

    imported_objects = {}
    load_models = {}

    def get_dict_from_names_to_possible_models():  # type: () -> Dict[str, List[str]]
        """
        Collect dictionary from names to possible models. Model is represented as his full path.
        Name of model can be alias if SHELL_PLUS_MODEL_ALIASES or SHELL_PLUS_APP_PREFIXES is specified for this model.
        This dictionary is used by collision resolver.
        At this phase we can't import any models, because collision resolver can change results.
        :return: Dict[str, List[str]]. Key is name, value is list of full model's path's.
        """
        models_to_import = {}  # type: Dict[str, List[str]]
        for app_mod, models in sorted(load_models.items()):
            app_name = get_app_name(app_mod)
            app_aliases = model_aliases.get(app_name, {})
            prefix = app_prefixes.get(app_name)

            for model_name in sorted(models):
                if "%s.%s" % (app_name, model_name) in dont_load:
                    continue

                alias = app_aliases.get(model_name)

                if not alias:
                    if prefix:
                        alias = "%s_%s" % (prefix, model_name)
                    else:
                        alias = model_name

                models_to_import.setdefault(alias, [])
                models_to_import[alias].append("%s.%s" % (app_mod, model_name))
        return models_to_import

    def import_subclasses():
        base_classes_to_import = getattr(settings, 'SHELL_PLUS_SUBCLASSES_IMPORT', [])  # type: List[Union[str, type]]
        if base_classes_to_import:
            if not quiet_load:
                print(style.SQL_TABLE("# Shell Plus Subclasses Imports"))
            perform_automatic_imports(SubclassesFinder(base_classes_to_import).collect_subclasses())

    def import_models():
        """
        Perform collision resolving and imports all models.
        When collisions are resolved we can perform imports and print information's, because it is last phase.
        This function updates imported_objects dictionary.
        """
        modules_to_models = CollisionResolvingRunner().run_collision_resolver(get_dict_from_names_to_possible_models())
        perform_automatic_imports(modules_to_models)

    def perform_automatic_imports(modules_to_classes):  # type: (Dict[str, List[Tuple[str, str]]]) -> ()
        """
        Import elements from given dictionary.
        :param modules_to_classes: dictionary from module name to tuple.
        First element of tuple is model name, second is model alias.
        If both elements are equal than element is imported without alias.
        """
        for full_module_path, models in modules_to_classes.items():
            model_labels = []
            for (model_name, alias) in sorted(models):
                try:
                    imported_objects[alias] = import_string("%s.%s" % (full_module_path, model_name))
                    if model_name == alias:
                        model_labels.append(model_name)
                    else:
                        model_labels.append("%s (as %s)" % (model_name, alias))
                except ImportError as e:
                    if options.get("traceback"):
                        traceback.print_exc()
                    if not options.get('quiet_load'):
                        print(style.ERROR(
                            "Failed to import '%s' from '%s' reason: %s" % (model_name, full_module_path, str(e))))
            if not options.get('quiet_load'):
                print(style.SQL_COLTYPE("from %s import %s" % (full_module_path, ", ".join(model_labels))))

    def get_apps_and_models():
        for app in apps.get_app_configs():
            # <<<<< patched to use app.module if app.models_module is not defined so shell works with single file app
            module = app.models_module or app.module
            if module:
                yield module, app.get_models()

    mongoengine = False
    try:
        from mongoengine.base import _document_registry
        mongoengine = True
    except ImportError:
        pass

    # Perform pre-imports before any other imports
    if SHELL_PLUS_PRE_IMPORTS:
        if not quiet_load:
            print(style.SQL_TABLE("# Shell Plus User Pre Imports"))
        imports = import_items(SHELL_PLUS_PRE_IMPORTS, style, quiet_load=quiet_load)
        for k, v in imports.items():
            imported_objects[k] = v

    if mongoengine and not dont_load_any_models:
        for name, mod in _document_registry.items():
            name = name.split('.')[-1]
            app_name = get_app_name(mod.__module__)
            if app_name in dont_load or ("%s.%s" % (app_name, name)) in dont_load:
                continue

            load_models.setdefault(mod.__module__, [])
            load_models[mod.__module__].append(name)

    if not dont_load_any_models:
        for app_mod, app_models in get_apps_and_models():
            if not app_models:
                continue

            app_name = get_app_name(app_mod.__name__)
            if app_name in dont_load:
                continue

            for mod in app_models:
                if "%s.%s" % (app_name, mod.__name__) in dont_load:
                    continue

                if mod.__module__:
                    # Only add the module to the dict if `__module__` is not empty.
                    load_models.setdefault(mod.__module__, [])
                    load_models[mod.__module__].append(mod.__name__)

    import_subclasses()
    if not quiet_load:
        print(style.SQL_TABLE("# Shell Plus Model Imports%s") % (' SKIPPED' if dont_load_any_models else ''))

    import_models()

    # Imports often used from Django
    if getattr(settings, 'SHELL_PLUS_DJANGO_IMPORTS', True):
        if not quiet_load:
            print(style.SQL_TABLE("# Shell Plus Django Imports"))
        imports = import_items(SHELL_PLUS_DJANGO_IMPORTS, style, quiet_load=quiet_load)
        for k, v in imports.items():
            imported_objects[k] = v

    SHELL_PLUS_IMPORTS = getattr(settings, 'SHELL_PLUS_IMPORTS', {})
    if SHELL_PLUS_IMPORTS:
        if not quiet_load:
            print(style.SQL_TABLE("# Shell Plus User Imports"))
        imports = import_items(SHELL_PLUS_IMPORTS, style, quiet_load=quiet_load)
        for k, v in imports.items():
            imported_objects[k] = v

    # Perform post-imports after any other imports
    SHELL_PLUS_POST_IMPORTS = getattr(settings, 'SHELL_PLUS_POST_IMPORTS', {})
    if SHELL_PLUS_POST_IMPORTS:
        if not quiet_load:
            print(style.SQL_TABLE("# Shell Plus User Post Imports"))
        imports = import_items(SHELL_PLUS_POST_IMPORTS, style, quiet_load=quiet_load)
        for k, v in imports.items():
            imported_objects[k] = v

    return imported_objects

import django_extensions.management.shells
django_extensions.management.shells.import_objects = patched_import_objects
