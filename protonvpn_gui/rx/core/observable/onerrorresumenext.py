from typing import Union
from asyncio import Future

from ... import from_future
from ...scheduler import CurrentThreadScheduler
from ...core import Observable
from ...disposable import CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from ...internal.utils import is_future


def _on_error_resume_next(*sources: Union[Observable, Future]) -> Observable:
    """Continues an observable sequence that is terminated normally or
    by an exception with the next observable sequence.

    Examples:
        >>> res = ...on_error_resume_next(xs, ys, zs)

    Returns:
        An observable sequence that concatenates the source sequences,
        even if a sequence terminates exceptionally.
    """

    sources_ = iter(sources)

    def subscribe(observer, scheduler=None):

        scheduler = scheduler or CurrentThreadScheduler.singleton()

        subscription = SerialDisposable()
        cancelable = SerialDisposable()

        def action(scheduler, state=None):
            try:
                source = next(sources_)
            except StopIteration:
                observer.on_completed()
                return

            # Allow source to be a factory method taking an error
            source = source(state) if callable(source) else source
            current = from_future(source) if is_future(source) else source

            d = SingleAssignmentDisposable()
            subscription.disposable = d

            def on_resume(state=None):
                scheduler.schedule(action, state)

            d.disposable = current.subscribe_(observer.on_next, on_resume, on_resume, scheduler)

        cancelable.disposable = scheduler.schedule(action)
        return CompositeDisposable(subscription, cancelable)
    return Observable(subscribe)
