import React from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Grid, 
  Paper,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider
} from '@mui/material';
import { Formik, Form, Field, FieldArray } from 'formik';
import * as Yup from 'yup';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';

const ServicesSchema = Yup.object().shape({
  services: Yup.array().of(
    Yup.object().shape({
      name: Yup.string().nullable(),
      description: Yup.string().nullable(),
      price: Yup.string().nullable()
    })
  ),
  faqs: Yup.array().of(
    Yup.object().shape({
      question: Yup.string().nullable(),
      answer: Yup.string().nullable()
    })
  )
});

const ServicesForm = ({ initialData = {}, onSubmit, onBack }) => {
  // Direct continuation function that bypasses form validation
  const handleForceContinue = (values) => {
    console.log('Force continuing with services form values:', values);
    
    // Process values to ensure they're valid
    const processedValues = { ...values };
    
    // Filter out empty services
    if (processedValues.services && Array.isArray(processedValues.services)) {
      processedValues.services = processedValues.services.filter(service => 
        service.name.trim() !== '' || service.description.trim() !== '' || service.price.trim() !== '');
    }
    
    // Filter out empty FAQs
    if (processedValues.faqs && Array.isArray(processedValues.faqs)) {
      processedValues.faqs = processedValues.faqs.filter(faq => 
        faq.question.trim() !== '' || faq.answer.trim() !== '');
    }
    
    // Ensure at least one empty service if all were filtered out
    if (!processedValues.services || processedValues.services.length === 0) {
      processedValues.services = [{ name: '', description: '', price: '' }];
    }
    
    // Ensure at least one empty FAQ if all were filtered out
    if (!processedValues.faqs || processedValues.faqs.length === 0) {
      processedValues.faqs = [{ question: '', answer: '' }];
    }
    
    // Call the parent component's onSubmit directly
    onSubmit(processedValues);
  };
  const getInitialValues = () => {
    return {
      services: initialData.services || [
        { name: '', description: '', price: '' }
      ],
      faqs: initialData.faqs || [
        { question: '', answer: '' }
      ]
    };
  };

  return (
    <Formik
      initialValues={getInitialValues()}
      validationSchema={ServicesSchema}
      onSubmit={(values) => {
        onSubmit(values);
      }}
    >
      {({ errors, touched, values }) => (
        <Form noValidate>
          {/* Hidden submit button that can be triggered programmatically if needed */}
          <button type="submit" style={{ display: 'none' }} />
          <Paper elevation={0} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Services & FAQs
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Add the services your business offers and frequently asked questions. This helps Sloane provide accurate information to your callers.
            </Typography>
            
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle1" gutterBottom>
                Services
              </Typography>
              
              <FieldArray name="services">
                {({ push, remove }) => (
                  <>
                    <List>
                      {values.services.map((service, index) => (
                        <Box key={index}>
                          {index > 0 && <Divider sx={{ my: 2 }} />}
                          <ListItem
                            disableGutters
                            sx={{ 
                              display: 'block', 
                              py: 2 
                            }}
                          >
                            <Grid container spacing={2}>
                              <Grid item xs={12} sm={6}>
                                <Field name={`services.${index}.name`}>
                                  {({ field }) => (
                                    <TextField
                                      {...field}
                                      fullWidth
                                      label="Service Name"
                                      variant="outlined"
                                      error={
                                        touched.services?.[index]?.name && 
                                        Boolean(errors.services?.[index]?.name)
                                      }
                                      helperText={
                                        touched.services?.[index]?.name && 
                                        errors.services?.[index]?.name
                                      }
                                    />
                                  )}
                                </Field>
                              </Grid>
                              
                              <Grid item xs={12} sm={6}>
                                <Field name={`services.${index}.price`}>
                                  {({ field }) => (
                                    <TextField
                                      {...field}
                                      fullWidth
                                      label="Price (Optional)"
                                      variant="outlined"
                                      placeholder="e.g. $99, $50-100, or 'Varies'"
                                      error={
                                        touched.services?.[index]?.price && 
                                        Boolean(errors.services?.[index]?.price)
                                      }
                                      helperText={
                                        touched.services?.[index]?.price && 
                                        errors.services?.[index]?.price
                                      }
                                    />
                                  )}
                                </Field>
                              </Grid>
                              
                              <Grid item xs={12}>
                                <Field name={`services.${index}.description`}>
                                  {({ field }) => (
                                    <TextField
                                      {...field}
                                      fullWidth
                                      label="Description"
                                      variant="outlined"
                                      multiline
                                      rows={2}
                                      error={
                                        touched.services?.[index]?.description && 
                                        Boolean(errors.services?.[index]?.description)
                                      }
                                      helperText={
                                        touched.services?.[index]?.description && 
                                        errors.services?.[index]?.description
                                      }
                                    />
                                  )}
                                </Field>
                              </Grid>
                            </Grid>
                            
                            {values.services.length > 1 && (
                              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                                <IconButton 
                                  edge="end" 
                                  aria-label="delete"
                                  onClick={() => remove(index)}
                                  color="error"
                                  size="small"
                                >
                                  <DeleteIcon />
                                </IconButton>
                              </Box>
                            )}
                          </ListItem>
                        </Box>
                      ))}
                    </List>
                    
                    <Button
                      startIcon={<AddIcon />}
                      onClick={() => push({ name: '', description: '', price: '' })}
                      sx={{ mt: 2 }}
                    >
                      Add Service
                    </Button>
                  </>
                )}
              </FieldArray>
            </Box>
            
            <Box sx={{ mt: 5 }}>
              <Typography variant="subtitle1" gutterBottom>
                Frequently Asked Questions
              </Typography>
              
              <FieldArray name="faqs">
                {({ push, remove }) => (
                  <>
                    <List>
                      {values.faqs.map((faq, index) => (
                        <Box key={index}>
                          {index > 0 && <Divider sx={{ my: 2 }} />}
                          <ListItem
                            disableGutters
                            sx={{ 
                              display: 'block', 
                              py: 2 
                            }}
                          >
                            <Grid container spacing={2}>
                              <Grid item xs={12}>
                                <Field name={`faqs.${index}.question`}>
                                  {({ field }) => (
                                    <TextField
                                      {...field}
                                      fullWidth
                                      label="Question"
                                      variant="outlined"
                                      error={
                                        touched.faqs?.[index]?.question && 
                                        Boolean(errors.faqs?.[index]?.question)
                                      }
                                      helperText={
                                        touched.faqs?.[index]?.question && 
                                        errors.faqs?.[index]?.question
                                      }
                                    />
                                  )}
                                </Field>
                              </Grid>
                              
                              <Grid item xs={12}>
                                <Field name={`faqs.${index}.answer`}>
                                  {({ field }) => (
                                    <TextField
                                      {...field}
                                      fullWidth
                                      label="Answer"
                                      variant="outlined"
                                      multiline
                                      rows={3}
                                      error={
                                        touched.faqs?.[index]?.answer && 
                                        Boolean(errors.faqs?.[index]?.answer)
                                      }
                                      helperText={
                                        touched.faqs?.[index]?.answer && 
                                        errors.faqs?.[index]?.answer
                                      }
                                    />
                                  )}
                                </Field>
                              </Grid>
                            </Grid>
                            
                            {values.faqs.length > 1 && (
                              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                                <IconButton 
                                  edge="end" 
                                  aria-label="delete"
                                  onClick={() => remove(index)}
                                  color="error"
                                  size="small"
                                >
                                  <DeleteIcon />
                                </IconButton>
                              </Box>
                            )}
                          </ListItem>
                        </Box>
                      ))}
                    </List>
                    
                    <Button
                      startIcon={<AddIcon />}
                      onClick={() => push({ question: '', answer: '' })}
                      sx={{ mt: 2 }}
                    >
                      Add FAQ
                    </Button>
                  </>
                )}
              </FieldArray>
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
              // Remove type="submit" to prevent form validation
              variant="contained"
              color="primary"
              size="large"
              sx={{ py: 1.5, px: 4 }}
              onClick={() => {
                console.log('Continue button clicked directly');
                // Skip form validation entirely and just continue
                handleForceContinue(values);
              }}
            >
              Continue
            </Button>
          </Box>
        </Form>
      )}
    </Formik>
  );
};

export default ServicesForm;
