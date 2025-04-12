# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Run/Test Commands

### Frontend (React)
- `cd sloane-frontend-package && npm start` - Start the frontend dev server
- `cd sloane-frontend-package && npm test` - Run all frontend tests
- `cd sloane-frontend-package && npm test -- -t "testName"` - Run specific frontend test
- `cd sloane-frontend-package && npm run build` - Build frontend for production

### Backend (Python/FastAPI)
- `cd ai-phone-service-v2 && python -m main` - Run the main server
- `cd ai-phone-service-v2 && python -m tests.test_ai_phone_service` - Run unit tests
- `cd ai-phone-service-v2 && python -m tests.test_ai_phone_service TestAIPhoneService.test_greeting` - Run specific test
- `cd ai-phone-service-v2 && python -m tests.integration_test` - Run integration tests

## Code Style Guidelines

### JavaScript/React
- Use ES6+ features and functional components
- Follow React hooks pattern for state management
- Use Material UI components for consistent design
- Use named exports for components, `export function MyComponent()`
- Handle errors with try/catch blocks and provide user feedback

### Python
- Follow PEP 8 style guidelines
- Use type hints (Python 3.9+ typing)
- Organize imports: standard library, third-party, local
- Document functions with docstrings
- Use exception handling with specific exceptions
- Follow FastAPI API design practices
- Use dependency injection for services

### General
- Use descriptive variable/function names (camelCase for JS, snake_case for Python)
- Write unit tests for all new functionality
- Add comments for complex logic
- Keep functions small and focused
- Use proper error handling with user-friendly messages