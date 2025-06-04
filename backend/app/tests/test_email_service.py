import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from email.message import EmailMessage
import services.email_service as es


@pytest.mark.asyncio
async def test_send_alert_email(monkeypatch):
    sent = {}

    async def fake_send(msg: EmailMessage, hostname, port, username, password, start_tls):
        sent['msg'] = msg
        sent['hostname'] = hostname
        sent['port'] = port
        sent['username'] = username
        sent['password'] = password
        sent['start_tls'] = start_tls

    async def fake_render(template_name: str, context: dict) -> str:
        return '<html>alert</html>'

    monkeypatch.setattr(es, 'send', fake_send)
    monkeypatch.setattr(es, 'render_template_to_string', fake_render)

    leak = {
        'company': 'TestCo',
        'country': 'US',
        'date': '2025-05-07',
        'description': 'desc',
        'link': 'http://example.onion/leak/123',
    }

    await es.send_alert_email('user@example.com', leak)

    msg = sent['msg']
    assert msg['From'] == es.SMTP_USER
    assert msg['To'] == 'user@example.com'
    assert msg['Subject'] == 'Novo vazamento: TestCo'
    html_part = msg.get_payload()[1]
    assert 'alert' in html_part.get_content()


@pytest.mark.asyncio
async def test_send_password_reset_email(monkeypatch):
    sent = {}

    async def fake_send(msg: EmailMessage, hostname, port, username, password, start_tls):
        sent['msg'] = msg

    monkeypatch.setattr(es, 'send', fake_send)
    async def fake_render(*args, **kwargs):
        return '<html></html>'

    monkeypatch.setattr(es, 'render_template_to_string', fake_render)

    await es.send_password_reset_email('user@example.com', 'http://reset-link', 'User')

    msg = sent['msg']
    assert msg['From'] == es.SMTP_USER
    assert msg['To'] == 'user@example.com'
    assert msg['Subject'] == 'Redefinição de senha – Deep Protexion'
    text_part = msg.get_payload()[0]
    assert 'http://reset-link' in text_part.get_content()
