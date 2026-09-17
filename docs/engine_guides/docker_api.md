# Docker

`xbrl-forge` can be also used via Docker!

## Table of Contents

1. [Installation](#installation)
2. [Usage](#Usage)
3. [Conclusion](#conclusion)

---

## Installation

Please make sure you have docker and docker compose installed. Simply build and run the `xbrl-forge` engine:

```bash
docker compose up --build engine
```

This will start the webserver on port `8000`. The port and logging level can be configured in the `engine` section of the `docker-compose.yaml` file.

---

## Usage

Please see the [Web Api How-To](web_api.md) documentation to understand the usage.

---

## Conclusion

The `xbrl-forge` package simplifies the process of working with XBRL files by providing tools to validate the input, preprocess, and generate XBRL documents. By following this guide, you can integrate these functions into your workflow and streamline your reporting processes.

For more details, check the documentation or raise issues for support.
