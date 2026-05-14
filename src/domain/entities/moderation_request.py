from dataclasses import dataclass

@dataclass(frozen=True)
class ModerationRequest:
    user_id: str
    text: str

    def __post_init__(self):
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        if not self.text:
            raise ValueError("text cannot be empty")
