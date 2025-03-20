from pydantic import BaseModel


class Mapping[TParam, TResult](BaseModel):
    param: TParam
    result: TResult


class Trial(BaseModel):
    parameter_range: ParameterRange
    result: list[Mapping]