# IT Helpdesk Workflow Notes

## Suggested graph responsibilities

Map each node to one clear responsibility, such as request validation, intent routing, knowledge retrieval, answer generation, tool execution, and escalation. Document the actual graph in source before treating this list as implemented.

## State and transitions

For each graph state field, record its type, producer, consumer, and whether it can contain sensitive information. Document each conditional edge and the criteria used to select the next node.

## Tool boundaries

- Use read-only tools by default.
- Require confirmation before destructive actions, access changes, or account modifications.
- Validate tool inputs and handle timeouts and permission errors.
- Never pass passwords, tokens, or unnecessary personal data to an external model.
- Keep a human escalation path for unresolved incidents.

## Testing

Cover common support requests, ambiguous questions, missing knowledge articles, tool failures, repeated routing, and prompt injection. Assert that sensitive actions are not executed without authorization.
