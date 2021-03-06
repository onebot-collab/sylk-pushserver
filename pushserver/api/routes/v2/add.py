from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse

from pushserver.models.requests import AddRequest, fix_platform_name, AddResponse
from pushserver.resources import settings
from pushserver.resources.storage import TokenStorage
from pushserver.resources.storage.errors import StorageError
from pushserver.resources.utils import (check_host,
                                        log_event, log_add_request)

router = APIRouter()


@router.post('/{account}', response_model=AddResponse)
async def add_requests(account: str,
                       request: Request,
                       add_request: AddRequest,
                       background_tasks: BackgroundTasks):

    add_request.platform = fix_platform_name(add_request.platform)

    host, port = request.client.host, request.client.port

    code, description, data = '', '', {}

    if check_host(host, settings.params.allowed_pool):
        request_id = f"{account}-{add_request.app_id}-{add_request.device_id}"
        if not settings.params.return_async:
            background_tasks.add_task(log_add_request, task='log_request',
                                      host=host, loggers=settings.params.loggers,
                                      request_id=request_id, body=add_request.__dict__)

            background_tasks.add_task(log_add_request, task='log_success',
                                      host=host, loggers=settings.params.loggers,
                                      request_id=request_id, body=add_request.__dict__)

            storage = TokenStorage()
            background_tasks.add_task(storage.add, account, add_request)

            return add_request
        else:
            log_add_request(task='log_request',
                            host=host, loggers=settings.params.loggers,
                            request_id=request_id, body=add_request.__dict__)

            storage = TokenStorage()
            try:
                storage.add(account, add_request)
            except StorageError:
                error = HTTPException(status_code=500, detail="Internal error: storage")
                log_add_request(task='log_failure',
                                host=host, loggers=settings.params.loggers,
                                request_id=request_id, body=add_request.__dict__,
                                error_msg=f'500: {{\"detail\": \"{error.detail}\"}}')
                raise error

            log_add_request(task='log_success',
                            host=host, loggers=settings.params.loggers,
                            request_id=request_id, body=add_request.__dict__)
            return add_request
    else:
        msg = f'incoming request from {host} is denied'
        log_event(loggers=settings.params.loggers,
                  msg=msg, level='deb')
        code = 403
        description = 'access denied by access list'
        data = {}

        log_event(loggers=settings.params.loggers,
                  msg=msg, level='deb')

    return JSONResponse(status_code=code, content={'code': code,
                                                   'description': description,
                                                   'data': data})
