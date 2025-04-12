import React from 'react';
import { Box, Typography, Container, Grid, Card, CardContent, useTheme } from '@mui/material';
import PhoneInTalkIcon from '@mui/icons-material/PhoneInTalk';
import EventNoteIcon from '@mui/icons-material/EventNote';
import SpeedIcon from '@mui/icons-material/Speed';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import SmartphoneIcon from '@mui/icons-material/Smartphone';
import SavingsIcon from '@mui/icons-material/Savings';

const FeaturesSection = () => {
  const theme = useTheme();
  
  const features = [
    {
      icon: <PhoneInTalkIcon fontSize="large" color="primary" />,
      title: 'Never miss another call or opportunity',
      description: 'Sloane is there anytime you\'re not available. You\'ll never miss another opportunity just because you can\'t answer the phone.'
    },
    {
      icon: <EventNoteIcon fontSize="large" color="primary" />,
      title: 'Automatic appointment scheduling',
      description: 'Sloane can schedule appointments directly on your calendar, saving you time and ensuring you never double-book.'
    },
    {
      icon: <SpeedIcon fontSize="large" color="primary" />,
      title: 'Amazing human-like AI',
      description: 'You\'ll outshine your competition with the most modern AI voice technology that sounds natural and professional.'
    },
    {
      icon: <AccessTimeIcon fontSize="large" color="primary" />,
      title: 'Available 24/7',
      description: 'Sloane works around the clock, answering calls even outside business hours so you never miss an opportunity.'
    },
    {
      icon: <SmartphoneIcon fontSize="large" color="primary" />,
      title: 'Instant notifications',
      description: 'Get notified right away via email and/or text every time a new call comes in, so you can quickly decide how to handle it.'
    },
    {
      icon: <SavingsIcon fontSize="large" color="primary" />,
      title: '10x cheaper than an answering service',
      description: 'There\'s no need to spend a bunch of money on an outsourced answering service. Sloane can do it for a fraction of the cost.'
    }
  ];

  return (
    <Box
      sx={{
        py: { xs: 8, md: 12 },
        backgroundColor: theme.palette.background.default,
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography
            variant="h2"
            component="h2"
            color="text.primary"
            sx={{ mb: 2 }}
          >
            Why Sloane is right for your small business
          </Typography>
          <Typography
            variant="h5"
            component="p"
            color="text.secondary"
            sx={{ maxWidth: 700, mx: 'auto' }}
          >
            The power of the latest AI tech, working for you 24/7.
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.3s, box-shadow 0.3s',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: theme.shadows[10],
                  },
                  borderRadius: 3,
                }}
                elevation={2}
              >
                <CardContent sx={{ flexGrow: 1, p: 4 }}>
                  <Box sx={{ mb: 2 }}>{feature.icon}</Box>
                  <Typography variant="h5" component="h3" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default FeaturesSection;
