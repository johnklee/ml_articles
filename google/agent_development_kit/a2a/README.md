# How to use `a2a_root`:
## Start the Remote A2A Agent server
start the remote agent server, which will host the `a2a_app` within the `hello_world` agent:

```shell
# Under path ml_articles/google/agent_development_kit/a2a
$ uvicorn a2a_root.remote_a2a.hello_world.agent:a2a_app --host localhost --port 8001
...
NFO:     Started server process [2630123]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8001 (Press CTRL+C to quit)
```

## Check that your remote agent is running
You can check that your agent is up and running by visiting the agent card that was auto-generated earlier as part of your `to_a2a()` function in <font color='olive'>a2a_root/remote_a2a/hello_world/agent.py</font>:
```shell
$ wget -qO- http://localhost:8001/.well-known/agent-card.json | python3 -m json.tool
{
    "capabilities": {},
    "defaultInputModes": [
        "text/plain"
    ],
    "defaultOutputModes": [
        "text/plain"
    ],
    "description": "hello world agent that can roll a dice of 8 sides and check prime numbers.",
    "name": "hello_world_agent",
    "preferredTransport": "JSONRPC",
    "protocolVersion": "0.3.0",
    "skills": [
        {
            "description": "hello world agent that can roll a dice of 8 sides and check prime numbers....",
            "id": "hello_world_agent",
            "name": "model",
            "tags": [
                "llm"
            ]
        },
        {
            "description": "Roll a die and return the rolled result...",
            "id": "hello_world_agent-roll_die",
            "name": "roll_die",
            "tags": [
                "llm",
                "tools"
            ]
        },
        {
            ...
        }
    ],
    "supportsAuthenticatedExtendedCard": false,
    "url": "http://localhost:8001",
    "version": "0.0.1"
}
```

##
```shell
$ adk web .
```


