import React from 'react'

const statusColors = {
  running: '#3b82f6',
  complete: '#10b981',
  failed: '#ef4444',
  waiting_human_input: '#f59e0b',
  max_steps_reached: '#8b5cf6',
}

const statusLabels = {
  running: 'Running',
  complete: 'Complete',
  failed: 'Failed',
  waiting_human_input: 'Waiting for Input',
  max_steps_reached: 'Max Steps Reached',
}

const AgentStatus = ({ status, steps, finalAnswer, error }) => {
  const statusColor = statusColors[status] || '#6b7280'
  const statusLabel = statusLabels[status] || status

  return (
    <div className="agent-status">
      <div className="status-header">
        <div className="status-badge" style={{ backgroundColor: statusColor }}>
          <span className="status-dot"></span>
          {statusLabel}
        </div>
        <div className="steps-counter">Step {steps}</div>
      </div>
      
      {finalAnswer && (
        <div className="final-answer">
          <h3>Final Answer:</h3>
          <p>{finalAnswer}</p>
        </div>
      )}
      
      {error && (
        <div className="error-message">
          <h3>Error:</h3>
          <p>{error}</p>
        </div>
      )}
    </div>
  )
}

export default AgentStatus

