from invoke import Collection
import re
from typing import List
from typing import Optional


def compose_collection(
    ns: Collection,
    ns_add: Collection,
    sub: bool = True,  # If True, added as sub-collection.
                       # If False, tasks added to collection.
    name: Optional[str] = None,  # If added as sub-collection, name for the sub-collection.
    include: List[str] = ['.*'],  # Collections or tasks to include in the composition.
                                  # Currently only applied to immediate children.
    exclude: List[str] = [],  # Collections or tasks to exclude from the composition.
                              # Currently only applied to immediate children.
                              # Exclusions take priority over inclusions.
):
    """
    Compose a Collection by adding elements of another Collection.
    """

    # Check any invalid parameters
    if (not sub) and (name is not None):
        raise ValueError('Invalid combination for sub and name.')

    # Any configuration is propagated to the existing Collection
    ns.configure(ns_add.configuration())

    # Create a collection to hold results of applying inclusion and exclusion patterns
    if not ns_add.name:
        ns_included = Collection()
    else:
        ns_included = Collection(ns_add.name)

    # First apply to tasks
    for name_current, task_current in ns_add.tasks.items():
        include_current = False

        for pattern_current in include:
            include_current |= re.fullmatch(pattern=pattern_current, string=name_current) is not None
        for pattern_current in exclude:
            include_current &= re.fullmatch(pattern=pattern_current, string=name_current) is None

        if include_current:
            ns_included.add_task(task_current, name=name_current)

    # Then apply to any sub-collections
    for name_current, collection_current in ns_add.collections.items():
        include_current = False

        for pattern_current in include:
            include_current |= re.fullmatch(pattern=pattern_current, string=name_current) is not None
        for pattern_current in exclude:
            include_current &= re.fullmatch(pattern=pattern_current, string=name_current) is None

        if include_current:
            ns_included.add_collection(collection_current, name=name_current)

    if sub:
        # A sub-collection is added
        if not name:
            ns.add_collection(ns_included)
        else:
            ns.add_collection(ns_included, name=name)
    else:
        # Add elements of the collection directly to the existing collection
        for name_current, task_current in ns_included.tasks.items():
            ns.add_task(task_current, name=name_current)
        for name_current, collection_current in ns_included.collections.items():
            ns.add_collection(collection_current, name=name_current)
