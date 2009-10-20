import os
from django.core.management.base import NoArgsCommand
from optparse import make_option

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--plain', action='store_true', dest='plain',
            help='Tells Django to use plain Python, not IPython.'),
    )
    help = "Runs a Python interactive interpreter. Tries to use IPython, if it's available."

    requires_model_validation = False

    def handle_noargs(self, **options):
        # XXX: (Temporary) workaround for ticket #1796: force early loading of all
        # models from installed apps.
        from django.db.models.loading import get_models, get_apps
        loaded_models = get_models()

        use_plain = options.get('plain', False)

        from django.conf import settings
        imported_objects = {'settings': settings}
        
        import_messages = []
        for app_mod in get_apps():
            app_models = get_models(app_mod)
            if not app_models:
                continue
            model_labels = ", ".join([model.__name__ for model in app_models])
            import_messages.append("Models from '%s': %s" % (app_mod.__name__.split('.')[-2], model_labels))
            for model in app_models:
                try:
                    imported_objects[model.__name__] = getattr(__import__(app_mod.__name__, {}, {}, model.__name__), model.__name__)
                except AttributeError, e:
                    import_messages.append("Failed to import '%s' from '%s': %s" % (model.__name__, app_mod.__name__.split('.')[-2], str(e)))
                    continue

        try:
            if use_plain:
                # Don't bother loading IPython, because the user wants plain Python.
                raise ImportError
            try:
                from tempfile import mkstemp
                _, tmp_name = mkstemp(suffix='.py')
                tmp = open(tmp_name, 'w')
                tmp.write("\n".join((('raise Warning, "%s"' if line.startswith("Failed") else 'print "%s"') % line for line in import_messages)))
                tmp.close()
                from bpython import cli
                cli.main(args=['--interactive', tmp_name], locals_=imported_objects)
                os.unlink(tmp_name)
            except ImportError:
                import IPython
                # Explicitly pass an empty list as arguments, because otherwise IPython
                # would use sys.argv from this script.
                shell = IPython.Shell.IPShell(argv=[])
                shell.mainloop()
        except ImportError:
            import code
            # Set up a dictionary to serve as the environment for the shell, so
            # that tab completion works on objects that are imported at runtime.
            # See ticket 5082.
            imported_objects = {}
            try: # Try activating rlcompleter, because it's handy.
                import readline
            except ImportError:
                pass
            else:
                # We don't have to wrap the following import in a 'try', because
                # we already know 'readline' was imported successfully.
                import rlcompleter
                readline.set_completer(rlcompleter.Completer(imported_objects).complete)
                readline.parse_and_bind("tab:complete")

            # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
            # conventions and get $PYTHONSTARTUP first then import user.
            if not use_plain: 
                pythonrc = os.environ.get("PYTHONSTARTUP") 
                if pythonrc and os.path.isfile(pythonrc): 
                    try: 
                        execfile(pythonrc) 
                    except NameError: 
                        pass
                # This will import .pythonrc.py as a side-effect
                import user
            code.interact(local=imported_objects)
