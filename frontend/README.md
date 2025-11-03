# 12-Factor Agents UI

A modern, beautiful web interface for managing and monitoring AI agents built with React and Vite.

## Features

- **Launch New Agents**: Submit natural language tasks to launch new agent workflows
- **Real-Time Monitoring**: Watch agent execution in real-time with automatic polling
- **Execution History**: View all past agent executions in a sidebar
- **Step-by-Step View**: See detailed execution context, tool calls, and outputs
- **Human-in-the-Loop**: Interactive dialog for providing input when agents need clarification
- **Status Tracking**: Visual status indicators for running, complete, failed, and waiting states
- **Resume Workflows**: Resume interrupted or paused agent workflows

## Installation

1. Install dependencies:

```bash
cd frontend
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The UI will be available at `http://localhost:3000`.

Make sure your backend server is running on `http://localhost:8000` (see main README for server setup).

## Building for Production

Build the production bundle:

```bash
npm run build
```

The built files will be in the `dist/` directory.

Preview the production build:

```bash
npm run preview
```

## Architecture

- **React**: UI framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client for API communication
- **CSS**: Custom styling with modern design patterns

### Components

- `App.jsx`: Main application component with state management and polling logic
- `TaskForm.jsx`: Form for launching new agents
- `AgentStatus.jsx`: Status badge and final answer display
- `ExecutionView.jsx`: Detailed view of agent execution context
- `HumanInputDialog.jsx`: Modal dialog for human input requests
- `AgentHistory.jsx`: Sidebar showing all agent executions

### API Integration

The UI communicates with the FastAPI backend through the `api/client.js` module, which provides:
- `launch()`: Launch a new agent
- `getState()`: Get current agent state
- `resume()`: Resume a paused agent
- `provideInput()`: Provide human input to a waiting agent

## Usage

1. **Launch an Agent**: Enter a task description (e.g., "Solve the roots of this equation: x^2 - 5x + 6 = 0") and click "Launch Agent"

2. **Monitor Execution**: The agent's status updates automatically. Watch the execution context grow as the agent processes your request.

3. **Provide Input**: If the agent needs clarification, a dialog will appear. Enter your response and submit.

4. **View History**: Click on any agent in the sidebar to view its details and execution history.

5. **Resume Workflows**: If an agent is paused, use the "Resume" button to continue execution.

