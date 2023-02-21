"""
安装依赖
pip install falcon gunicorn uvicorn websockets

启动服务
gunicorn \
    --bind=0.0.0.0:9000 \
    --worker-class=uvicorn.workers.UvicornWorker \
    --workers=1 \
    --timeout=300 \
    --keep-alive=7200 \
    --forwarded-allow-ips='*' \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info \
    wsdemo:application

发送请求
websocat -vvv 'ws://127.0.0.1:9000/ws/demo?total=100'
"""
import asyncio
import concurrent.futures
import faulthandler
import functools
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Coroutine

import falcon.asgi
import falcon.errors
from falcon.asgi import Request, WebSocket

faulthandler.enable()

LOG = logging.getLogger(__name__)

LOG_FORMAT = "%(levelname)1.1s %(asctime)s %(name)s:%(lineno)d %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    level=logging.INFO,
)

# 单独的线程池，数量可以大一点
WSDEMO_EXECUTOR = ThreadPoolExecutor(
    max_workers=3,
    thread_name_prefix='wsdemo',
)


class DemoStreamResource:
    def _run_coroutine(
        self,
        coro: Coroutine,
        loop: asyncio.AbstractEventLoop,
    ):
        fut: concurrent.futures.Future
        fut = asyncio.run_coroutine_threadsafe(coro, loop=loop)
        fut.result()

    def _stream_main(
        self,
        *,
        ws: WebSocket,
        total: int,
        loop: asyncio.AbstractEventLoop,
    ):
        self._run_coroutine(ws.accept(), loop=loop)
        LOG.info('wsdemo accepted')
        for i in range(total):
            time.sleep(1)
            text = f'wsdemo n={i}'
            LOG.info(text)
            self._run_coroutine(ws.send_text(text), loop=loop)
        self._run_coroutine(ws.close(), loop=loop)
        LOG.info('wsdemo closed')

    async def on_websocket(self, req: Request, ws: WebSocket):
        total = req.get_param_as_int('total', default=30)
        LOG.info('wsdemo total=%d', total)
        loop = asyncio.get_running_loop()
        func_call = functools.partial(
            self._stream_main,
            ws=ws,
            total=total,
            loop=loop,
        )
        try:
            await loop.run_in_executor(WSDEMO_EXECUTOR, func_call)
        finally:
            if not ws.closed:
                await ws.close()


application = falcon.asgi.App()
application.add_route('/ws/demo', DemoStreamResource())

# 模拟启动耗时
time.sleep(10)
LOG.info('wsdemo server started')
