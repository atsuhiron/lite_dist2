class LD2Error(Exception):
    pass


class LD2ModelTypeError(LD2Error):
    def __init__(self, type_name: str) -> None:
        super().__init__(f"Unknown type: {type_name}")
