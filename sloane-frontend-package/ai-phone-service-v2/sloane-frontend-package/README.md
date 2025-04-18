# README.md - Sloane AI Phone Answering Service

Welcome to the Sloane AI Phone Answering Service frontend application! This README provides an overview of the project and instructions for getting started.

## Overview

Sloane is an AI-powered phone answering service for small businesses, inspired by heyrosie.com. The application provides an intuitive interface for businesses to set up and manage their AI phone answering service.

## Key Features

- Modern, responsive UI built with React and Material UI
- Easy onboarding process for non-technical users
- Business profile management
- Call history and analytics
- Business hours configuration
- Calendar integration
- Secure authentication system

## Documentation

This package includes the following documentation:

1. `deployment-instructions.md` - Step-by-step instructions for deploying to Netlify
2. `implementation-documentation.md` - Technical details about the implementation
3. `frontend_architecture.md` - Overview of the frontend architecture
4. `testing-plan.md` - Testing approach and methodology
5. `bug-tracking.md` - Known issues and their status

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/esolamichael/ai-phone-service.git
   cd ai-phone-service
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file in the root directory:
   ```
   REACT_APP_API_URL=https://fluted-mercury-455419-n0.uc.r.appspot.com/api
   ```

4. Start the development server:
   ```
   npm start
   ```

5. Open [http://localhost:3000](http://localhost:3000) to view the application in your browser.

### Building for Production

To build the application for production:

```
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Project Structure

```
sloane-frontend/
├── public/               # Static files
├── src/
│   ├── api/              # API service modules
│   ├── assets/           # Images and other static assets
│   ├── components/       # Reusable UI components
│   ├── contexts/         # React context providers
│   ├── pages/            # Page components
│   ├── styles/           # Global styles and theme
│   ├── utils/            # Utility functions
│   ├── App.jsx           # Main application component
│   └── index.js          # Application entry point
```

## Deployment

See `deployment-instructions.md` for detailed deployment instructions to Netlify.

## Support

For any questions or issues, please contact the development team.

---

Thank you for using Sloane AI Phone Answering Service!
