# Nifty Anilist Tools
 
## Overview

This is a simple utility library for interfacing with the [Anilist GraphQL API](https://docs.anilist.co/). It provides things like authentication and schema validation for requests.

### Setup

To use this library, you will need to have the variables shown in [.env.example](./.env.example) in environment variables or your local `.env` file.

## Features

### GraphQL Requests
The Anilist API is GraphQL-based and provides a [public schema](https://studio.apollographql.com/sandbox/schema/reference). This library uses [gql](https://github.com/graphql-python/gql) to make GraphQL requests. You should use the `anilist_request()` function in [request.py](./nifty_anilist/request.py) to make requests to Anilist.

### Anilist Auth

#### Token Storage
This library will store Anilist auth token(s) locally in one of two ways (customizable with the `TOKEN_SAVING_METHOD` environment variable):
1. Using your system's keyring (kept "permanently"): `KEYRING`
2. In-memory (lost when you restart your program): `IN_MEMORY`

#### Using Auth
In order to get an auth token for the first time, you can use the `sign_in_if_no_global()` function from [auth.py](./nifty_anilist/auth.py). After the first time, these details will be stored locally and added to your Anilist requests automatically.

**Note:** The sign-in function currently opens an instance of Google Chrome to the Anilist login page, from which your auth code will be automatically extracted. There will be more ways to do sign-in later.

There are two ways that auth headers can be added to your requests:
1. Using a global user ID stored in the `.env` file: The ID is stored as `ANILIST_CURRENT_USER`. This is the user ID that will be used to retrieve the token from the storage method(s) above. When making requests with `anilist_request()`, you can ignore the optional `user_id` parameter to use this approach. Example:
```py
async def do_something():
    request = gql("some query")
    return await anilist_request(request)

if __name__ == "__main__":
    sign_in_if_no_global()
    data = asyncio.run(do_something())
    print(data)
```
2. Manually passing in a user ID to the `anilist_request()` with the `user_id` parameter will try to get that user's token from local storage and use it instead of the global one. Example:
```py
async def do_something(user_id: str):
    request = gql("some query")
    return await anilist_request(request, user_id=user_id)

if __name__ == "__main__":
    my_user_id = "12345"
    data = asyncio.run(do_something(user_id=my_user_id))
    print(data)
```

You can also choose to not use auth on requests with the `use_auth` parameter (default is `True`):
```py
async def do_something():
    request = gql("some query")
    return await anilist_request(request, use_auth=False)
```
