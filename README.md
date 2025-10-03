# Nifty Anilist Tools
 
## Overview

This is a simple utility library for interfacing with the [Anilist GraphQL API](https://docs.anilist.co/). It provides things like authentication and schema validation for requests.

### Setup

To use this library, you will need to have the variables shown in [.env.example](./.env.example) in environment variables or your local `.env` file.

## Features

### GraphQL Requests
The Anilist API is GraphQL-based and provides a [public schema](https://studio.apollographql.com/sandbox/schema/reference). This library uses [gql](https://github.com/graphql-python/gql) to make GraphQL requests. You should use the `anilist_request()` function in [request.py](./nifty_anilist/request.py) to make requests to Anilist.

### Anilist Auth
This API will automatically add your Anilist client's auth to the headers of requests (unless you disable it). It will look for an auth token in the local `.env` file under the name `ANILIST_AUTH_TOKEN`. You don't need to add this variable yourself, as it will be added by the library if it is missing. However, this currently opens an instance of Google Chrome to the Anilist login page, from which your auth code will be automatically extracted.
