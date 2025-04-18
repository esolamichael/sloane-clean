import React from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Grid, 
  Paper,
  FormControl,
  FormControlLabel,
  Checkbox,
  FormGroup,
  FormHelperText,
  TextField
} from '@mui/material';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { parse, format } from 'date-fns';

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

const BusinessHoursForm = ({ initialData = {}, onSubmit, onBack }) => {
  const getInitialValues = () => {
    const defaultDay = {
      isOpen: true,
      openTime: defaultOpenTime,
      closeTime: defaultCloseTime
    };

    return {
      monday: initialData.monday || { ...defaultDay },
      tuesday: initialData.tuesday || { ...defaultDay },
      wednesday: initialData.wednesday || { ...defaultDay },
      thursday: initialData.thursday || { ...defaultDay },
      friday: initialData.friday || { ...defaultDay },
      saturday: initialData.saturday || { ...defaultDay, isOpen: false },
      sunday: initialData.sunday || { ...defaultDay, isOpen: false },
      customMessage: initialData.customMessage || ''
    };
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Formik
        initialValues={getInitialValues()}
        validationSchema={BusinessHoursSchema}
        onSubmit={(values) => {
          onSubmit(values);
        }}
      >
        {({ errors, touched, values, setFieldValue }) => (
          <Form>
            <Paper elevation={0} sx={{ p: 3, mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                Set your business hours
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Sloane will use these hours to know when to answer calls and what to tell callers about your availability.
              </Typography>
              
              {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map((day) => (
                <Box key={day} sx={{ mb: 2, py: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={3}>
                      <FormControl component="fieldset">
                        <FormGroup>
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={values[day].isOpen}
                                onChange={(e) => {
                                  setFieldValue(`${day}.isOpen`, e.target.checked);
                                }}
                                name={`${day}.isOpen`}
                              />
                            }
                            label={day.charAt(0).toUpperCase() + day.slice(1)}
                          />
                        </FormGroup>
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
            </Paper>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button
                variant="outlined"
                color="primary"
                onClick={onBack}
                sx={{ py: 1.5, px: 4 }}
              >
                Back
              </Button>
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
    </LocalizationProvider>
  );
};

export default BusinessHoursForm;
