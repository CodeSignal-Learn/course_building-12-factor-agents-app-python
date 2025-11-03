import axios from 'axios'

// Use same-origin requests (empty baseURL) since API and UI are served from the same server
const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const agentAPI = {
  launch: async (inputPrompt) => {
    const response = await api.post('/agent/launch', { input_prompt: inputPrompt })
    return response.data
  },

  getState: async (stateId) => {
    const response = await api.get(`/agent/state/${stateId}`)
    return response.data
  },

  resume: async (stateId) => {
    const response = await api.post('/agent/resume', { id: stateId })
    return response.data
  },

  pause: async (stateId) => {
    const response = await api.post('/agent/pause', { id: stateId })
    return response.data
  },

  provideInput: async (stateId, answer) => {
    const response = await api.post('/agent/provide_input', {
      id: stateId,
      answer: answer,
    })
    return response.data
  },
}

export default api

