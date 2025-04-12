import React, { useState, useEffect, useRef } from 'react';
import { 
  TextField, 
  Box, 
  Paper, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Typography,
  Divider,
  CircularProgress,
  InputAdornment,
  IconButton,
  Alert,
  Button
} from '@mui/material';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import StorefrontIcon from '@mui/icons-material/Storefront';
import SearchIcon from '@mui/icons-material/Search';
import PhoneIcon from '@mui/icons-material/Phone';
import businessApi from '../../api/business';

// Google Maps API key is now loaded directly from index.html 
// No need to define it here as we're not loading the API from the component

// Sample business data for fallback when Google Places API is unavailable
const SAMPLE_BUSINESSES = [
  // Los Angeles Businesses
  {
    id: 'la-business-1',
    name: 'LA Dental Studio',
    description: 'Dentist in Los Angeles, CA',
    address: '2500 Wilshire Blvd, Los Angeles, CA 90057',
    phone: '(213) 555-1234',
    website: 'https://ladentalstudio.com',
    businessType: 'dentist',
    location: { lat: 34.0610, lng: -118.2765 }
  },
  // ... more sample businesses here
];

const GooglePlacesAutocomplete = ({ onBusinessSelect }) => {
  const [inputValue, setInputValue] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [useGooglePlaces, setUseGooglePlaces] = useState(false);
  const [googleApiLoaded, setGoogleApiLoaded] = useState(false);
  const [googleApiError, setGoogleApiError] = useState(null);
  const autocompleteService = useRef(null);
  const placesService = useRef(null);
  const sessionToken = useRef(null);

  // State for location loading & error
  const [locationLoading, setLocationLoading] = useState(false);
  const [locationError, setLocationError] = useState(null);

  // Just initialize Google Services - API is loaded from index.html
  useEffect(() => {
    // Register a callback for when API loads (in case it hasn't loaded yet)
    window.googleMapsCallbacks = window.googleMapsCallbacks || [];
    window.googleMapsCallbacks.push(() => {
      console.log('✅ API loaded callback triggered');
      initializeGoogleServices();
      setGoogleApiLoaded(true);
      setUseGooglePlaces(true);
    });
    
    // If API is already loaded, initialize immediately
    if (window.google && window.google.maps && window.google.maps.places) {
      console.log('✅ Google Maps API already available in window');
      initializeGoogleServices();
      setGoogleApiLoaded(true);
      setUseGooglePlaces(true);
    } 
    // If googleMapsLoaded flag is true, also initialize
    else if (window.googleMapsLoaded) {
      console.log('✅ Google Maps API already loaded via global script');
      initializeGoogleServices();
      setGoogleApiLoaded(true);
      setUseGooglePlaces(true);
    }
    else {
      console.log('⏳ Waiting for Google Maps API to load from index.html script...');
    }
  }, []);

  // Initialize Google services when API is loaded
  const initializeGoogleServices = () => {
    console.log('🔄 Attempting to initialize Google services');
    
    if (!window.google) {
      console.error('❌ window.google is undefined');
      return;
    }
    
    if (!window.google.maps) {
      console.error('❌ window.google.maps is undefined');
      return;
    }
    
    if (!window.google.maps.places) {
      console.error('❌ window.google.maps.places is undefined');
      return;
    }
    
    try {
      console.log('🔄 Initializing Google Maps services...');
      
      // Check available Google Maps APIs
      console.log('Available Google Maps APIs:', {
        places: !!window.google.maps.places,
        PlacesService: !!window.google.maps.places.PlacesService,
        AutocompleteService: !!window.google.maps.places.AutocompleteService,
        AutocompleteSessionToken: !!window.google.maps.places.AutocompleteSessionToken
      });
      
      // Create a session token
      sessionToken.current = new window.google.maps.places.AutocompleteSessionToken();
      console.log('✅ Created session token');
      
      // Initialize the autocomplete service
      autocompleteService.current = new window.google.maps.places.AutocompleteService();
      console.log('✅ Created autocomplete service');
      
      // Initialize the Places service (needs a map div)
      const mapDiv = document.createElement('div');
      console.log('🗺️ Creating map instance for Places service');
      const map = new window.google.maps.Map(mapDiv, { 
        center: { lat: 0, lng: 0 }, 
        zoom: 1 
      });
      placesService.current = new window.google.maps.places.PlacesService(map);
      console.log('✅ Created places service');
      
      console.log('✅ Google Maps services initialized successfully');
    } catch (error) {
      console.error('❌ Error initializing Google services:', error);
      console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        where: error.toString()
      });
      setGoogleApiError(`Failed to initialize Google services: ${error.message}. Using fallback data.`);
      setUseGooglePlaces(false);
    }
  };

  // Try to get user's location on component mount
  useEffect(() => {
    if (navigator.geolocation) {
      setLocationLoading(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
          setLocationLoading(false);
          setLocationError(null);
        },
        (error) => {
          console.log('Geolocation error or permission denied:', error);
          setLocationLoading(false);
          
          // Set a user-friendly error message based on the error code
          switch(error.code) {
            case error.PERMISSION_DENIED:
              setLocationError("Location access denied. Using nationwide business search.");
              break;
            case error.POSITION_UNAVAILABLE:
              setLocationError("Location information unavailable. Using nationwide business search.");
              break;
            case error.TIMEOUT:
              setLocationError("Location request timed out. Using nationwide business search.");
              break;
            default:
              setLocationError("An unknown error occurred. Using nationwide business search.");
          }
          
          // Provide a default location in the center of US if geolocation fails
          setUserLocation({
            lat: 39.8283, // Approximate center of the United States
            lng: -98.5795
          });
        },
        { 
          timeout: 10000, // 10 second timeout
          maximumAge: 600000 // 10 minutes cache
        }
      );
    } else {
      setLocationError("Geolocation is not supported by your browser. Using nationwide business search.");
      
      // Provide a default location in the center of US if geolocation is not supported
      setUserLocation({
        lat: 39.8283, // Approximate center of the United States
        lng: -98.5795
      });
    }
  }, []);

  // Calculate distance between two points using Haversine formula
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    if (!lat1 || !lon1 || !lat2 || !lon2) return Infinity;
    
    const R = 6371; // Radius of the earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2); 
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
    const distance = R * c; // Distance in km
    return distance;
  };

  // Get Google Places predictions
  const getGooglePlacesPredictions = (query) => {
    console.log('🔍 getGooglePlacesPredictions called with:', query);
    
    if (!autocompleteService.current) {
      console.error('❌ Autocomplete service not initialized');
      return Promise.resolve([]);
    }
    
    if (!query || query.length < 2) {
      console.log('ℹ️ Query too short, skipping API call');
      return Promise.resolve([]);
    }
    
    return new Promise((resolve) => {
      try {
        // Prepare the request
        const request = {
          input: query,
          types: ['establishment']
        };
        
        // Add session token if available
        if (sessionToken.current) {
          request.sessionToken = sessionToken.current;
        }
        
        // Add location bias if user location is available
        if (userLocation) {
          request.locationBias = {
            center: userLocation,
            radius: 50000 // 50km radius
          };
        }
        
        // Get predictions
        autocompleteService.current.getPlacePredictions(
          request,
          (predictions, status) => {
            if (status !== window.google.maps.places.PlacesServiceStatus.OK || !predictions) {
              console.warn('Places API returned status:', status);
              resolve([]);
              return;
            }
            
            console.log(`Received ${predictions.length} predictions from Places API`);
            resolve(predictions);
          }
        );
      } catch (error) {
        console.error('Error in getPlacePredictions:', error);
        resolve([]);
      }
    });
  };
  
  // Get details for a selected place
  const getPlaceDetails = (placeId) => {
    console.log('🔍 getPlaceDetails called for place ID:', placeId);
    
    if (!placesService.current) {
      console.error('❌ Places service not initialized');
      return Promise.reject(new Error('Places service not initialized'));
    }
    
    return new Promise((resolve, reject) => {
      try {
        const fields = ['name', 'formatted_address', 'formatted_phone_number', 'website', 'geometry', 'types'];
        
        placesService.current.getDetails(
          {
            placeId: placeId,
            fields: fields
          },
          (place, status) => {
            if (status !== window.google.maps.places.PlacesServiceStatus.OK || !place) {
              console.error('Error fetching place details. Status:', status);
              reject(new Error(`Error fetching place details: ${status}`));
              return;
            }
            
            console.log('Successfully retrieved place details');
            resolve(place);
          }
        );
      } catch (error) {
        console.error('Error in getPlaceDetails:', error);
        reject(error);
      }
    });
  };

  // Filter businesses based on search term and location for fallback
  const filterBusinesses = (searchTerm) => {
    if (!searchTerm || searchTerm.length < 2) return [];
    
    const lowercaseSearch = searchTerm.toLowerCase();
    
    // First find all matches based on name or description
    const exactMatches = SAMPLE_BUSINESSES.filter(business => 
      business.name.toLowerCase() === lowercaseSearch
    );
    
    const startsWithMatches = SAMPLE_BUSINESSES.filter(business => 
      business.name.toLowerCase().startsWith(lowercaseSearch) &&
      !exactMatches.includes(business)
    );
    
    const containsMatches = SAMPLE_BUSINESSES.filter(business => 
      (business.name.toLowerCase().includes(lowercaseSearch) || 
       business.description.toLowerCase().includes(lowercaseSearch)) &&
      !exactMatches.includes(business) &&
      !startsWithMatches.includes(business)
    );
    
    // Combine matches with precedence: exact > starts with > contains
    let allMatches = [...exactMatches, ...startsWithMatches, ...containsMatches];
    
    // If user has shared location, apply proximity sorting within each match category
    if (userLocation) {
      // Helper function to sort by distance
      const sortByDistance = (businesses) => {
        return businesses.sort((a, b) => {
          const distanceA = a.location ? 
            calculateDistance(userLocation.lat, userLocation.lng, a.location.lat, a.location.lng) : 
            Infinity;
          
          const distanceB = b.location ? 
            calculateDistance(userLocation.lat, userLocation.lng, b.location.lat, b.location.lng) : 
            Infinity;
          
          return distanceA - distanceB;
        });
      };
      
      // Sort each category by distance and combine
      const sortedExact = sortByDistance([...exactMatches]);
      const sortedStartsWith = sortByDistance([...startsWithMatches]);
      const sortedContains = sortByDistance([...containsMatches]);
      
      // Only return businesses within 50km of user for containsMatches
      // This will prioritize local results over distant ones that happen to match
      const localContainsMatches = sortedContains.filter(business => {
        if (!business.location) return true; // Keep businesses without location data
        
        const distance = calculateDistance(
          userLocation.lat, userLocation.lng, 
          business.location.lat, business.location.lng
        );
        
        return distance <= 50; // Only include businesses within 50km for partial matches
      });
      
      allMatches = [...sortedExact, ...sortedStartsWith, ...localContainsMatches];
    }
    
    return allMatches;
  };

  // Handle input change and update predictions
  const handleInputChange = async (e) => {
    const value = e.target.value;
    setInputValue(value);
    
    if (value.length >= 2) {
      setLoading(true);
      setError(null);
      
      try {
        let results = [];
        
        if (useGooglePlaces && googleApiLoaded) {
          // Use Google Places API
          const predictions = await getGooglePlacesPredictions(value);
          results = predictions.map(prediction => ({
            id: prediction.place_id,
            name: prediction.structured_formatting.main_text,
            description: prediction.description,
            address: prediction.structured_formatting.secondary_text,
            isGooglePlace: true
          }));
        } else {
          // Use fallback data
          results = filterBusinesses(value);
        }
        
        setPredictions(results);
        
        if (results.length === 0 && value.length > 2) {
          setError(
            `No matches found for "${value}". Try a different search term or create a custom business below.`
          );
        }
      } catch (error) {
        console.error('Error getting predictions:', error);
        setError('Error searching for businesses. Using fallback data.');
        
        // Fallback to sample data if Google Places fails
        const fallbackResults = filterBusinesses(value);
        setPredictions(fallbackResults);
      } finally {
        setLoading(false);
      }
    } else {
      setPredictions([]);
    }
  };

  // Handle manual search button click
  const handleSearch = async () => {
    if (inputValue.trim().length >= 2) {
      setLoading(true);
      setError(null);
      
      try {
        let results = [];
        
        if (useGooglePlaces && googleApiLoaded) {
          // Use Google Places API
          const predictions = await getGooglePlacesPredictions(inputValue);
          results = predictions.map(prediction => ({
            id: prediction.place_id,
            name: prediction.structured_formatting.main_text,
            description: prediction.description,
            address: prediction.structured_formatting.secondary_text,
            isGooglePlace: true
          }));
        } else {
          // Use fallback data
          results = filterBusinesses(inputValue);
        }
        
        setPredictions(results);
        
        if (results.length === 0) {
          setError(
            `No matches found for "${inputValue}". Try a different search term or create a custom business below.`
          );
        }
      } catch (error) {
        console.error('Error in search:', error);
        setError('Error searching for businesses. Using fallback data.');
        
        // Fallback to sample data if Google Places fails
        const fallbackResults = filterBusinesses(inputValue);
        setPredictions(fallbackResults);
      } finally {
        setLoading(false);
      }
    }
  };

  // Determine business type from Google Place types
  const getBusinessTypeFromTypes = (types) => {
    if (!types || types.length === 0) return 'other';
    
    if (types.includes('dentist')) return 'dentist';
    if (types.includes('doctor') || types.includes('hospital') || types.includes('health')) return 'medical';
    if (types.includes('gym') || types.includes('fitness_center')) return 'fitness';
    if (types.includes('restaurant') || types.includes('cafe') || types.includes('food')) return 'restaurant';
    if (types.includes('hair_care') || types.includes('beauty_salon')) return 'salon';
    if (types.includes('storage') || types.includes('moving_company')) return 'storage';
    if (types.includes('lawyer') || types.includes('attorney')) return 'legal';
    if (types.includes('accounting') || types.includes('finance')) return 'financial';
    if (types.includes('real_estate_agency')) return 'realestate';
    if (types.includes('lodging') || types.includes('hotel')) return 'hospitality';
    
    // Check for tech business types
    if (types.includes('electronics_store') || 
        types.includes('computer_store') || 
        types.some(type => type.includes('tech'))) {
      return 'tech_services';
    }
    
    return 'other';
  };

  // Handle selection of a business from the predictions
  const handleSelectBusiness = async (business) => {
    setInputValue(business.name);
    setPredictions([]);
    setLoading(true);
    
    try {
      // For Google Places results, fetch more details
      if (business.isGooglePlace) {
        const placeDetails = await getPlaceDetails(business.id);
        
        // Determine business type from place types
        const businessType = getBusinessTypeFromTypes(placeDetails.types);
        
        // Format Google Places result
        const formattedBusiness = {
          id: business.id,
          name: placeDetails.name,
          address: placeDetails.formatted_address || business.address,
          phone: placeDetails.formatted_phone_number || '',
          website: placeDetails.website || '',
          location: placeDetails.geometry?.location ? {
            lat: placeDetails.geometry.location.lat(),
            lng: placeDetails.geometry.location.lng()
          } : null,
          hours: getBusinessHours(businessType),
          services: getBusinessServices(businessType),
          faqs: getBusinessFAQs(businessType)
        };
        
        // Pass formatted business data to parent component
        if (onBusinessSelect) {
          onBusinessSelect(formattedBusiness);
        }
      } else {
        // For fallback data, use the business object directly
        const formattedBusiness = {
          id: business.id,
          name: business.name,
          address: business.address,
          phone: business.phone,
          website: business.website,
          location: business.location,
          hours: getBusinessHours(business.businessType),
          services: getBusinessServices(business.businessType),
          faqs: getBusinessFAQs(business.businessType)
        };
        
        // Pass formatted business data to parent component
        if (onBusinessSelect) {
          onBusinessSelect(formattedBusiness);
        }
      }
    } catch (error) {
      console.error('Error getting business details:', error);
      setError('Error retrieving business details. Please try again.');
      
      // Still try to use the basic information we have
      const formattedBusiness = {
        id: business.id,
        name: business.name,
        address: business.address || '',
        phone: '',
        website: '',
        hours: getBusinessHours('other'),
        services: getBusinessServices('other'),
        faqs: getBusinessFAQs('other')
      };
      
      if (onBusinessSelect) {
        onBusinessSelect(formattedBusiness);
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle key press events (mainly for Enter key)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Handle creation of custom business
  const handleCreateCustomBusiness = () => {
    // Create a custom business based on user input
    const customBusiness = {
      id: `custom-${Date.now()}`,
      name: inputValue,
      description: `Custom business created from search`,
      address: userLocation ? 'Near your location' : '123 Main St',
      phone: '(555) 123-4567',
      website: `https://${inputValue.toLowerCase().replace(/\s+/g, '')}.example.com`,
      businessType: 'custom',
      location: userLocation ? { lat: userLocation.lat, lng: userLocation.lng } : null
    };
    handleSelectBusiness(customBusiness);
  };

  // Get business hours based on business type
  const getBusinessHours = (businessType) => {
    // Default hours (9-5 weekdays)
    const defaultHours = {
      monday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
      tuesday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
      wednesday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
      thursday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
      friday: { isOpen: true, openTime: '9:00 AM', closeTime: '5:00 PM' },
      saturday: { isOpen: false, openTime: '', closeTime: '' },
      sunday: { isOpen: false, openTime: '', closeTime: '' }
    };
    
    // Type-specific hours
    switch (businessType) {
      case 'restaurant':
        return {
          monday: { isOpen: true, openTime: '7:00 AM', closeTime: '10:00 PM' },
          tuesday: { isOpen: true, openTime: '7:00 AM', closeTime: '10:00 PM' },
          wednesday: { isOpen: true, openTime: '7:00 AM', closeTime: '10:00 PM' },
          thursday: { isOpen: true, openTime: '7:00 AM', closeTime: '10:00 PM' },
          friday: { isOpen: true, openTime: '7:00 AM', closeTime: '11:00 PM' },
          saturday: { isOpen: true, openTime: '8:00 AM', closeTime: '11:00 PM' },
          sunday: { isOpen: true, openTime: '8:00 AM', closeTime: '9:00 PM' }
        };
      case 'fitness':
        return {
          monday: { isOpen: true, openTime: '6:00 AM', closeTime: '10:00 PM' },
          tuesday: { isOpen: true, openTime: '6:00 AM', closeTime: '10:00 PM' },
          wednesday: { isOpen: true, openTime: '6:00 AM', closeTime: '10:00 PM' },
          thursday: { isOpen: true, openTime: '6:00 AM', closeTime: '10:00 PM' },
          friday: { isOpen: true, openTime: '6:00 AM', closeTime: '10:00 PM' },
          saturday: { isOpen: true, openTime: '7:00 AM', closeTime: '8:00 PM' },
          sunday: { isOpen: true, openTime: '8:00 AM', closeTime: '6:00 PM' }
        };
      case 'dentist':
      case 'medical':
        return {
          monday: { isOpen: true, openTime: '8:00 AM', closeTime: '5:00 PM' },
          tuesday: { isOpen: true, openTime: '8:00 AM', closeTime: '5:00 PM' },
          wednesday: { isOpen: true, openTime: '8:00 AM', closeTime: '5:00 PM' },
          thursday: { isOpen: true, openTime: '8:00 AM', closeTime: '5:00 PM' },
          friday: { isOpen: true, openTime: '8:00 AM', closeTime: '5:00 PM' },
          saturday: { isOpen: true, openTime: '9:00 AM', closeTime: '1:00 PM' },
          sunday: { isOpen: false, openTime: '', closeTime: '' }
        };
      default:
        return defaultHours;
    }
  };

  // Get business services based on business type
  const getBusinessServices = (businessType) => {
    // For custom businesses, try to guess appropriate services based on name
    if (businessType === 'custom') {
      const businessName = inputValue.toLowerCase();
      
      // Check for different business types in the name
      if (businessName.includes('dental') || businessName.includes('dentist') || businessName.includes('smile')) {
        return [
          { name: 'Teeth Cleaning', description: 'Professional dental cleaning', price: '$120' },
          { name: 'Dental Checkup', description: 'Comprehensive dental examination', price: '$85' },
          { name: 'Teeth Whitening', description: 'Professional whitening treatment', price: '$250' },
          { name: 'Dental Filling', description: 'Tooth restoration', price: '$175' }
        ];
      } else if (businessName.includes('tech') || businessName.includes('IT') || businessName.includes('computer') || businessName.includes('digital')) {
        return [
          { name: 'IT Consulting', description: 'Technology strategy and planning', price: '$150/hr' },
          { name: 'Network Setup', description: 'Business network installation', price: '$1,200' },
          { name: 'Cloud Migration', description: 'Migrate systems to cloud platforms', price: '$3,500' },
          { name: 'Cybersecurity', description: 'Security assessment and implementation', price: '$2,000' }
        ];
      } else if (businessName.includes('fitness') || businessName.includes('gym') || businessName.includes('workout') || businessName.includes('health')) {
        return [
          { name: 'Personal Training', description: 'One-on-one fitness coaching', price: '$80/session' },
          { name: 'Group Classes', description: 'Various fitness classes', price: '$25/class' },
          { name: 'Membership', description: 'Monthly gym access', price: '$89/month' },
          { name: 'Nutrition Consultation', description: 'Personalized nutrition plan', price: '$120' }
        ];
      } else if (businessName.includes('restaurant') || businessName.includes('cafe') || businessName.includes('bistro') || businessName.includes('kitchen')) {
        return [
          { name: 'Lunch Special', description: 'Weekday lunch menu', price: '$15' },
          { name: 'Dinner Menu', description: 'Full dinner service', price: '$25-45' },
          { name: 'Catering', description: 'Group and event catering', price: 'Varies' },
          { name: 'Private Dining', description: 'Reserved dining areas', price: 'Minimum spend $500' }
        ];
      } else if (businessName.includes('salon') || businessName.includes('hair') || businessName.includes('beauty') || businessName.includes('spa')) {
        return [
          { name: 'Haircut', description: 'Professional styling', price: '$45-65' },
          { name: 'Color Treatment', description: 'Hair coloring services', price: '$80-120' },
          { name: 'Manicure', description: 'Nail care service', price: '$35' },
          { name: 'Facial', description: 'Skin treatment', price: '$75' }
        ];
      } else if (businessName.includes('medical') || businessName.includes('clinic') || businessName.includes('health') || businessName.includes('doctor')) {
        return [
          { name: 'General Consultation', description: 'Initial medical consultation', price: '$150' },
          { name: 'Physical Examination', description: 'Comprehensive health checkup', price: '$200' },
          { name: 'Follow-up Visit', description: 'Post-treatment check', price: '$100' },
          { name: 'Specialized Testing', description: 'Medical diagnostic tests', price: '$75-400' }
        ];
      }
      
      // Default custom business services
      return [
        { name: `${inputValue} Standard Service`, description: 'Our most popular service', price: '$99' },
        { name: `${inputValue} Premium Package`, description: 'Enhanced service offering', price: '$149' },
        { name: 'Consultation', description: 'Professional consultation', price: '$75' },
        { name: 'Custom Solutions', description: 'Tailored to your specific needs', price: 'Varies' }
      ];
    }
    
    // For predefined business types
    switch (businessType) {
      case 'dentist':
        return [
          { name: 'Teeth Cleaning', description: 'Professional dental cleaning', price: '$120' },
          { name: 'Dental Checkup', description: 'Comprehensive dental examination', price: '$85' },
          { name: 'Teeth Whitening', description: 'Professional whitening treatment', price: '$250' },
          { name: 'Dental Filling', description: 'Tooth restoration', price: '$175' }
        ];
      case 'tech_services':
        return [
          { name: 'IT Consulting', description: 'Technology strategy and planning', price: '$150/hr' },
          { name: 'Network Setup', description: 'Business network installation', price: '$1,200' },
          { name: 'Cloud Migration', description: 'Migrate systems to cloud platforms', price: '$3,500' },
          { name: 'Cybersecurity', description: 'Security assessment and implementation', price: '$2,000' }
        ];
      case 'fitness':
        return [
          { name: 'Personal Training', description: 'One-on-one fitness coaching', price: '$80/session' },
          { name: 'Group Classes', description: 'Various fitness classes', price: '$25/class' },
          { name: 'Membership', description: 'Monthly gym access', price: '$89/month' },
          { name: 'Nutrition Consultation', description: 'Personalized nutrition plan', price: '$120' }
        ];
      case 'restaurant':
        return [
          { name: 'Lunch Special', description: 'Weekday lunch menu', price: '$15' },
          { name: 'Dinner Menu', description: 'Full dinner service', price: '$25-45' },
          { name: 'Catering', description: 'Group and event catering', price: 'Varies' },
          { name: 'Private Dining', description: 'Reserved dining areas', price: 'Minimum spend $500' }
        ];
      case 'salon':
        return [
          { name: 'Haircut', description: 'Professional styling', price: '$45-65' },
          { name: 'Color Treatment', description: 'Hair coloring services', price: '$80-120' },
          { name: 'Manicure', description: 'Nail care service', price: '$35' },
          { name: 'Facial', description: 'Skin treatment', price: '$75' }
        ];
      case 'medical':
        return [
          { name: 'General Consultation', description: 'Initial medical consultation', price: '$150' },
          { name: 'Physical Examination', description: 'Comprehensive health checkup', price: '$200' },
          { name: 'Follow-up Visit', description: 'Post-treatment check', price: '$100' },
          { name: 'Specialized Testing', description: 'Medical diagnostic tests', price: '$75-400' }
        ];
      default:
        return [
          { name: 'Standard Service', description: 'Our most popular service', price: '$99' },
          { name: 'Premium Package', description: 'Enhanced service offering', price: '$149' },
          { name: 'Consultation', description: 'Professional consultation', price: '$75' }
        ];
    }
  };

  // Get business FAQs based on business type
  const getBusinessFAQs = (businessType) => {
    const generalFAQs = [
      { 
        question: 'What are your hours of operation?', 
        answer: 'Please check our business profile for up-to-date hours of operation.'
      },
      { 
        question: 'Do you accept credit cards?', 
        answer: 'Yes, we accept all major credit cards including Visa, MasterCard, American Express, and Discover.'
      }
    ];
    
    // For custom businesses, create FAQs based on the name
    if (businessType === 'custom') {
      const businessName = inputValue.toLowerCase();
      
      // Default custom business FAQs
      let customFAQs = [
        { question: `How long has ${inputValue} been in business?`, answer: 'We have been proudly serving our customers for over 5 years.' },
        { question: `What makes ${inputValue} different from competitors?`, answer: 'We pride ourselves on exceptional customer service and personalized solutions for each client.' }
      ];
      
      // Add industry-specific FAQs based on business name keywords
      if (businessName.includes('dental') || businessName.includes('dentist') || businessName.includes('smile')) {
        customFAQs = [
          { question: 'Do you accept insurance?', answer: 'Yes, we accept most major dental insurance plans. Please call our office to verify your coverage.' },
          { question: 'How often should I have a dental checkup?', answer: 'We recommend visiting for a checkup and cleaning every 6 months.' },
          { question: 'Do you offer emergency dental services?', answer: 'Yes, we provide emergency dental care. Please call our office as early as possible.' }
        ];
      } else if (businessName.includes('tech') || businessName.includes('IT') || businessName.includes('computer')) {
        customFAQs = [
          { question: 'Do you offer support for small businesses?', answer: 'Yes, we specialize in supporting small to medium businesses with all their IT needs.' },
          { question: 'What areas do you service?', answer: 'We service the entire local area and surrounding regions.' },
          { question: 'Do you offer managed IT services?', answer: 'Yes, we offer comprehensive managed IT services with 24/7 monitoring and support.' }
        ];
      } else if (businessName.includes('fitness') || businessName.includes('gym') || businessName.includes('workout')) {
        customFAQs = [
          { question: 'Do you offer free trials?', answer: 'Yes, we offer a 3-day free trial for new members.' },
          { question: 'What types of classes do you offer?', answer: 'We offer yoga, spin, HIIT, pilates, and strength training classes.' },
          { question: 'Is there a joining fee?', answer: 'There is a one-time $50 joining fee for new memberships.' }
        ];
      } else if (businessName.includes('restaurant') || businessName.includes('cafe') || businessName.includes('bistro')) {
        customFAQs = [
          { question: 'Do you take reservations?', answer: 'Yes, we accept reservations for parties of any size. We recommend booking in advance for weekends.' },
          { question: 'Do you have vegetarian/vegan options?', answer: 'Yes, we offer several vegetarian and vegan options on our menu.' },
          { question: 'Do you offer takeout or delivery?', answer: 'Yes, we offer both takeout and delivery through our website and popular delivery apps.' }
        ];
      }
      
      return [...customFAQs, ...generalFAQs];
    }
    
    // For predefined business types
    let specificFAQs = [];
    
    switch (businessType) {
      case 'dentist':
        specificFAQs = [
          { question: 'Do you accept insurance?', answer: 'Yes, we accept most major dental insurance plans. Please call our office to verify your coverage.' },
          { question: 'How often should I have a dental checkup?', answer: 'We recommend visiting for a checkup and cleaning every 6 months.' },
          { question: 'Do you offer emergency dental services?', answer: 'Yes, we provide emergency dental care. Please call our office as early as possible.' }
        ];
        break;
      case 'tech_services':
        specificFAQs = [
          { question: 'Do you offer support for small businesses?', answer: 'Yes, we specialize in supporting small to medium businesses with all their IT needs.' },
          { question: 'What areas do you service?', answer: 'We service the entire local area and surrounding regions.' },
          { question: 'Do you offer managed IT services?', answer: 'Yes, we offer comprehensive managed IT services with 24/7 monitoring and support.' }
        ];
        break;
      case 'fitness':
        specificFAQs = [
          { question: 'Do you offer free trials?', answer: 'Yes, we offer a 3-day free trial for new members.' },
          { question: 'What types of classes do you offer?', answer: 'We offer yoga, spin, HIIT, pilates, and strength training classes.' },
          { question: 'Is there a joining fee?', answer: 'There is a one-time $50 joining fee for new memberships.' }
        ];
        break;
      case 'restaurant':
        specificFAQs = [
          { question: 'Do you take reservations?', answer: 'Yes, we accept reservations for parties of any size. We recommend booking in advance for weekends.' },
          { question: 'Do you have vegetarian/vegan options?', answer: 'Yes, we offer several vegetarian and vegan options on our menu.' },
          { question: 'Do you offer takeout or delivery?', answer: 'Yes, we offer both takeout and delivery through our website and popular delivery apps.' }
        ];
        break;
      case 'salon':
        specificFAQs = [
          { question: 'Do I need to make an appointment?', answer: 'Yes, appointments are recommended, but we do accept walk-ins based on availability.' },
          { question: 'What services do you offer?', answer: 'We offer a full range of salon services including haircuts, coloring, styling, manicures, pedicures, and facials.' },
          { question: 'Do you offer gift certificates?', answer: 'Yes, gift certificates are available for purchase in-store or on our website.' }
        ];
        break;
      case 'medical':
        specificFAQs = [
          { question: 'Do you accept insurance?', answer: 'Yes, we accept most major health insurance plans. Please contact our office to verify your coverage.' },
          { question: 'How do I schedule an appointment?', answer: 'You can schedule an appointment by calling our office or using our online booking system on our website.' },
          { question: 'What should I bring to my first appointment?', answer: 'Please bring your insurance card, ID, medical history, and a list of current medications.' }
        ];
        break;
      default:
        specificFAQs = [
          { question: 'How can I contact customer service?', answer: 'You can reach our customer service team by phone, email, or through the contact form on our website.' },
          { question: 'Do you offer any discounts?', answer: 'We offer seasonal promotions and discounts. Sign up for our newsletter to be notified of upcoming offers.' }
        ];
    }
    
    return [...specificFAQs, ...generalFAQs];
  };

  return (
    <Box sx={{ position: 'relative', width: '100%' }}>
      {googleApiError && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {googleApiError} You can still search for and create businesses using our default database.
        </Alert>
      )}
      
      <TextField
        fullWidth
        placeholder="Start typing a business name..."
        value={inputValue}
        onChange={handleInputChange}
        onKeyPress={handleKeyPress}
        variant="outlined"
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              {loading ? (
                <CircularProgress size={20} />
              ) : (
                <IconButton 
                  edge="end" 
                  onClick={handleSearch}
                  disabled={inputValue.trim().length < 2}
                >
                  <SearchIcon />
                </IconButton>
              )}
            </InputAdornment>
          ),
        }}
        sx={{ mb: 1 }}
      />
      
      {/* Location status message */}
      {locationLoading ? (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <CircularProgress size={12} sx={{ mr: 1 }} />
          Detecting your location for better search results...
        </Typography>
      ) : locationError ? (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          {locationError}
        </Typography>
      ) : userLocation && (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <LocationOnIcon fontSize="small" sx={{ fontSize: '14px', mr: 0.5 }} />
          Using your current location for better local search results
        </Typography>
      )}
      
      {error && (
        <Alert severity="info" sx={{ mt: 1, mb: 1 }}>
          {error}
          {inputValue.length > 2 && predictions.length === 0 && (
            <Box sx={{ mt: 1 }}>
              <Button 
                variant="outlined" 
                size="small" 
                color="primary"
                onClick={handleCreateCustomBusiness}
                sx={{ mt: 1 }}
              >
                Use "{inputValue}" for my business
              </Button>
            </Box>
          )}
        </Alert>
      )}
      
      {/* Predictions dropdown */}
      {predictions.length > 0 && (
        <Paper 
          elevation={3} 
          sx={{ 
            position: 'absolute',
            width: '100%', 
            mt: 0.5, 
            zIndex: 10,
            maxHeight: 350,
            overflow: 'auto'
          }}
        >
          <List dense>
            {predictions.map((business) => (
              <React.Fragment key={business.id}>
                <ListItem 
                  button 
                  onClick={() => handleSelectBusiness(business)}
                  sx={{ py: 1.5 }}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    <StorefrontIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body1" fontWeight="medium">
                        {business.name}
                      </Typography>
                    }
                    secondary={
                      <>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', mt: 0.5 }}>
                          <LocationOnIcon fontSize="small" sx={{ mr: 0.5, mt: 0.3, fontSize: '0.9rem', color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            {business.address}
                          </Typography>
                        </Box>
                        {userLocation && business.location && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                            {(calculateDistance(
                              userLocation.lat, 
                              userLocation.lng, 
                              business.location.lat, 
                              business.location.lng
                            ) * 0.621371).toFixed(1)} miles from your location
                          </Typography>
                        )}
                      </>
                    }
                  />
                </ListItem>
                <Divider component="li" />
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default GooglePlacesAutocomplete;
