from typing import Callable, Optional

from ... import operators as ops, empty, timer
from ...core import Observable, typing


def _delay_subscription(duetime: typing.AbsoluteOrRelativeTime,
                        scheduler: Optional[typing.Scheduler] = None
                        ) -> Callable[[Observable], Observable]:
    def delay_subscription(source: Observable) -> Observable:
        """Time shifts the observable sequence by delaying the subscription.

        Examples.
            >>> res = source.delay_subscription(5)

        Args:
            source: Source subscription to delay.

        Returns:
            Time-shifted sequence.
        """

        def mapper(_) -> Observable:
            return empty()

        return source.pipe(
            ops.delay_with_mapper(timer(duetime, scheduler=scheduler), mapper)
        )
    return delay_subscription
