from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import JSONResponse

from pushserver.models.requests import RemoveRequest, RemoveResponse
from pushserver.resources import settings
from pushserver.resources.storage import TokenStorage
from pushserver.resources.storage.errors import StorageError
from pushserver.resources.utils import (check_host,
                                        log_event, log_remove_request)

router = APIRouter()


@router.delete('/{account}', response_model=RemoveResponse)
async def remove_requests(account: str,
                          request: Request,
                          rm_request: RemoveRequest,
                          background_tasks: BackgroundTasks):

    host, port = request.client.host, request.client.port

    code, description, data = '', '', {}

    if check_host(host, settings.params.allowed_pool):
        request_id = f"{account}-{rm_request.app_id}-{rm_request.device_id}"

        if not settings.params.return_async:
            background_tasks.add_task(log_remove_request, task='log_request',
                                      host=host, loggers=settings.params.loggers,
                                      request_id=request_id, body=rm_request.__dict__)
            background_tasks.add_task(log_remove_request, task='log_success',
                                      host=host, loggers=settings.params.loggers,
                                      request_id=request_id, body=rm_request.__dict__)
            storage = TokenStorage()
            background_tasks.add_task(storage.remove, account, rm_request.app_id, rm_request.device_id)
            return rm_request
        else:
            log_remove_request(task='log_request',
                               host=host, loggers=settings.params.loggers,
                               request_id=request_id, body=rm_request.__dict__)

            storage = TokenStorage()
            try:
                storage_data = storage[account]
            except StorageError:
                error = HTTPException(status_code=500, detail="Internal error: storage")
                log_remove_request(task='log_failure',
                                host=host, loggers=settings.params.loggers,
                                request_id=request_id, body=rm_request.__dict__,
                                error_msg=f'500: {{\"detail\": \"{error.detail}\"}}')
                raise error
            if not storage_data:
                log_remove_request(task='log_failure',
                                   host=host, loggers=settings.params.loggers,
                                   request_id=request_id, body=rm_request.__dict__,
                                   error_msg="User not found in token storage")
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={'result': 'User not found'}
                )

            device_id = f"{rm_request.app_id}-{rm_request.device_id}"
            try:
                device = storage_data[device_id]
            except KeyError:
                log_remove_request(task='log_failure',
                                   host=host, loggers=settings.params.loggers,
                                   request_id=request_id, body=rm_request.__dict__,
                                   error_msg="Device or app_id not found in token storage")
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={'result': 'Not found'}
                )
            else:
                storage.remove(account, rm_request.app_id, rm_request.device_id)
                log_remove_request(task='log_success',
                                   host=host, loggers=settings.params.loggers,
                                   request_id=request_id, body=rm_request.__dict__)
                msg = f'Removing {device}'
                log_event(loggers=settings.params.loggers,
                          msg=msg, level='deb')
                return rm_request

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
