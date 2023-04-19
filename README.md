# EnhanceDocs

Welcome to EnhanceDocs! EnhanceDocs is the open-source AI-powered search engine for your project or business documentation.

[![License: SSPL v1](https://img.shields.io/badge/license-SSPL--v1-yellow)](https://www.mongodb.com/licensing/server-side-public-license)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/enhancedocs.svg?style=social&label=Follow%20%40EnhanceDocs)](https://twitter.com/enhancedocs)
[![](https://dcbadge.vercel.app/api/server/AUDa3KZavw?compact=true&style=flat)](https://discord.gg/AUDa3KZavw)

## Getting Started

#### Download EnhanceDocs

- Cloning this repository `git clone git@github.com:enhancedocs/enhancedocs.git`

or

- Using docker image `docker pull enhancedocs/enhancedocs`

#### Set up env variables

Use the `.example.env` as a template and fill with the required fields.

- `OPENAI_API_KEY` is required; EnhanceDocs relies on [OpenAI API](https://platform.openai.com/docs/introduction)
- `ENHANCEDOCS_API_KEY` is optional; By default you can ingest data into EnhanceDocs without an API Key, 
so you can work conformable in your local environment, 
but we highlight recommend to set this on production if you are exposing the API to the internet.
- `ENHANCEDOCS_ACCESS_TOKEN` is optional; This is a client side token, 
and we recommend its usage together with cors so only your site can make requests to the API.

```bash
cp .example.env .env
```

#### Update config.json

Update `config.json` so matches your project description


### 🚀 Launch EnhanceDocs

```bash
docker compose up
```

## Managed EnhanceDocs

EnhanceDocs is free and open source, and it requires that you self-host it. 
Alternatively you can use EnhanceDocs managed version, with built-in integrations with your preferred tools out of box, such as
Notion, Slack, Teams, Confluence, Discord and much more...

https://enhancedocs.com

## LICENSE

EnhanceDocs is free and the source is available.
EnhanceDocs is published under the [Server Side Public License (SSPL) v1](LICENSE)
