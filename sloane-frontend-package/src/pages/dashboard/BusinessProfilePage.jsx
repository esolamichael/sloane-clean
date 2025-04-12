import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Grid, 
  Paper, 
  TextField,
  Button,
  CircularProgress,
  Alert,
  Snackbar,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../contexts/AuthContext';
import businessApi from '../../api/business';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { enhancedApiCall } from '../../utils/ErrorHandling';

const BusinessProfileSchema = Yup.object().shape({
  businessName: Yup.string().required('Business name is required'),
  industry: Yup.string().required('Industry is required'),
  address: Yup.string().required('Address is required'),
  city: Yup.string().required('City is required'),
  state: Yup.string().required('State is required'),
  zipCode: Yup.string().required('ZIP code is required'),
  phoneNumber: Yup.string().required('Phone number is required'),
  website: Yup.string().url('Enter a valid URL'),
  description: Yup.string().max(500, 'Description must be 500 characters or less')
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

const BusinessProfilePage = () => {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [profileData, setProfileData] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchBusinessProfile = async () => {
try {
    setLoading(true);
    const response = await enhancedApiCall(businessApi.getBusinessProfile);
    setProfileData(response);
  } catch (error) {
    console.error('Error fetching business profile:', error);
    setError('Failed to load business profile. Please try again later.');
    // Set some default data for demonstration
    setProfileData({
      businessName: currentUser?.businessName || '',
      industry: '',
      address: '',
      city: '',
      state: '',
      zipCode: '',
      phoneNumber: '',
      website: '',
      description: ''
    });
  } finally {
    setLoading(false);
  }
};
    fetchBusinessProfile();
  }, [currentUser]);

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      setError('');
      await businessApi.updateBusinessProfile(values);
      setSuccess(true);
    } catch (error) {
      console.error('Error updating business profile:', error);
      setError('Failed to update business profile. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(false);
  };

  if (loading) {
    return <LoadingSpinner message="Loading business profile..." />;
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Business Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your business information that Sloane uses when answering calls
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        {profileData && (
          <Formik
            initialValues={profileData}
            validationSchema={BusinessProfileSchema}
            onSubmit={handleSubmit}
            enableReinitialize
          >
            {({ errors, touched, values, handleChange, handleBlur, isSubmitting }) => (
              <Form>
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
                          helperText={touched.businessName && errors.businessName}
                        />
                      )}
                    </Field>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControl 
                      fullWidth 
                      variant="outlined"
                      error={touched.industry && Boolean(errors.industry)}
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
                      {touched.industry && errors.industry && (
                        <Typography color="error" variant="caption">
                          {errors.industry}
                        </Typography>
                      )}
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
                          helperText={touched.phoneNumber && errors.phoneNumber}
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
                  
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        disabled={isSubmitting}
                        sx={{ py: 1.5, px: 4 }}
                      >
                        {isSubmitting ? (
                          <CircularProgress size={24} color="inherit" />
                        ) : (
                          'Save Changes'
                        )}
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              </Form>
            )}
          </Formik>
        )}
      </Paper>

      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          Business profile updated successfully!
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default BusinessProfilePage;
