# response.py
from typing import Any, Optional, Dict

from starlette.background import BackgroundTask
from starlette.responses import JSONResponse


class Response(JSONResponse):
    def __init__(self,
                 code: int = 0,
                 msg: str = '操作成功',
                 data: Any = None,
                 status_code: int = 200,
                 headers: Optional[Dict[str, str]] = None,
                 background: Optional[BackgroundTask] = None,
                 count: int = 1
                 ) -> None:
        content = {
            'code': code,
            'msg': msg,
            'data': data,
            'count': count,
        }
        status_code = int(status_code)
        super().__init__(content=content, status_code=status_code, headers=headers, media_type='application/json',
                         background=background)
