from typing import (
    NamedTuple,
    Optional,
)


ReceivedMessage = NamedTuple('ReceivedMessage', [
    ('sender_psid', str),
    ('text', str),
    ('payload', Optional[str]),
])

