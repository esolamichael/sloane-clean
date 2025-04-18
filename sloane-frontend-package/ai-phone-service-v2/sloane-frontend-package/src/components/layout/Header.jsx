import React from 'react';
import { AppBar, Toolbar, Button, Box, Typography, Container, useMediaQuery, IconButton, Menu, MenuItem, useTheme } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import { useAuth } from '../../contexts/AuthContext';

const Header = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { currentUser, logout } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState(null);
  
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleLogout = async () => {
    try {
      await logout();
      handleMenuClose();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <AppBar position="static" color="default" elevation={0} sx={{ backgroundColor: 'white' }}>
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          {/* Logo */}
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              mr: 2,
              fontWeight: 700,
              color: 'primary.main',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            Sloane
          </Typography>

          <Box sx={{ flexGrow: 1 }} />

          {isMobile ? (
            <>
              <IconButton
                edge="end"
                color="primary"
                aria-label="menu"
                onClick={handleMenuOpen}
              >
                <MenuIcon />
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                keepMounted
              >
                <MenuItem component={RouterLink} to="/resources" onClick={handleMenuClose}>
                  Resources
                </MenuItem>
                <MenuItem component={RouterLink} to="/pricing" onClick={handleMenuClose}>
                  Pricing
                </MenuItem>
                {currentUser ? (
                  <>
                    <MenuItem component={RouterLink} to="/dashboard" onClick={handleMenuClose}>
                      Dashboard
                    </MenuItem>
                    <MenuItem onClick={handleLogout}>Logout</MenuItem>
                  </>
                ) : (
                  <>
                    <MenuItem component={RouterLink} to="/login" onClick={handleMenuClose}>
                      Login
                    </MenuItem>
                    <MenuItem component={RouterLink} to="/signup" onClick={handleMenuClose}>
                      Sign Up
                    </MenuItem>
                  </>
                )}
              </Menu>
            </>
          ) : (
            <>
              <Button
                component={RouterLink}
                to="/resources"
                color="inherit"
                sx={{ mx: 1 }}
              >
                Resources
              </Button>
              <Button
                component={RouterLink}
                to="/pricing"
                color="inherit"
                sx={{ mx: 1 }}
              >
                Pricing
              </Button>
              
              {currentUser ? (
                <>
                  <Button
                    component={RouterLink}
                    to="/dashboard"
                    color="inherit"
                    sx={{ mx: 1 }}
                  >
                    Dashboard
                  </Button>
                  <Button
                    color="primary"
                    variant="outlined"
                    onClick={logout}
                    sx={{ ml: 2 }}
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    component={RouterLink}
                    to="/login"
                    color="inherit"
                    sx={{ mx: 1 }}
                  >
                    Login
                  </Button>
                  <Button
                    component={RouterLink}
                    to="/signup"
                    color="primary"
                    variant="contained"
                    sx={{ ml: 2 }}
                  >
                    Get Started for Free
                  </Button>
                </>
              )}
            </>
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
