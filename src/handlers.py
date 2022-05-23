import logging
from json import JSONDecodeError

from fastapi.exceptions import RequestValidationError
from pydantic import (
    PydanticTypeError,
    MissingError,
)
from pydantic.error_wrappers import (
    ErrorWrapper,
    ValidationError,
)
from starlette import status
from starlette.requests import Request
from starlette.responses import (
    JSONResponse,
    PlainTextResponse,
)


logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_response = {
        "detail": "Unexpected error",
    }
    invalid_type = []
    field_required = []
    for arg in exc.args:
        if isinstance(arg, list):
            for items in arg:
                if isinstance(items, ErrorWrapper):
                    if isinstance(items.exc, PydanticTypeError):
                        loc_type = items.loc_tuple()[0]
                        if "path" == loc_type:
                            # If error in on the path, the response will be 404
                            if request.method == "DELETE":
                                return PlainTextResponse(status_code=status.HTTP_404_NOT_FOUND)
                            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Not Found"})
                        elif "query" == loc_type:
                            invalid_type.append(items.loc_tuple()[1])
                        else:
                            logger.exception("Unsupported type for {}".format(items.exc))
                    elif isinstance(items.exc, MissingError):
                        error_response["detail"] = "Payload required"
                    elif isinstance(items.exc, ValidationError):
                        for error in items.exc.errors():
                            error_type = error.get("type", "")
                            if error_type.startswith("value_error"):
                                field_required.append(error.get("loc")[0])
                            elif error_type.startswith("type_error"):
                                invalid_type.append(error.get("loc")[0])
                    elif isinstance(items.exc, JSONDecodeError):
                        error_response["detail"] = "Invalid payload"
                    else:
                        logger.exception("Unsupported exception for {}".format(items.exc))
                else:
                    logger.exception("Unsupported item for {}".format(items))
        else:
            logger.exception("Unsupported type for {}".format(arg))

    invalid_type_msg = ""
    if invalid_type:
        invalid_type_msg = "Invalid type{} in {}".format(
            "s" if len(invalid_type) > 1 else "",
            " ".join(invalid_type),
        )
    field_required_msg = ""
    if field_required:
        field_required_msg = "Field{} {} required".format(
            "s" if len(field_required) > 1 else "",
            " ".join(field_required),
        )

    if all([invalid_type_msg, field_required_msg]):
        error_response["detail"] = "\n".join([invalid_type_msg, field_required_msg])
    elif invalid_type_msg:
        error_response["detail"] = invalid_type_msg
    elif field_required_msg:
        error_response["detail"] = field_required_msg

    return JSONResponse(status_code=400, content=error_response)
