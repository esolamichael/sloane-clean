import React from 'react';
import { Box, Typography, Container, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 6,
        px: 2,
        mt: 'auto',
        backgroundColor: (theme) => theme.palette.background.light,
      }}
    >
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'center', md: 'flex-start' },
            textAlign: { xs: 'center', md: 'left' },
          }}
        >
          <Box sx={{ mb: { xs: 4, md: 0 } }}>
            <Typography
              variant="h6"
              component={RouterLink}
              to="/"
              sx={{
                fontWeight: 700,
                color: 'primary.main',
                textDecoration: 'none',
                display: 'block',
                mb: 2,
              }}
            >
              Sloane
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 300 }}>
              AI phone answering service for small businesses. 10x better than voicemail. 10x cheaper than an answering service.
            </Typography>
          </Box>

          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              gap: { xs: 4, sm: 8 },
            }}
          >
            <Box>
              <Typography variant="subtitle1" color="text.primary" gutterBottom>
                Product
              </Typography>
              <Link component={RouterLink} to="/pricing" color="text.secondary" sx={{ display: 'block', mb: 1, textDecoration: 'none' }}>
                Pricing
              </Link>
              <Link component={RouterLink} to="/features" color="text.secondary" sx={{ display: 'block', mb: 1, textDecoration: 'none' }}>
                Features
              </Link>
              <Link component={RouterLink} to="/resources" color="text.secondary" sx={{ display: 'block', mb: 1, textDecoration: 'none' }}>
                Resources
              </Link>
            </Box>

            <Box>
              <Typography variant="subtitle1" color="text.primary" gutterBottom>
                Company
              </Typography>
              <Link component={RouterLink} to="/about" color="text.secondary" sx={{ display: 'block', mb: 1, textDecoration: 'none' }}>
                About
              </Link>
              <Link component={RouterLink} to="/contact" color="text.secondary" sx={{ display: 'block', mb: 1, textDecoration: 'none' }}>
                Contact
              </Link>
              <Link component={RouterLink} to="/blog" color="text.secondary" sx={{ display: 'block', mb: 1, textDecoration: 'none' }}>
                Blog
              </Link>
            </Box>

            <Box>
              <Typography variant="subtitle1" color="text.primary" gutterBottom>
                Legal
              </Typography>
              <Link component={RouterLink} to="/privacy" color="text.secondary" sx={{ display: 'block', mb: 1, textDecoration: 'none' }}>
                Privacy
              </Link>
              <Link component={RouterLink} to="/terms" color="text.secondary" sx={{ display: 'block', mb: 1, textDecoration: 'none' }}>
                Terms
              </Link>
            </Box>
          </Box>
        </Box>

        <Box
          sx={{
            mt: 6,
            textAlign: 'center',
            borderTop: '1px solid',
            borderColor: 'divider',
            pt: 3,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} Sloane AI Phone Service. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
