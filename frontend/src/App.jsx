import React, { useState, useEffect, useRef } from 'react'
import TaskForm from './components/TaskForm'
import AgentStatus from './components/AgentStatus'
import ExecutionView from './components/ExecutionView'
import HumanInputDialog from './components/HumanInputDialog'
import AgentHistory from './components/AgentHistory'
import { agentAPI } from './api/client'
import './App.css'

const TERMINAL_STATUSES = ['complete', 'failed', 'max_steps_reached']
const NON_RESUMABLE_STATUSES = ['complete', 'failed'] // Statuses that cannot be resumed
const POLL_INTERVAL = 2000 // 2 seconds

function App() {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [humanInputQuestion, setHumanInputQuestion] = useState(null)
  const pollingIntervalRef = useRef(null)
  const selectedAgentIdRef = useRef(null)

  // Extract ask_human question from state
  const extractAskHumanQuestion = (state) => {
    if (!state.context) return null
    
    for (let i = state.context.length - 1; i >= 0; i--) {
      const item = state.context[i]
      if (
        item &&
        typeof item === 'object' &&
        item.type === 'function_call' &&
        item.name === 'ask_human'
      ) {
        try {
          const args = typeof item.arguments === 'string'
            ? JSON.parse(item.arguments)
            : item.arguments
          return args.question || 'Please provide input'
        } catch {
          return 'Please provide input'
        }
      }
    }
    return null
  }

  // Start polling for an agent
  const startPolling = (agentId) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
    }

    pollingIntervalRef.current = setInterval(async () => {
      try {
        const state = await agentAPI.getState(agentId)
        updateAgentState(state)

        // Check if waiting for human input
        if (state.status === 'waiting_human_input') {
          const question = extractAskHumanQuestion(state)
          if (question) {
            setHumanInputQuestion({ agentId, question })
            clearInterval(pollingIntervalRef.current)
          }
        }

        // Stop polling if terminal status
        if (TERMINAL_STATUSES.includes(state.status)) {
          clearInterval(pollingIntervalRef.current)
        }
      } catch (error) {
        console.error('Error polling agent state:', error)
      }
    }, POLL_INTERVAL)
  }

  // Update agent in list
  const updateAgentState = (state) => {
    setAgents((prev) => {
      const index = prev.findIndex((a) => a.id === state.id)
      if (index >= 0) {
        const updated = [...prev]
        updated[index] = state
        return updated
      } else {
        return [...prev, state]
      }
    })

    // Update selected agent if it matches (using ref to avoid stale closure)
    if (selectedAgentIdRef.current === state.id) {
      setSelectedAgent(state)
    }
  }

  // Launch new agent
  const handleLaunch = async (prompt) => {
    setIsSubmitting(true)
    try {
      const state = await agentAPI.launch(prompt)
      setAgents((prev) => [state, ...prev])
      setSelectedAgent(state)
      selectedAgentIdRef.current = state.id
      startPolling(state.id)
    } catch (error) {
      console.error('Error launching agent:', error)
      alert('Failed to launch agent: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsSubmitting(false)
    }
  }

  // Select agent from history
  const handleSelectAgent = async (agentId) => {
    try {
      const state = await agentAPI.getState(agentId)
      setSelectedAgent(state)
      selectedAgentIdRef.current = agentId
      
      // Start polling if not terminal
      if (!TERMINAL_STATUSES.includes(state.status)) {
        startPolling(agentId)
      }
    } catch (error) {
      console.error('Error fetching agent state:', error)
    }
  }

  // Resume agent
  const handleResume = async () => {
    if (!selectedAgent) return
    
    try {
      const state = await agentAPI.resume(selectedAgent.id)
      updateAgentState(state)
      selectedAgentIdRef.current = state.id
      startPolling(state.id)
    } catch (error) {
      console.error('Error resuming agent:', error)
      alert('Failed to resume agent: ' + (error.response?.data?.detail || error.message))
    }
  }

  // Pause agent
  const handlePause = async () => {
    if (!selectedAgent) return
    
    try {
      const state = await agentAPI.pause(selectedAgent.id)
      updateAgentState(state)
      // Don't stop polling - keep UI updated
    } catch (error) {
      console.error('Error pausing agent:', error)
      alert('Failed to pause agent: ' + (error.response?.data?.detail || error.message))
    }
  }

  // Provide human input
  const handleProvideInput = async (answer) => {
    if (!humanInputQuestion) return

    try {
      const state = await agentAPI.provideInput(humanInputQuestion.agentId, answer)
      updateAgentState(state)
      selectedAgentIdRef.current = state.id
      setHumanInputQuestion(null)
      startPolling(state.id)
    } catch (error) {
      console.error('Error providing input:', error)
      alert('Failed to provide input: ' + (error.response?.data?.detail || error.message))
    }
  }

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
    }
  }, [])

  return (
    <div className="app">
      <div className="app-container">
        <aside className="sidebar">
          <AgentHistory
            agents={agents}
            onSelectAgent={handleSelectAgent}
            selectedId={selectedAgent?.id}
          />
        </aside>

        <main className="main-content">
          <div className="task-section">
            <h2>Launch New Agent</h2>
            <TaskForm onSubmit={handleLaunch} isSubmitting={isSubmitting} />
          </div>

          {selectedAgent && (
            <div className="agent-details">
              <div className="details-header">
                <h2>Agent Details</h2>
                <div className="action-buttons">
                  {selectedAgent.status === 'running' && (
                    <button onClick={handlePause} className="pause-button">
                      Pause
                    </button>
                  )}
                  {selectedAgent.status !== 'running' &&
                    selectedAgent.status !== 'waiting_human_input' &&
                    !NON_RESUMABLE_STATUSES.includes(selectedAgent.status) && (
                      <button onClick={handleResume} className="resume-button">
                        Resume
                      </button>
                    )}
                </div>
              </div>

              <AgentStatus
                status={selectedAgent.status}
                steps={selectedAgent.steps}
                finalAnswer={selectedAgent.final_answer}
                error={selectedAgent.error}
              />

              <ExecutionView
                context={selectedAgent.context || []}
                pendingToolCalls={selectedAgent.pending_tool_calls || []}
              />
            </div>
          )}

          {!selectedAgent && (
            <div className="empty-state-large">
              <p>Launch an agent to see its execution details here</p>
            </div>
          )}
        </main>
      </div>

      <HumanInputDialog
        isOpen={!!humanInputQuestion}
        question={humanInputQuestion?.question}
        onSubmit={handleProvideInput}
        onClose={() => setHumanInputQuestion(null)}
      />
    </div>
  )
}

export default App

