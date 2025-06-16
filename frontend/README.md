# Frontend

## Overview

This is the frontend for the AI-powered chat application. It uses React, TypeScript, and native WebSockets for real-time communication with the backend.

## Features

- Real-time chat using native WebSockets
- Intent classification and routing
- Analytics dashboard
- Feedback system

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```

## WebSocket Communication

The frontend uses native WebSockets to communicate with the backend. The WebSocket endpoint is available at `ws://localhost:8000/ws`.

## Project Structure

- `src/components`: UI components
- `src/hooks`: Custom hooks for WebSocket and chat logic
- `src/services`: API and WebSocket logic
- `src/types`: TypeScript type definitions
- `src/utils`: Utility functions

## Documentation

For more details, see the [documentation](./docs/README.md).
