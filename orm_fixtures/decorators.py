def require_fixtures(*fixtures):
    """
    Adds the named fixtures to the list of requirements for this fixture.
    """
    def decorator(func):
        func._requires = fixtures
        return func
    return decorator
