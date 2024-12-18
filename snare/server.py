import logging
import aiohttp
import aiohttp_jinja2
import jinja2
import ssl

from aiohttp import web
from aiohttp.web import StaticResource as StaticRoute

from snare.middlewares import SnareMiddleware
from snare.tanner_handler import TannerHandler


class HttpRequestHandler:
    def __init__(self, meta, run_args, snare_uuid, debug=False, keep_alive=75, **kwargs):
        self.run_args = run_args
        self.dir = run_args.full_page_path
        self.meta = meta
        self.snare_uuid = snare_uuid
        self.logger = logging.getLogger(__name__)
        self.sroute = StaticRoute(name=None, prefix="/", directory=self.dir)
        self.tanner_handler = TannerHandler(run_args, meta, snare_uuid)
        self.ssl_cert = run_args.ssl_cert
        self.ssl_key = run_args.ssl_key

    async def submit_slurp(self, data):
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                r = await session.post(
                    "https://{0}:8080/api?auth={1}&chan=snare_test&msg={2}".format(
                        self.run_args.slurp_host, self.run_args.slurp_auth, data
                    ),
                    json=data,
                    timeout=10.0,
                )
                assert r.status == 200
                r.close()
        except Exception as e:
            self.logger.error("Error submitting slurp: %s", e)

    async def handle_request(self, request):
        self.logger.info("Request path: {0}".format(request.path_qs))
        data = self.tanner_handler.create_data(request, 200)
        if request.method == "POST":
            post_data = await request.post()
            self.logger.info("POST data:")
            for key, val in post_data.items():
                self.logger.info("\t- {0}: {1}".format(key, val))
            data["post_data"] = dict(post_data)

        event_result = await self.tanner_handler.submit_data(data)
        if self.run_args.slurp_enabled:
            await self.submit_slurp(request.path_qs)

        content, headers, status_code = await self.tanner_handler.parse_tanner_response(
            request.path_qs, event_result["response"]["message"]["detection"]
        )

        if self.run_args.server_header:
            headers["Server"] = self.run_args.server_header

        if "cookies" in data and "sess_uuid" in data["cookies"]:
            previous_sess_uuid = data["cookies"]["sess_uuid"]
        else:
            previous_sess_uuid = None

        if event_result is not None and "sess_uuid" in event_result["response"]["message"]:
            cur_sess_id = event_result["response"]["message"]["sess_uuid"]
            if previous_sess_uuid is None or not previous_sess_uuid.strip() or previous_sess_uuid != cur_sess_id:
                headers.add("Set-Cookie", "sess_uuid=" + cur_sess_id)

        return web.Response(body=content, status=status_code, headers=headers)

    async def start(self):
        app = web.Application()
        app.add_routes([web.route("*", "/{tail:.*}", self.handle_request)])
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(self.dir))
        middleware = SnareMiddleware(
            error_404=self.meta["/status_404"].get("hash"),
            headers=self.meta["/status_404"].get("headers", []),
            server_header=self.run_args.server_header,
        )
        middleware.setup_middlewares(app)

        self.runner = web.AppRunner(app)
        await self.runner.setup()

        try:
            if self.ssl_cert and self.ssl_key:
                self.logger.info("Creating SSL Context with Cert: %s and Key: %s", self.ssl_cert, self.ssl_key)
                ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)  # adjusted line
                ssl_context.load_cert_chain(certfile=self.ssl_cert, keyfile=self.ssl_key)
                self.logger.info("SSL Context created successfully.")  # added line
            else:
                self.logger.warning("SSL Cert or Key not provided. HTTPS will not be available.")
                ssl_context = None

            self.logger.info("Starting HTTP site on %s:%s", self.run_args.host_ip, self.run_args.port)
            http_site = web.TCPSite(self.runner, self.run_args.host_ip, self.run_args.port)
            await http_site.start()

            if ssl_context:
                self.logger.info("Starting HTTPS site on %s:443", self.run_args.host_ip)
                https_site = web.TCPSite(self.runner, self.run_args.host_ip, 443, ssl_context=ssl_context)
                await https_site.start()

        except ssl.SSLError as e:  # adjusted line
            self.logger.error("SSL Error: %s", str(e))  # adjusted line
        except Exception as e:
            self.logger.exception("Error starting the server: %s", str(e))

        names = sorted(str(s.name) for s in self.runner.sites)
        print("======== Running on {} ========\n" "(Press CTRL+C to quit)".format(", ".join(names)))

    async def stop(self):
        await self.runner.cleanup()
