import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, CssBaseline, ThemeProvider } from '@mui/material';
import Header from './Header';
import Footer from './Footer';
import theme from '../../styles/theme';

const Layout = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
        }}
      >
        <Header />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Outlet />
        </Box>
        <Footer />
      </Box>
    </ThemeProvider>
  );
};

export default Layout;
