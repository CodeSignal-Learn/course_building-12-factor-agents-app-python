import React from 'react'

const statusColors = {
  running: '#3b82f6',
  complete: '#10b981',
  failed: '#ef4444',
  waiting_human_input: '#f59e0b',
  max_steps_reached: '#8b5cf6',
}

const AgentHistory = ({ agents, onSelectAgent, selectedId }) => {
  const getInitialPrompt = (context) => {
    const userMessage = context.find(item => 
      (typeof item === 'object' && item.role === 'user') ||
      (typeof item === 'string' && item.includes('user'))
    )
    if (userMessage?.content) return userMessage.content
    if (userMessage && typeof userMessage === 'string') return userMessage
    if (context[0]?.content) return context[0].content
    return 'No prompt available'
  }

  return (
    <div className="agent-history">
      <h3>Agent History</h3>
      <div className="history-list">
        {agents.length === 0 ? (
          <div className="empty-state">No agents launched yet</div>
        ) : (
          agents.map((agent) => {
            const prompt = getInitialPrompt(agent.context || [])
            const statusColor = statusColors[agent.status] || '#6b7280'
            const isSelected = agent.id === selectedId

            return (
              <div
                key={agent.id}
                className={`history-item ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelectAgent(agent.id)}
              >
                <div className="history-item-header">
                  <div
                    className="status-indicator"
                    style={{ backgroundColor: statusColor }}
                  ></div>
                  <span className="agent-id">{agent.id.slice(0, 8)}...</span>
                </div>
                <p className="history-prompt">{prompt.slice(0, 60)}...</p>
                <div className="history-meta">
                  <span>Steps: {agent.steps}</span>
                  <span className="status-text">{agent.status}</span>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

export default AgentHistory

