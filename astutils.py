def inject_into(module):
    """
    Adds all methods of the given class to the classes of the `ast` module.
    A method `Call_translate` is added to class `Call` as method `translate`.
    """
    def inner(cls):
        for k, v in cls.__dict__.items():
            if k[0] == '_': continue
            m, n = k.split('_', 1)
            setattr(getattr(module, m), n, v)
    return inner
