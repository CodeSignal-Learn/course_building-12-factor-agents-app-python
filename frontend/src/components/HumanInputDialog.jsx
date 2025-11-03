import React, { useState, useEffect } from 'react'

const HumanInputDialog = ({ isOpen, question, onSubmit, onClose }) => {
  const [answer, setAnswer] = useState('')

  useEffect(() => {
    if (isOpen) {
      setAnswer('')
    }
  }, [isOpen])

  if (!isOpen) return null

  const handleSubmit = (e) => {
    e.preventDefault()
    if (answer.trim()) {
      onSubmit(answer.trim())
    }
  }

  return (
    <div className="dialog-overlay" onClick={onClose}>
      <div className="dialog-content" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-header">
          <h2>Human Input Required</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="dialog-body">
          <p className="question-text">{question}</p>
          <form onSubmit={handleSubmit}>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Enter your answer..."
              rows={4}
              className="answer-input"
              autoFocus
            />
            <div className="dialog-actions">
              <button type="submit" className="submit-button" disabled={!answer.trim()}>
                Submit
              </button>
              <button type="button" className="cancel-button" onClick={onClose}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default HumanInputDialog

