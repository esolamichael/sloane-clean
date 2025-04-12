import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  Container, 
  Grid, 
  Link, 
  InputAdornment, 
  IconButton,
  Alert,
  CircularProgress
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { enhancedApiCall } from '../../utils/ErrorHandling';

const LoginSchema = Yup.object().shape({
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  password: Yup.string()
    .required('Password is required')
});

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      setError('');
      await login(values.email, values.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Failed to login. Please check your credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Box sx={{ mb: 4, textAlign: 'center' }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Welcome back
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Sign in to your Sloane account
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Formik
            initialValues={{ email: '', password: '' }}
            validationSchema={LoginSchema}
            onSubmit={handleSubmit}
          >
            {({ errors, touched, isSubmitting }) => (
              <Form>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Field name="email">
                      {({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Email Address"
                          variant="outlined"
                          error={touched.email && Boolean(errors.email)}
                          helperText={touched.email && errors.email}
                        />
                      )}
                    </Field>
                  </Grid>
                  <Grid item xs={12}>
                    <Field name="password">
                      {({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Password"
                          type={showPassword ? 'text' : 'password'}
                          variant="outlined"
                          error={touched.password && Boolean(errors.password)}
                          helperText={touched.password && errors.password}
                          InputProps={{
                            endAdornment: (
                              <InputAdornment position="end">
                                <IconButton
                                  onClick={() => setShowPassword(!showPassword)}
                                  edge="end"
                                >
                                  {showPassword ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                              </InputAdornment>
                            )
                          }}
                        />
                      )}
                    </Field>
                  </Grid>
                  <Grid item xs={12}>
                    <Button
                      type="submit"
                      fullWidth
                      variant="contained"
                      color="primary"
                      size="large"
                      disabled={isSubmitting}
                      sx={{ py: 1.5 }}
                    >
                      {isSubmitting ? (
                         <LoadingSpinner message="Signing in..." />
                      ) : (
                        'Sign In'
                      )}
                    </Button>
                  </Grid>
                </Grid>
              </Form>
            )}
          </Formik>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Link
              component={RouterLink}
              to="/forgot-password"
              variant="body2"
              color="primary"
              underline="hover"
            >
              Forgot password?
            </Link>
          </Box>

          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Don't have an account?{' '}
              <Link
                component={RouterLink}
                to="/signup"
                variant="body2"
                color="primary"
                underline="hover"
              >
                Sign up
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;
