"""
Referendum's app: Custom errors
"""


class UserHasAlreadyVotedError(Exception):
    """Raised when a user try to vote more than one time to the same referendum"""
    pass
