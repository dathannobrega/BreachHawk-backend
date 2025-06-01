# Imagem base enxuta, mas com repositório Debian‑stable (Tor 0.4.8.x)
FROM debian:stable-slim

# Instala Tor e dependências básicas
RUN apt-get update && \
    apt-get install -y --no-install-recommends tor tor-geoipdb ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copia torrc customizado (ver abaixo)
COPY torrc /etc/tor/torrc

# Expõe porta SOCKS5
EXPOSE 9050

# Tor escreve logs no stdout
CMD ["tor", "-f", "/etc/tor/torrc"]
