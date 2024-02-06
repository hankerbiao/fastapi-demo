from fastapi import APIRouter, status, Depends

from response.response import Response
from util.upgrade import Upgrade

router = APIRouter()


@router.get('/upgrade', status_code=status.HTTP_200_OK)
async def upgrade(execute=Depends(Upgrade)):
    """
    emss自升级操作
    """
    msg = await execute.run()
    return Response(data=msg)
