import React from 'react';
import { Box, Typography, Button, Container, useTheme } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const CallToActionSection = () => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        py: { xs: 8, md: 10 },
        backgroundColor: theme.palette.primary.main,
        color: 'white',
      }}
    >
      <Container maxWidth="lg">
        <Box
          sx={{
            textAlign: 'center',
            maxWidth: 800,
            mx: 'auto',
          }}
        >
          <Typography
            variant="h2"
            component="h2"
            sx={{ mb: 3, color: 'white' }}
          >
            Never miss an opportunity because you can't answer the phone.
          </Typography>
          
          <Typography
            variant="h5"
            component="p"
            sx={{ mb: 5, opacity: 0.9 }}
          >
            Powerful, yet super easy to set up and get started in minutes.
          </Typography>
          
          <Button
            component={RouterLink}
            to="/onboarding"
            variant="contained"
            color="secondary"
            size="large"
            sx={{ 
              py: 1.5, 
              px: 4,
              fontSize: '1.1rem',
              boxShadow: theme.shadows[4],
            }}
          >
            Get Started for Free
          </Button>
          
          <Typography
            variant="body1"
            sx={{ mt: 2, opacity: 0.8 }}
          >
            First 25 minutes completely free. No credit card required.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default CallToActionSection;
