import React from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Grid, 
  Paper,
  FormControl,
  FormHelperText,
  Alert,
  CircularProgress
} from '@mui/material';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { isAfter } from 'date-fns';

// Enhanced validation schema with time range validation
const BusinessHoursValidationSchema = Yup.object().shape({
  monday: Yup.object().shape({
    isOpen: Yup.boolean(),
    openTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Opening time is required')
    }),
    closeTime: Yup.mixed().when(['isOpen', 'openTime'], {
      is: (isOpen, openTime) => isOpen && openTime,
      then: Yup.mixed()
        .required('Closing time is required')
        .test('is-after-open', 'Closing time must be after opening time', function(closeTime) {
          const { openTime } = this.parent;
          if (!openTime || !closeTime) return true;
          return isAfter(closeTime, openTime);
        })
    })
  }),
  // Repeat for other days of the week...
  tuesday: Yup.object().shape({
    isOpen: Yup.boolean(),
    openTime: Yup.mixed().when('isOpen', {
      is: true,
      then: Yup.mixed().required('Opening time is required')
    }),
    closeTime: Yup.mixed().when(['isOpen', 'openTime'], {
      is: (isOpen, openTime) => isOpen && openTime,
      then: Yup.mixed()
        .required('Closing time is required')
        .test('is-after-open', 'Closing time must be after opening time', function(closeTime) {
          const { openTime } = this.parent;
          if (!openTime || !closeTime) return true;
          return isAfter(closeTime, openTime);
        })
    })
  }),
  // ... and so on for other days
});

// Example usage in a component
const EnhancedBusinessHoursForm = ({ initialData, onSubmit, onBack }) => {
  return (
    <Formik
      initialValues={initialData}
      validationSchema={BusinessHoursValidationSchema}
      onSubmit={onSubmit}
    >
      {({ errors, touched, values, setFieldValue, isSubmitting }) => (
        <Form>
          {/* Form fields here */}
          {/* When rendering time pickers, use the enhanced validation */}
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TimePicker
                label="Opening Time"
                value={values.monday.openTime}
                onChange={(newValue) => {
                  setFieldValue('monday.openTime', newValue);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    fullWidth
                    error={touched.monday?.openTime && Boolean(errors.monday?.openTime)}
                    helperText={touched.monday?.openTime && errors.monday?.openTime}
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <TimePicker
                label="Closing Time"
                value={values.monday.closeTime}
                onChange={(newValue) => {
                  setFieldValue('monday.closeTime', newValue);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    fullWidth
                    error={touched.monday?.closeTime && Boolean(errors.monday?.closeTime)}
                    helperText={touched.monday?.closeTime && errors.monday?.closeTime}
                  />
                )}
              />
            </Grid>
          </Grid>
          
          {/* Submit button */}
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </Form>
      )}
    </Formik>
  );
};

export default EnhancedBusinessHoursForm;
