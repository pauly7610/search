# Knowledge Base Format

The knowledge base is stored as a single JSON file: `backend/src/xfinity_knowledge_base.json`.

## Structure

```jsonc
{
  "knowledge_base": {
    "name": "Xfinity Customer Support Knowledge Base",
    "agents": {
      "tech_support": {
        "name": "Tech Support Agent",
        "categories": {
          "modem_reset": {
            "question": "How do I reset my Xfinity modem?",
            "responses": [
              {
                "id": "modem_reset_1",
                "type": "basic_power_reset",
                "content": "To reset your Xfinity modem...",
                "keywords": ["reset", "modem", ...]
              },
              // ...
            ]
          },
          // ...
        }
      },
      // billing, general, ...
    }
  }
}
```

## Adding/Editing Agents

- Add a new agent under `agents` with a unique key (e.g., `"new_agent": {...}`)
- Each agent must have a `name`, `description`, and `categories`

## Adding/Editing Categories

- Each category is a FAQ or topic (e.g., `modem_reset`, `slow_internet`)
- Each category has a `question` and a list of `responses`

## Adding/Editing Responses

- Each response has:
  - `id`: unique string
  - `type`: e.g., `troubleshooting`, `step_by_step`, etc.
  - `content`: the answer text
  - `keywords`: list of keywords for matching

## Best Practices

- Use clear, concise questions and answers
- Add multiple responses for nuanced topics
- Use relevant keywords for better matching
- Review and update regularly for accuracy

## Example

See the full file at `backend/src/xfinity_knowledge_base.json` for a complete example.
