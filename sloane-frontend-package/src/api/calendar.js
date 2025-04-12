import api from './index';

const calendarApi = {
  // Get calendar integrations
  getCalendarIntegrations: async () => {
    try {
      const response = await api.get('/calendar/integrations');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Connect calendar (start OAuth flow)
  connectCalendar: async (provider) => {
    try {
      const response = await api.post('/calendar/connect', { provider });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Complete OAuth flow with code
  completeCalendarConnection: async (provider, code) => {
    try {
      const response = await api.post('/calendar/connect/callback', { provider, code });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Disconnect calendar
  disconnectCalendar: async (integrationId) => {
    try {
      const response = await api.delete(`/calendar/integrations/${integrationId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get appointments
  getAppointments: async (params = {}) => {
    try {
      const response = await api.get('/calendar/appointments', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get appointment details
  getAppointmentDetails: async (appointmentId) => {
    try {
      const response = await api.get(`/calendar/appointments/${appointmentId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Create appointment
  createAppointment: async (appointmentData) => {
    try {
      const response = await api.post('/calendar/appointments', appointmentData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update appointment
  updateAppointment: async (appointmentId, appointmentData) => {
    try {
      const response = await api.put(`/calendar/appointments/${appointmentId}`, appointmentData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete appointment
  deleteAppointment: async (appointmentId) => {
    try {
      const response = await api.delete(`/calendar/appointments/${appointmentId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get availability
  getAvailability: async (date) => {
    try {
      const response = await api.get('/calendar/availability', { params: { date } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default calendarApi;
