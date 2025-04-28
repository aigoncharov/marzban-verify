# marzban-verify

Email verification to automatically create accounts in Marzban. Allow your org to setup a VPN account with a couple of Telegram messages and a single email.

Features:

- Whitelist a specific email domain
- Send verification email vis SMTP and Exchange
- Simple setup via Docker


## Quickstart

1. Start Marzban
2. Get an admin API token
3. Create `compose.yml`
    ```yaml
    services:
        marzban-verify:
            image: aigoncharov/marzban-verify:latest
            container_name: marzban-verify
            restart: always
            env_file:
                - .env
    ```
4. Create `.env` file
   1. Exchange (using a personal email address to send emails to your colleagues)
        ```
        TG_BOT_TOKEN=XXXXXXX
        MARZBAN_ADMIN_API_TOKEN=XXXXXXX
        MARZBAN_API_BASE_URL=https://marzban_api_domain.com
        ALLOWED_EMAIL_POSTFIX=@example.com

        MAIL_DELIVERY=EXCHANGE
        EWS_MAIL_LOGIN=
        EWS_MAIL_PASSWORD=
        EWS_MAIL_SERVER=
        EWS_MAIL_ADDRESS=
        ```
    2. SMTP (setup a self-hosted email server to deliver emails, not always available as some hosters block 25 port, also prone to be identified as spam)
        ```
        TG_BOT_TOKEN=XXXXXXX
        MARZBAN_ADMIN_API_TOKEN=XXXXXXX
        MARZBAN_API_BASE_URL=https://marzban_api_domain.com
        ALLOWED_EMAIL_POSTFIX=@example.com

        MAIL_DELIVERY=DIRECT
        DIRECT_MAILER_SMTP_PORT=25
        <!-- https://serverfault.com/questions/305925/what-exactly-should-helo-say -->
        DIRECT_MAILER_SENDER_DOMAIN=
        DIRECT_MAILER_HELLO_NAME=
        ```
5. Start with `docker compose up -d`

## Config

Available as environment variables:

1. `USER_CONFIG`. Set inbounds, expiration date, traffic limit and [more](https://gozargah.github.io/marzban/en/docs/api). Pass a string with a stringified JSON (loadable with `json.loads(...)`). See default [here](https://github.com/aigoncharov/marzban-verify/blob/a4aca1d31c9667e1cd2cec84e9f63c96b3685dd3/marzban_verify/utils/config.py#L16).
