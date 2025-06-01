import sys
import os
# Ajusta o path para que “services” seja encontrado quando o pytest rodar
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

    # Monkeypatch da função send()
    monkeypatch.setattr(es, 'send', fake_send)

    # Dados de exemplo
    leak = {
        'company': 'TestCo',
        'source_url': 'http://example.onion/leak/123',
        'found_at': '2025-05-07T12:00:00Z'
    }

    await es.send_alert_email('user@example.com', leak)

    msg = sent['msg']
    assert msg['From'] == es.SMTP_USER
    assert msg['To'] == 'user@example.com'
    assert msg['Subject'] == 'Novo vazamento: TestCo'

    # A parte HTML deve conter nosso template
    html_part = msg.get_payload()[1]
    content = html_part.get_content()
    assert 'Vazamento Detectado' in content
    assert 'TestCo' in content
    assert 'http://example.onion/leak/123' in content


def test_send_password_reset_email(monkeypatch):
    sent = {}

    def fake_send(msg: EmailMessage, hostname, port, username, password, start_tls):
        sent['msg'] = msg

    monkeypatch.setattr(es, 'send', fake_send)

    es.send_password_reset_email('user@example.com', 'http://reset-link')

    msg = sent['msg']
    assert msg['From'] == es.SMTP_USER
    assert msg['To'] == 'user@example.com'
    assert msg['Subject'] == 'Redefinição de senha – Deep Protexion'

    # A parte plain-text deve conter o link de reset
    text_part = msg.get_payload()[0]
    assert 'http://reset-link' in text_part.get_content()
