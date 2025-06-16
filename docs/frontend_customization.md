# Frontend Customization

## Customizing the Chat UI

- Edit components in `src/components/chat/` (e.g., `ChatInterface`, `MessageBubble`)
- Display additional metadata (agent, answer type, intent) as needed
- Add icons, colors, or tooltips for agent/source info

## Customizing Analytics

- Edit dashboard components in `src/components/analytics/`
- Use or extend hooks in `src/hooks/useAnalytics.ts`
- Add new charts or metrics as needed

## Displaying Agent/Intent Info

- The `MessageBubble` component displays agent name, answer type, and intent for assistant messages
- To add more info, update the `Message` type and UI rendering logic

## Theming & Branding

- Edit Tailwind config in `tailwind.config.js`
- Update CSS in `src/styles/` and component modules
- Change layout in `src/components/layout/`

## Adding New Features

- Create new components in `src/components/`
- Add new hooks in `src/hooks/`
- Update API calls in `src/services/`

## Example: Add a New Agent Display

1. Add new agent logic to backend and knowledge base
2. Update `MessageBubble` to recognize and style the new agent
3. Optionally, add icons or colors for the new agent type

---

For more, see the main frontend README and code comments.
