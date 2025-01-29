# marzban-verify
marzban-email integration for account management


## Quickstart

1. Create .env file
    ```
    TG_BOT_TOKEN=XXXXXXX
    MAIL_DELIVERY=direct
    DOMAIN=domain to send verification emails from
    ALLOWED_EMAIL_DOMAIN=example.com
    API_BASE_URL=base URL of your marzban panel
    ADMIN_TOKEN=admin token for marzban panel
    ```
2. `poetry self add poetry-plugin-dotenv`
3. `poetry run marzban_verify`