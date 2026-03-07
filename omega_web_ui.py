from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from omega_constitutional_model import ConstitutionalState, G_constitutional_op


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Omega 憲法模型測試介面</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; max-width: 920px; line-height: 1.45; }}
    h1 {{ margin-bottom: .2rem; }}
    p.note {{ color: #555; margin-top: 0; }}
    .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 1rem; background: #fafafa; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(230px, 1fr)); gap: .9rem 1.2rem; }}
    label {{ font-weight: 600; display: block; margin-bottom: .2rem; }}
    input, select {{ width: 100%; padding: .45rem; border-radius: 8px; border: 1px solid #bbb; }}
    button {{ margin-top: .9rem; padding: .6rem 1rem; border: 0; border-radius: 8px; background: #2d6cdf; color: #fff; cursor: pointer; }}
    .result {{ background: #f0f8ff; border: 1px solid #b8d8ff; border-radius: 10px; padding: 1rem; margin-top: .9rem; }}
    .error {{ background: #fff2f2; border: 1px solid #f2b8b8; color: #7e1111; border-radius: 10px; padding: .8rem; margin-top: .8rem; }}
    code {{ background: #eee; padding: .1rem .25rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Omega 憲法模型測試介面</h1>
  <p class="note">輸入狀態參數與操作，快速檢視 U 指數、安全硬約束與角色權重效果。</p>

  <form method="post" class="card">
    <h3>1) 基本狀態輸入</h3>
    <div class="grid">
      <div>
        <label for="L_star">L_star（清晰度/誠實度，0~1）</label>
        <input id="L_star" name="L_star" value="{L_star}" type="number" min="0" max="1" step="0.01" required />
      </div>
      <div>
        <label for="a_star">a_star（衝突/風險，-1~1）</label>
        <input id="a_star" name="a_star" value="{a_star}" type="number" min="-1" max="1" step="0.01" required />
      </div>
      <div>
        <label for="b_star">b_star（希望/幫助性，-1~1）</label>
        <input id="b_star" name="b_star" value="{b_star}" type="number" min="-1" max="1" step="0.01" required />
      </div>
    </div>

    <h3>2) 套用操作（可選）</h3>
    <div class="grid">
      <div>
        <label for="op_type">op_type</label>
        <select id="op_type" name="op_type">
          {op_options}
        </select>
      </div>
      <div>
        <label for="lam">lambda（0~1）</label>
        <input id="lam" name="lam" value="{lam}" type="number" min="0" max="1" step="0.01" required />
      </div>
      <div>
        <label for="principal">principal</label>
        <select id="principal" name="principal">
          {principal_options}
        </select>
      </div>
    </div>

    <button type="submit">執行測試</button>
  </form>

  {message_block}
</body>
</html>
"""

OPS = ["NONE", "REFRAME_JUSTICE", "RECEIVE_GRACE", "HONESTY_CHECK"]
PRINCIPALS = ["User", "Operator", "Anthropic"]


def _to_float(values: dict[str, list[str]], key: str) -> float:
    return float(values.get(key, ["0"])[0])


def _sel_options(options: list[str], current: str) -> str:
    parts = []
    for option in options:
        selected = " selected" if option == current else ""
        parts.append(f'<option value="{html.escape(option)}"{selected}>{html.escape(option)}</option>')
    return "\n".join(parts)


def _render_result(state: ConstitutionalState, op_type: str, lam: float, principal: str) -> str:
    initial_u = state.compute_u_index()
    ep1, esyn, ecosyn = state.compute_spectral_energies()
    hard = state.check_hard_constraints()

    body = [
        '<div class="result">',
        "<h3>結果</h3>",
        f"<p><b>初始 U 指數：</b><code>{initial_u:.4f}</code></p>",
        f"<p><b>硬約束觸發：</b><code>{hard}</code></p>",
        f"<p><b>頻譜能量：</b> E_p1=<code>{ep1:.4f}</code>, E_syn=<code>{esyn:.4f}</code>, E_cosyn=<code>{ecosyn:.4f}</code></p>",
    ]

    if op_type != "NONE":
        new_state = G_constitutional_op(state, op_type, lam, principal)
        new_u = new_state.compute_u_index()
        body.append("<hr />")
        body.append(
            f"<p><b>操作後狀態：</b>L*={new_state.L_star:.4f}, a*={new_state.a_star:.4f}, b*={new_state.b_star:.4f}</p>"
        )
        body.append(f"<p><b>操作後 U 指數：</b><code>{new_u:.4f}</code></p>")

    body.append("</div>")
    return "\n".join(body)


class OmegaUIHandler(BaseHTTPRequestHandler):
    def _render_page(self, form: dict[str, list[str]] | None = None, message_block: str = "") -> bytes:
        form = form or {}
        current = {
            "L_star": form.get("L_star", ["0.8"])[0],
            "a_star": form.get("a_star", ["0.6"])[0],
            "b_star": form.get("b_star", ["0.5"])[0],
            "op_type": form.get("op_type", ["NONE"])[0],
            "lam": form.get("lam", ["0.5"])[0],
            "principal": form.get("principal", ["User"])[0],
        }

        page = HTML_TEMPLATE.format(
            L_star=html.escape(current["L_star"]),
            a_star=html.escape(current["a_star"]),
            b_star=html.escape(current["b_star"]),
            lam=html.escape(current["lam"]),
            op_options=_sel_options(OPS, current["op_type"]),
            principal_options=_sel_options(PRINCIPALS, current["principal"]),
            message_block=message_block,
        )
        return page.encode("utf-8")

    def _send_html(self, payload: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        self._send_html(self._render_page())

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw_data = self.rfile.read(length).decode("utf-8")
        form = parse_qs(raw_data)

        try:
            state = ConstitutionalState(
                L_star=_to_float(form, "L_star"),
                a_star=_to_float(form, "a_star"),
                b_star=_to_float(form, "b_star"),
            )
            op_type = form.get("op_type", ["NONE"])[0]
            lam = _to_float(form, "lam")
            principal = form.get("principal", ["User"])[0]

            if op_type not in OPS:
                raise ValueError("無效的 op_type")
            if principal not in PRINCIPALS:
                raise ValueError("無效的 principal")

            message_block = _render_result(state, op_type, lam, principal)
        except ValueError as exc:
            message_block = f'<div class="error">輸入錯誤：{html.escape(str(exc))}</div>'

        self._send_html(self._render_page(form=form, message_block=message_block))


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = HTTPServer((host, port), OmegaUIHandler)
    print(f"Omega UI 啟動：http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
