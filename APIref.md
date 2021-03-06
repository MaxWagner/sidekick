Sidekick API Reference
======================

By default, sidekick listens on port 8080. Upon queries it answers with JSON data objects.  
Character sheets are stored sorted according to their rule system (e.g. [GURPS](http://en.wikipedia.org/wiki/GURPS)), and the combination of (system, sheet id) must be globally unique.

Listing of character sheets
---------------------------

To get a listing of all character sheets found, point a GET request to  
`/sheets`  
This will return a JSON object (Content-Type: application/json) along the following schema:

    {
        "sheets":
            [{
                "system": "callofcthulhu",
                "name": "Old Man Henderson",
                "id": "henderson.md"
            },
            {
                "system": "<system>",
                "name": "<character name>",
                "id": "<sheet id>"
            }]
    }

Specific character sheets
-------------------------

Specific character sheets can be requested (GET), written/replaced (PUT) and deleted (DELETE). When using these methods, the URI and the passed data (if any) must be consistent.
The URI schema here is /sheets/`system`/`sheet id`

Example:
GET /sheets/callofcthulhu/henderson.md

    {
        "id": "henderson.md",
        "name": "Old Man Henderson",
        "system": "callofcthulhu",
        "categories":
        [
            { "id": "stats", "name": "Stats", data: { "st": 10, ...} },
            ...
        ]
    }

The content of each category's `data` object is dependent on the system, as different frameworks have different kinds of stats, skills, etc.

The data format is the same across all these methods, but attempting to PUT a character sheet with a `system` or `id` that doesn't fit the queried URI will result in an error 400 (Bad Request).
