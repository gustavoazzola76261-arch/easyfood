"""Serviço compartilhado de e-mail (Atividade 6).

A API depende apenas de send_email(). Sem EMAIL_API_KEY o envio vai para o console,
o que cobre testes e desenvolvimento local. Com a chave, usa a API HTTP do Resend.
"""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from html import escape


def build_html(*, header: str, body: str, footer: str) -> str:
    return f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
      <h2>{header}</h2>
      <div>{body}</div>
      <hr />
      <p style="color: #888; font-size: 12px;">{footer}</p>
    </div>
    """


def send_email(*, to: str, to_name: str, subject: str, header: str, body: str, footer: str) -> None:
    html = build_html(header=header, body=body, footer=footer)
    text = f"{header}\n\n{body}\n\n{footer}"
    api_key = os.getenv("EMAIL_API_KEY", "").strip()

    if not api_key:
        print(f'[EMAIL] Enviado para {to} - "{subject}"')
        print(text)
        return

    payload = {
        "from": f"{os.getenv('EMAIL_FROM_NAME', 'EasyFood')} <{os.getenv('EMAIL_FROM', 'no-reply@easyfood.local')}>",
        "to": [f"{to_name or to} <{to}>"] if to_name else [to],
        "subject": subject,
        "html": html,
        "text": text,
    }
    request = urllib.request.Request(
        os.getenv("EMAIL_API_URL", "https://api.resend.com/emails"),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=10, context=context) as response:
            response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Falha ao enviar e-mail: {exc}") from exc

    print(f'[EMAIL] Enviado para {to} - "{subject}"')


def notify_safely(**kwargs) -> None:
    """Ação secundária: nunca derruba a operação principal."""
    try:
        send_email(**kwargs)
    except Exception as exc:
        print("Erro ao enviar e-mail:", getattr(exc, "message", str(exc)))


def escape_text(value: str) -> str:
    return escape(value or "")
