class LD2Error(Exception):
    pass


class LD2ModelTypeError(LD2Error):
    def __init__(self, type_name: str) -> None:
        super().__init__(f"Unknown type: {type_name}")


class LD2ParameterError(LD2Error):
    def __init__(self, target_param: str, error_type: str) -> None:
        super().__init__(f"Invalid parameter: {target_param}; Error type: {error_type}")


class LD2UndefinedError(LD2Error):
    def __init__(self, name: str) -> None:
        super().__init__(f"Undefined: {name}")


class LD2InvalidSpaceError(LD2Error):
    def __init__(self, msg: str) -> None:
        super().__init__(f"Invalid space: {msg}")
