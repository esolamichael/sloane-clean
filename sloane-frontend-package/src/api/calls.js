import api from './index';

const callsApi = {
  // Get call history
  getCallHistory: async (params = {}) => {
    try {
      const response = await api.get('/calls/history', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get call details
  getCallDetails: async (callId) => {
    try {
      const response = await api.get(`/calls/${callId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get call analytics
  getCallAnalytics: async (params = {}) => {
    try {
      const response = await api.get('/calls/analytics', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update call notes
  updateCallNotes: async (callId, notes) => {
    try {
      const response = await api.put(`/calls/${callId}/notes`, { notes });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Mark call as handled
  markCallAsHandled: async (callId) => {
    try {
      const response = await api.put(`/calls/${callId}/handled`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Export call history
  exportCallHistory: async (format, params = {}) => {
    try {
      const response = await api.get(`/calls/export/${format}`, { 
        params,
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default callsApi;
