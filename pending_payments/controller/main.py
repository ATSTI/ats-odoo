from odoo import http
from odoo.addons.web.controllers.main import Home
from werkzeug.utils import redirect


class HomeDebug(Home):

    @http.route()
    def web_client(self, s_action=None, **kw):

        session = http.request.session

        # Executa só uma vez
        if not session.get("assets_loaded_once"):

            session["assets_loaded_once"] = True

            url = "/web?debug=assets"

            if s_action:
                url += f"#action={s_action}"

            return redirect(url)

        # Depois volta ao modo normal
        session.debug = ''

        return super().web_client(s_action=s_action, **kw)
