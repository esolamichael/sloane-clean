import api from './index';

const businessApi = {
  // Get business profile
  getBusinessProfile: async () => {
    try {
      const response = await api.get('/business/profile');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update business profile
  updateBusinessProfile: async (profileData) => {
    try {
      const response = await api.put('/business/profile', profileData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get business hours
  getBusinessHours: async () => {
    try {
      const response = await api.get('/business/hours');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update business hours
  updateBusinessHours: async (hoursData) => {
    try {
      const response = await api.put('/business/hours', hoursData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get business services
  getBusinessServices: async () => {
    try {
      const response = await api.get('/business/services');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update business services
  updateBusinessServices: async (servicesData) => {
    try {
      const response = await api.put('/business/services', servicesData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get business FAQs
  getBusinessFAQs: async () => {
    try {
      const response = await api.get('/business/faqs');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update business FAQs
  updateBusinessFAQs: async (faqsData) => {
    try {
      const response = await api.put('/business/faqs', faqsData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default businessApi;
