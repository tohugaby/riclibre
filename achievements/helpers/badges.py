"""
Achievements app: badge description and methods module
"""

from importlib import import_module

from riclibre.helpers.model_watcher import Register


def get_achievements():
    """
    Get achievements from all models of project.
    :return: a dict of achievements
    """
    achievements = dict()
    for model_name, module_name in Register.WATCHED_MODELS:
        module = import_module(module_name)
        model = getattr(module, model_name)
        if hasattr(model, 'ACHIEVEMENTS'):
            achievements.update(model.ACHIEVEMENTS)
    return achievements


BADGES = sorted([(key, key) for key in get_achievements().keys()])
