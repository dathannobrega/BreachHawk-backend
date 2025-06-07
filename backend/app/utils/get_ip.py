from fastapi import Request


def get_client_ip(request: Request) -> str:
    # Pega o header X-Forwarded-For
    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        # X-Forwarded-For pode conter uma lista de IPs, pega o primeiro
        ip = forwarded_for.split(",")[0].strip()
    else:
        # Se não tem o header, pega o IP da conexão TCP
        ip = request.client.host

    return ip
