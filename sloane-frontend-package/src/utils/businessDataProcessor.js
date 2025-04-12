// Example data processor utility
const processBusinessDataForTraining = (businessData) => {
  // Extract and format business hours
  const businessHours = {};
  if (businessData.regularHours) {
    businessData.regularHours.periods.forEach(period => {
      const day = period.openDay.toLowerCase();
      businessHours[day] = {
        isOpen: true,
        openTime: period.openTime,
        closeTime: period.closeTime
      };
    });
  }
  
  // Extract service categories and descriptions
  const services = [];
  if (businessData.categories) {
    businessData.categories.forEach(category => {
      services.push({
        name: category.displayName,
        description: '' // Google doesn't provide descriptions directly
      });
    }); 
  }
  
  // Format contact information
  const contactInfo = {
    phone: businessData.primaryPhone || '',
    website: businessData.websiteUri || '',
    email: businessData.primaryEmail || ''
  };
  
  // Build training dataset
  return {
    businessName: businessData.locationName,
    address: {
      street: businessData.address?.addressLines?.[0] || '',
      city: businessData.address?.locality || '',
      state: businessData.address?.administrativeArea || '',
      postalCode: businessData.address?.postalCode || '',
      country: businessData.address?.regionCode || ''
    },
    contactInfo,
    businessHours,
    services,
    description: businessData.profile?.description || '',
    // Other relevant data
  };
};
