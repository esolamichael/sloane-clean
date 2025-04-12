import api from './index';

// Mock business data for Google Business search
const mockBusinessData = [
  {
    id: 'business-1',
    name: 'Oak Tree Dental Care',
    address: '123 Main Street, San Francisco, CA 94105',
    phone: '(415) 555-1234',
    website: 'https://oaktreedentalcare.com',
    hours: {
      monday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
      tuesday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
      wednesday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
      thursday: { isOpen: true, openTime: '9:00 AM', closeTime: '6:00 PM' },
      friday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
      saturday: { isOpen: true, openTime: '10:00 AM', closeTime: '2:00 PM' },
      sunday: { isOpen: false, openTime: '', closeTime: '' }
    },
    services: [
      { name: 'Teeth Cleaning', description: 'Professional dental cleaning', price: '$120' },
      { name: 'Dental Checkup', description: 'Comprehensive dental examination', price: '$85' },
      { name: 'Teeth Whitening', description: 'Professional whitening treatment', price: '$250' },
      { name: 'Dental Filling', description: 'Tooth restoration', price: '$175' }
    ],
    faqs: [
      { question: 'Do you accept insurance?', answer: 'Yes, we accept most major dental insurance plans. Please call our office to verify your coverage.' },
      { question: 'How often should I have a dental checkup?', answer: 'We recommend visiting for a checkup and cleaning every 6 months.' },
      { question: 'Do you offer emergency dental services?', answer: 'Yes, we provide emergency dental care. Please call our office as early as possible.' }
    ]
  },
  {
    id: 'business-2',
    name: 'Bay Area Tech Solutions',
    address: '789 Market Street, San Francisco, CA 94103',
    phone: '(415) 555-7890',
    website: 'https://bayareatechsolutions.com',
    hours: {
      monday: { isOpen: true, openTime: '8:00 AM', closeTime: '6:00 PM' },
      tuesday: { isOpen: true, openTime: '8:00 AM', closeTime: '6:00 PM' },
      wednesday: { isOpen: true, openTime: '8:00 AM', closeTime: '6:00 PM' },
      thursday: { isOpen: true, openTime: '8:00 AM', closeTime: '6:00 PM' },
      friday: { isOpen: true, openTime: '8:00 AM', closeTime: '5:00 PM' },
      saturday: { isOpen: false, openTime: '', closeTime: '' },
      sunday: { isOpen: false, openTime: '', closeTime: '' }
    },
    services: [
      { name: 'IT Consulting', description: 'Technology strategy and planning', price: '$150/hr' },
      { name: 'Network Setup', description: 'Business network installation', price: '$1,200' },
      { name: 'Cloud Migration', description: 'Migrate systems to cloud platforms', price: '$3,500' },
      { name: 'Cybersecurity', description: 'Security assessment and implementation', price: '$2,000' }
    ],
    faqs: [
      { question: 'Do you offer support for small businesses?', answer: 'Yes, we specialize in supporting small to medium businesses with all their IT needs.' },
      { question: 'What areas do you service?', answer: 'We service the entire Bay Area including San Francisco, Oakland, and San Jose.' },
      { question: 'Do you offer managed IT services?', answer: 'Yes, we offer comprehensive managed IT services with 24/7 monitoring and support.' }
    ]
  },
  {
    id: 'business-3',
    name: 'Golden Gate Fitness',
    address: '456 Beach Street, San Francisco, CA 94133',
    phone: '(415) 555-4321',
    website: 'https://goldengatefit.com',
    hours: {
      monday: { isOpen: true, openTime: '6:00 AM', closeTime: '9:00 PM' },
      tuesday: { isOpen: true, openTime: '6:00 AM', closeTime: '9:00 PM' },
      wednesday: { isOpen: true, openTime: '6:00 AM', closeTime: '9:00 PM' },
      thursday: { isOpen: true, openTime: '6:00 AM', closeTime: '9:00 PM' },
      friday: { isOpen: true, openTime: '6:00 AM', closeTime: '8:00 PM' },
      saturday: { isOpen: true, openTime: '8:00 AM', closeTime: '6:00 PM' },
      sunday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' }
    },
    services: [
      { name: 'Personal Training', description: 'One-on-one fitness coaching', price: '$80/session' },
      { name: 'Group Classes', description: 'Various fitness classes', price: '$25/class' },
      { name: 'Membership', description: 'Monthly gym access', price: '$89/month' },
      { name: 'Nutrition Consultation', description: 'Personalized nutrition plan', price: '$120' }
    ],
    faqs: [
      { question: 'Do you offer free trials?', answer: 'Yes, we offer a 3-day free trial for new members.' },
      { question: 'What types of classes do you offer?', answer: 'We offer yoga, spin, HIIT, pilates, and strength training classes.' },
      { question: 'Is there a joining fee?', answer: 'There is a one-time $50 joining fee for new memberships.' }
    ]
  }
];

// Function to fetch the Google Maps API key from the Netlify function
const getGoogleApiKey = async () => {
  try {
    console.log('Fetching Google API key from Netlify function...');
    
    // First try Netlify function endpoint
    try {
      const response = await fetch('/.netlify/functions/getGoogleApiKey');
      
      if (response.ok) {
        const data = await response.json();
        if (data.apiKey) {
          console.log('API key successfully received from Netlify function');
          return data.apiKey;
        } else {
          console.warn('API key missing from Netlify function response');
        }
      } else {
        console.error('Failed to fetch API key, status:', response.status);
        const text = await response.text();
        console.error('Response:', text);
      }
    } catch (netlifyError) {
      console.error('Error accessing Netlify function:', netlifyError);
    }
    
    // If we got here, Netlify function failed, try direct environment variable (for local development)
    console.log('Trying to access API key from environment directly (for local development)');
    if (process.env && process.env.REACT_APP_GOOGLE_MAPS_API_KEY) {
      console.log('Found API key in REACT_APP_GOOGLE_MAPS_API_KEY environment variable');
      return process.env.REACT_APP_GOOGLE_MAPS_API_KEY;
    }
    
    console.error('No API key available from any source');
    throw new Error('Failed to get Google Maps API key');
  } catch (error) {
    console.error('Error fetching Google API key:', error);
    throw error;
  }
};

const businessApi = {
  // Get Google API key
  getGoogleApiKey,
  
  // Search business on Google Business Profile
  searchGoogleBusiness: async (query) => {
    // Simulate API call with delay
    return new Promise((resolve) => {
      setTimeout(() => {
        // Filter businesses based on search query
        const results = mockBusinessData.filter(business => 
          business.name.toLowerCase().includes(query.toLowerCase())
        );
        resolve({ results });
      }, 1000);
    });
  },
  
  // Get business details from Google Business Profile
  getGoogleBusinessDetails: async (businessId) => {
    // Simulate API call with delay
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const business = mockBusinessData.find(b => b.id === businessId);
        if (business) {
          resolve({ business });
        } else {
          reject(new Error('Business not found'));
        }
      }, 800);
    });
  },
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