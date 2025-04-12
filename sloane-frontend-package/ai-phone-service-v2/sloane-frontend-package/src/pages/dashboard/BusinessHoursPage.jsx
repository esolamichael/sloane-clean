import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Grid, 
  Paper, 
  Card,
  CardContent,
  Button,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  Snackbar
} from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import businessApi from '../../api/business';

const BusinessHoursSchema = Yup.object().shape({
  monday: Yup.object().shape({
    isOpen: Yup.boolean(),
    openTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Opening time is required')
    }),
    closeTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Closing time is required')
    })
  }),
  tuesday: Yup.object().shape({
    isOpen: Yup.boolean(),
    openTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Opening time is required')
    }),
    closeTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Closing time is required')
    })
  }),
  wednesday: Yup.object().shape({
    isOpen: Yup.boolean(),
    openTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Opening time is required')
    }),
    closeTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Closing time is required')
    })
  }),
  thursday: Yup.object().shape({
    isOpen: Yup.boolean(),
    openTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Opening time is required')
    }),
    closeTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Closing time is required')
    })
  }),
  friday: Yup.object().shape({
    isOpen: Yup.boolean(),
    openTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Opening time is required')
    }),
    closeTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Closing time is required')
    })
  }),
  saturday: Yup.object().shape({
    isOpen: Yup.boolean(),
    openTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Opening time is required')
    }),
    closeTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Closing time is required')
    })
  }),
  sunday: Yup.object().shape({
    isOpen: Yup.boolean(),
    openTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Opening time is required')
    }),
    closeTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Closing time is required')
    })
  }),
  customMessage: Yup.string().max(500, 'Message must be 500 characters or less')
});

const defaultOpenTime = new Date();
defaultOpenTime.setHours(9, 0, 0);

const defaultCloseTime = new Date();
defaultCloseTime.setHours(17, 0, 0);

const BusinessHoursPage = () => {
  const [loading, setLoading] = useState(true);
  const [hoursData, setHoursData] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchBusinessHours = async () => {
      try {
        setLoading(true);
        const response = await businessApi.getBusinessHours();
        setHoursData(response);
      } catch (error) {
        console.error('Error fetching business hours:', error);
        setError('Failed to load business hours. Please try again later.');
        
        // Set default data for demonstration
        const defaultDay = {
          isOpen: true,
          openTime: defaultOpenTime,
          closeTime: defaultCloseTime
        };
        
        setHoursData({
          monday: { ...defaultDay },
          tuesday: { ...defaultDay },
          wednesday: { ...defaultDay },
          thursday: { ...defaultDay },
          friday: { ...defaultDay },
          saturday: { ...defaultDay, isOpen: false },
          sunday: { ...defaultDay, isOpen: false },
          customMessage: ''
        });
      } finally {
        setLoading(false);
      }
    };

    fetchBusinessHours();
  }, []);

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      setError('');
      await businessApi.updateBusinessHours(values);
      setSuccess(true);
    } catch (error) {
      console.error('Error updating business hours:', error);
      setError('Failed to update business hours. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(false);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Business Hours
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Set your business hours so Sloane knows when to answer calls
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ p: 3 }}>
          {hoursData && (
            <Formik
              initialValues={hoursData}
              validationSchema={BusinessHoursSchema}
              onSubmit={handleSubmit}
              enableReinitialize
            >
              {({ errors, touched, values, setFieldValue, isSubmitting }) => (
                <Form>
                  {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map((day) => (
                    <Box key={day} sx={{ mb: 2, py: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                      <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} sm={3}>
                          <FormControl component="fieldset">
                            <Field
                              name={`${day}.isOpen`}
                              type="checkbox"
                              as={({ field }) => (
                                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                  <input
                                    type="checkbox"
                                    {...field}
                                    checked={field.value}
                                    id={`${day}-isOpen`}
                                  />
                                  <InputLabel 
                                    htmlFor={`${day}-isOpen`}
                                    sx={{ ml: 1, fontWeight: 'medium' }}
                                  >
                                    {day.charAt(0).toUpperCase() + day.slice(1)}
                                  </InputLabel>
                                </Box>
                              )}
                            />
                          </FormControl>
                        </Grid>
                        
                        {values[day].isOpen && (
                          <>
                            <Grid item xs={12} sm={4}>
                              <TimePicker
                                label="Opening Time"
                                value={values[day].openTime}
                                onChange={(newValue) => {
                                  setFieldValue(`${day}.openTime`, newValue);
                                }}
                                renderInput={(params) => (
                                  <TextField
                                    {...params}
                                    fullWidth
                                    error={touched[day]?.openTime && Boolean(errors[day]?.openTime)}
                                    helperText={touched[day]?.openTime && errors[day]?.openTime}
                                  />
                                )}
                              />
                            </Grid>
                            
                            <Grid item xs={12} sm={4}>
                              <TimePicker
                                label="Closing Time"
                                value={values[day].closeTime}
                                onChange={(newValue) => {
                                  setFieldValue(`${day}.closeTime`, newValue);
                                }}
                                renderInput={(params) => (
                                  <TextField
                                    {...params}
                                    fullWidth
                                    error={touched[day]?.closeTime && Boolean(errors[day]?.closeTime)}
                                    helperText={touched[day]?.closeTime && errors[day]?.closeTime}
                                  />
                                )}
                              />
                            </Grid>
                          </>
                        )}
                      </Grid>
                    </Box>
                  ))}
                  
                  <Box sx={{ mt: 4 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Custom After-Hours Message (Optional)
                    </Typography>
                    <Field name="customMessage">
                      {({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          multiline
                          rows={4}
                          placeholder="Example: Thank you for calling. Our office is currently closed. Our regular business hours are Monday through Friday, 9 AM to 5 PM. Please leave a message and we'll get back to you during business hours."
                          variant="outlined"
                          error={touched.customMessage && Boolean(errors.customMessage)}
                          helperText={
                            (touched.customMessage && errors.customMessage) || 
                            `${values.customMessage.length}/500 characters`
                          }
                        />
                      )}
                    </Field>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
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
            Business hours updated successfully!
          </Alert>
        </Snackbar>
      </Container>
    </LocalizationProvider>
  );
};

export default BusinessHoursPage;
