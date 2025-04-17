import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Grid, 
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Alert
} from '@mui/material';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../contexts/AuthContext';

const BusinessInfoSchema = Yup.object().shape({
  businessName: Yup.string()
    .required('Business name is required'),
  industry: Yup.string()
    .required('Industry is required'),
  address: Yup.string()
    .required('Address is required'),
  city: Yup.string()
    .required('City is required'),
  state: Yup.string()
    .required('State is required'),
  zipCode: Yup.string()
    .required('ZIP code is required'),
  phoneNumber: Yup.string()
    .required('Phone number is required'),
  website: Yup.string()
    .url('Enter a valid URL'),
  description: Yup.string()
    .max(500, 'Description must be 500 characters or less')
});

const industries = [
  'Accounting & Tax Services',
  'Automotive',
  'Beauty & Wellness',
  'Cleaning Services',
  'Construction',
  'Consulting',
  'Dental',
  'Education',
  'Event Planning',
  'Financial Services',
  'Fitness',
  'Healthcare',
  'Home Services',
  'Hospitality',
  'Insurance',
  'Legal Services',
  'Marketing & Advertising',
  'Pet Services',
  'Real Estate',
  'Retail',
  'Technology',
  'Other'
];

const BusinessInfoForm = ({ initialData = {}, onSubmit }) => {
  const { currentUser } = useAuth();
  const [userData, setUserData] = useState(null);
  
  // Get user data from localStorage if not available in context
  useEffect(() => {
    const savedData = localStorage.getItem('user_registration_data');
    if (savedData) {
      try {
        const parsedData = JSON.parse(savedData);
        setUserData(parsedData);
      } catch (e) {
        console.error('Error parsing saved user data:', e);
      }
    }
  }, []);
  
  // Determine initial values with priority: 
  // 1. Existing initialData (if provided)
  // 2. Current user data from Auth context
  // 3. Saved registration data from localStorage
  // 4. Empty string fallback
  const getInitialBusinessName = () => {
    if (initialData.businessName) return initialData.businessName;
    if (currentUser?.businessName) return currentUser.businessName;
    if (userData?.businessName) return userData.businessName;
    return '';
  };
  
  const getInitialBusinessWebsite = () => {
    if (initialData.website) return initialData.website;
    if (currentUser?.businessWebsite) return currentUser.businessWebsite;
    if (userData?.businessWebsite) return userData.businessWebsite;
    return '';
  };
  
  const getInitialPhoneNumber = () => {
    if (initialData.phoneNumber) return initialData.phoneNumber;
    if (currentUser?.phoneNumber) return currentUser.phoneNumber;
    if (userData?.phoneNumber) return userData.phoneNumber;
    return '';
  };
  
  return (
    <Formik
      initialValues={{
        businessName: getInitialBusinessName(),
        industry: initialData.industry || '',
        address: initialData.address || '',
        city: initialData.city || '',
        state: initialData.state || '',
        zipCode: initialData.zipCode || '',
        phoneNumber: getInitialPhoneNumber(),
        website: getInitialBusinessWebsite(),
        description: initialData.description || ''
      }}
      validationSchema={BusinessInfoSchema}
      onSubmit={(values) => {
        onSubmit(values);
      }}
      enableReinitialize={true}
    >
      {({ errors, touched, values, handleChange, handleBlur }) => (
        <Form>
          <Paper elevation={0} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Tell us about your business
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              This information helps Sloane provide a personalized experience for your callers.
            </Typography>
            
            {(getInitialBusinessName() || getInitialBusinessWebsite()) && (
              <Alert severity="info" sx={{ mb: 3 }}>
                We've pre-filled some information from your signup. Feel free to update it if needed.
              </Alert>
            )}
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Field name="businessName">
                  {({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Business Name"
                      variant="outlined"
                      error={touched.businessName && Boolean(errors.businessName)}
                      helperText={
                        (touched.businessName && errors.businessName) || 
                        (getInitialBusinessName() && "Pre-filled from signup")
                      }
                      sx={{
                        backgroundColor: getInitialBusinessName() ? 'rgba(25, 118, 210, 0.04)' : 'transparent',
                      }}
                    />
                  )}
                </Field>
              </Grid>
              
              <Grid item xs={12}>
                <FormControl 
                  fullWidth 
                  variant="outlined"
                  error={touched.industry && Boolean(errors.industry)}
                  sx={{
                    backgroundColor: 'transparent',
                  }}
                >
                  <InputLabel id="industry-label">Industry</InputLabel>
                  <Select
                    labelId="industry-label"
                    id="industry"
                    name="industry"
                    value={values.industry}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    label="Industry"
                  >
                    {industries.map((industry) => (
                      <MenuItem key={industry} value={industry}>
                        {industry}
                      </MenuItem>
                    ))}
                  </Select>
                  {touched.industry && errors.industry ? (
                    <FormHelperText>{errors.industry}</FormHelperText>
                  ) : null}
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <Field name="address">
                  {({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Address"
                      variant="outlined"
                      error={touched.address && Boolean(errors.address)}
                      helperText={touched.address && errors.address}
                    />
                  )}
                </Field>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <Field name="city">
                  {({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="City"
                      variant="outlined"
                      error={touched.city && Boolean(errors.city)}
                      helperText={touched.city && errors.city}
                    />
                  )}
                </Field>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <Field name="state">
                  {({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="State"
                      variant="outlined"
                      error={touched.state && Boolean(errors.state)}
                      helperText={touched.state && errors.state}
                    />
                  )}
                </Field>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <Field name="zipCode">
                  {({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="ZIP Code"
                      variant="outlined"
                      error={touched.zipCode && Boolean(errors.zipCode)}
                      helperText={touched.zipCode && errors.zipCode}
                    />
                  )}
                </Field>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Field name="phoneNumber">
                  {({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Phone Number"
                      variant="outlined"
                      error={touched.phoneNumber && Boolean(errors.phoneNumber)}
                      helperText={
                        (touched.phoneNumber && errors.phoneNumber) || 
                        (getInitialPhoneNumber() && "Pre-filled from signup")
                      }
                      sx={{
                        backgroundColor: getInitialPhoneNumber() ? 'rgba(25, 118, 210, 0.04)' : 'transparent',
                      }}
                    />
                  )}
                </Field>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Field name="website">
                  {({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Website (Optional)"
                      variant="outlined"
                      error={touched.website && Boolean(errors.website)}
                      helperText={touched.website && errors.website}
                    />
                  )}
                </Field>
              </Grid>
              
              <Grid item xs={12}>
                <Field name="description">
                  {({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Business Description (Optional)"
                      variant="outlined"
                      multiline
                      rows={4}
                      error={touched.description && Boolean(errors.description)}
                      helperText={
                        (touched.description && errors.description) || 
                        `${values.description.length}/500 characters`
                      }
                    />
                  )}
                </Field>
              </Grid>
            </Grid>
          </Paper>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              sx={{ py: 1.5, px: 4 }}
            >
              Continue
            </Button>
          </Box>
        </Form>
      )}
    </Formik>
  );
};

export default BusinessInfoForm;
