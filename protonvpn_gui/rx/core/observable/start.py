from typing import Optional, Callable

from ... import to_async
from ...core import Observable
from ...core.typing import Scheduler


def _start(func: Callable, scheduler: Optional[Scheduler] = None) -> Observable:
    """Invokes the specified function asynchronously on the specified
    scheduler, surfacing the result through an observable sequence.

    Example:
        >>> res = ...start(lambda: pprint('hello'))
        >>> res = ...start(lambda: pprint('hello'), ...Scheduler.timeout)

    Args:
        func: Function to run asynchronously.
        scheduler: [Optional] Scheduler to run the function on. If
            not specified, defaults to Scheduler.timeout.

    Remarks:
        The function is called immediately, not during the subscription
        of the resulting sequence. Multiple subscriptions to the
        resulting sequence can observe the function's result.

    Returns:
        An observable sequence exposing the function's result value,
        or an exception.
    """

    return to_async(func, scheduler)()
