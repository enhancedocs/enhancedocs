<p align="center">
  <img height="100" src="https://raw.githubusercontent.com/enhancedocs/enhancedocs/main/assets/logo.png" alt="EnhanceDocs">
</p>

<p align="center">
    <b>AI-powered search engine for your project documentation</b>
</p>

<p align=center>
    <a href="https://hub.docker.com/r/enhancedocs/enhancedocs"><img src="https://img.shields.io/docker/pulls/enhancedocs/enhancedocs.svg" alt="Docker Hub"></a>
    <a href="https://www.gnu.org/licenses/agpl-3.0.en.html"><img src="https://img.shields.io/badge/license-AGPL--3.0-yellow" alt="License: AGPL-3.0"></a>
    <a href="https://twitter.com/enhancedocs"><img src="https://img.shields.io/twitter/url/https/twitter.com/enhancedocs.svg?style=social&label=Follow%20%40EnhanceDocs" alt="Twitter"></a>
    <a href="https://discord.gg/AUDa3KZavw"><img src="https://dcbadge.vercel.app/api/server/AUDa3KZavw?compact=true&style=flat" alt="Discord"></a>
</p>

## Getting Started

### Install

The easiest way to use EnhanceDocs is to run a pre-built image. To do this, make sure Docker is installed on your system.

```bash
docker run -p 8080:8080 \
  -v $(pwd)/.enhancedocs/data:/data/enhancedocs \
  -v $(pwd)/.enhancedocs/config:/etc/enhancedocs \
  --env OPENAI_API_KEY=sk-... \
  enhancedocs/enhancedocs
```

In this case EnhanceDocs will use default configuration and store all data under ./.enhancedocs directory.

You can optionally provide the following env variables:

- `ENHANCEDOCS_API_KEY` is optional; By default you can ingest data into EnhanceDocs without an API Key, 
so you can work comfortable in your local environment, but we highlight recommend to set this on production.
- `ENHANCEDOCS_ACCESS_TOKEN` is optional; This is a client side token, and we recommend its usage on production 
together with cors so only your site can make requests to the API.

## Managed EnhanceDocs

EnhanceDocs is free and open source, and it requires that you self-host it. 
Alternatively you can use EnhanceDocs managed version, with built-in integrations with your preferred tools out of box, such as
Notion, Slack, Teams, Confluence, Discord and much more...

https://enhancedocs.com

## Learn more

The best place to get started is following our getting started guide on the [EnhanceDocs Documentation](https://docs.enhancedocs.com/).

## LICENSE

EnhanceDocs is free and the source is available.
EnhanceDocs is published under the [GNU Affero General Public License v3.0](LICENSE)
