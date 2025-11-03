import React, { useState } from 'react'

const TaskForm = ({ onSubmit, isSubmitting }) => {
  const [prompt, setPrompt] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (prompt.trim() && !isSubmitting) {
      onSubmit(prompt.trim())
      setPrompt('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <div className="form-group">
        <label htmlFor="task-prompt">Enter your task:</label>
        <textarea
          id="task-prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., Solve the roots of this equation: x^2 - 5x + 6 = 0"
          rows={3}
          disabled={isSubmitting}
          className="task-input"
        />
      </div>
      <button
        type="submit"
        disabled={!prompt.trim() || isSubmitting}
        className="submit-button"
      >
        {isSubmitting ? 'Launching...' : 'Launch Agent'}
      </button>
    </form>
  )
}

export default TaskForm

