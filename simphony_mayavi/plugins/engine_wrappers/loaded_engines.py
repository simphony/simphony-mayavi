from stevedore import extension


def get_loaded_engines():
    ''' Return the extension names in simphony.engine '''
    mgr = extension.ExtensionManager(
        namespace="simphony.engine",
        invoke_on_load=False)
    return tuple(extension.name for extension in mgr.extensions)


LOADED_ENGINES = get_loaded_engines()
