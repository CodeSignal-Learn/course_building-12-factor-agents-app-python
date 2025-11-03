import React from 'react'

const ExecutionView = ({ context, pendingToolCalls }) => {
  const renderContextItem = (item, index) => {
    if (typeof item === 'string') {
      return (
        <div key={index} className="context-item context-text">
          {item}
        </div>
      )
    }

    if (item.type === 'function_call') {
      const args = typeof item.arguments === 'string' 
        ? JSON.parse(item.arguments) 
        : item.arguments
      
      // Format arguments as compact inline text
      const argsText = Object.entries(args)
        .map(([key, value]) => `${key}: ${typeof value === 'object' ? JSON.stringify(value) : value}`)
        .join(', ')
      
      return (
        <div key={index} className="context-item context-function-call">
          <div className="function-call-header">
            <span className="function-name">{item.name}</span>
            <span className="call-id">#{item.call_id?.slice(0, 8)}</span>
          </div>
          <div className="function-args">{argsText}</div>
        </div>
      )
    }

    if (item.type === 'function_call_output') {
      let output
      try {
        output = typeof item.output === 'string' 
          ? JSON.parse(item.output) 
          : item.output
      } catch {
        output = item.output
      }

      // Format output as compact text
      let outputText
      if (typeof output === 'object' && output !== null) {
        if (output.result !== undefined) {
          outputText = String(output.result)
        } else if (output.answer !== undefined) {
          outputText = String(output.answer)
        } else {
          outputText = JSON.stringify(output)
        }
      } else {
        outputText = String(output)
      }

      return (
        <div key={index} className="context-item context-function-output">
          <div className="function-output-header">
            <span>Output</span>
            <span className="call-id">#{item.call_id?.slice(0, 8)}</span>
          </div>
          <div className="function-output">{outputText}</div>
        </div>
      )
    }

    if (item.role === 'user' || item.role === 'assistant') {
      return (
        <div key={index} className={`context-item context-${item.role}`}>
          <strong>{item.role === 'user' ? 'User' : 'Assistant'}:</strong> {item.content}
        </div>
      )
    }

    return (
      <div key={index} className="context-item">
        <div>{JSON.stringify(item)}</div>
      </div>
    )
  }

  return (
    <div className="execution-view">
      <h3>Execution Context</h3>
      <div className="context-list">
        {context.map((item, index) => renderContextItem(item, index))}
      </div>
      
      {pendingToolCalls && pendingToolCalls.length > 0 && (
        <div className="pending-calls">
          <h4>Pending Tool Calls:</h4>
          {pendingToolCalls.map((call, index) => {
            const args = typeof call.arguments === 'string' 
              ? JSON.parse(call.arguments) 
              : call.arguments
            const argsText = Object.entries(args)
              .map(([key, value]) => `${key}: ${typeof value === 'object' ? JSON.stringify(value) : value}`)
              .join(', ')
            return (
              <div key={index} className="pending-call">
                <span className="function-name">{call.name}</span>
                <div className="pending-args">{argsText}</div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default ExecutionView

