import { createTheme } from '@mui/material/styles';

// Professional color palette for Sloane
const colors = {
  primary: {
    main: '#6a3de8', // Purple - similar to heyrosie but unique for Sloane
    light: '#9c6eff',
    dark: '#4b2aa6',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#34c3ff', // Bright blue for accents
    light: '#7df6ff',
    dark: '#0092cc',
    contrastText: '#ffffff',
  },
  background: {
    default: '#f8f9fc',
    paper: '#ffffff',
    light: '#f0f2f8',
    dark: '#2c2c3c',
  },
  text: {
    primary: '#2c2c3c',
    secondary: '#6b7280',
    disabled: '#9ca3af',
  },
  success: {
    main: '#10b981',
    light: '#5eead4',
    dark: '#047857',
  },
  error: {
    main: '#ef4444',
    light: '#fca5a5',
    dark: '#b91c1c',
  },
  warning: {
    main: '#f59e0b',
    light: '#fcd34d',
    dark: '#b45309',
  },
  info: {
    main: '#3b82f6',
    light: '#93c5fd',
    dark: '#1d4ed8',
  },
};

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: colors.primary,
    secondary: colors.secondary,
    background: colors.background,
    text: colors.text,
    success: colors.success,
    error: colors.error,
    warning: colors.warning,
    info: colors.info,
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      lineHeight: 1.2,
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
      lineHeight: 1.2,
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.3,
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.4,
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.1rem',
      lineHeight: 1.4,
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      lineHeight: 1.4,
    },
    subtitle1: {
      fontSize: '1rem',
      lineHeight: 1.5,
      fontWeight: 500,
    },
    subtitle2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
      fontWeight: 500,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 8,
  },
  shadows: [
    'none',
    '0px 2px 4px rgba(0, 0, 0, 0.05)',
    '0px 4px 6px rgba(0, 0, 0, 0.05)',
    '0px 6px 8px rgba(0, 0, 0, 0.05)',
    '0px 8px 12px rgba(0, 0, 0, 0.05)',
    '0px 12px 16px rgba(0, 0, 0, 0.05)',
    '0px 14px 20px rgba(0, 0, 0, 0.05)',
    '0px 16px 24px rgba(0, 0, 0, 0.05)',
    '0px 18px 28px rgba(0, 0, 0, 0.05)',
    '0px 20px 32px rgba(0, 0, 0, 0.05)',
    '0px 22px 36px rgba(0, 0, 0, 0.05)',
    '0px 24px 38px rgba(0, 0, 0, 0.05)',
    '0px 26px 40px rgba(0, 0, 0, 0.05)',
    '0px 28px 42px rgba(0, 0, 0, 0.05)',
    '0px 30px 44px rgba(0, 0, 0, 0.05)',
    '0px 32px 46px rgba(0, 0, 0, 0.05)',
    '0px 34px 48px rgba(0, 0, 0, 0.05)',
    '0px 36px 50px rgba(0, 0, 0, 0.05)',
    '0px 38px 52px rgba(0, 0, 0, 0.05)',
    '0px 40px 54px rgba(0, 0, 0, 0.05)',
    '0px 42px 56px rgba(0, 0, 0, 0.05)',
    '0px 44px 58px rgba(0, 0, 0, 0.05)',
    '0px 46px 60px rgba(0, 0, 0, 0.05)',
    '0px 48px 62px rgba(0, 0, 0, 0.05)',
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 24px',
          fontWeight: 600,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.1)',
          },
        },
        containedPrimary: {
          background: `linear-gradient(90deg, ${colors.primary.main} 0%, ${colors.primary.dark} 100%)`,
          '&:hover': {
            background: `linear-gradient(90deg, ${colors.primary.main} 20%, ${colors.primary.dark} 100%)`,
          },
        },
        containedSecondary: {
          background: `linear-gradient(90deg, ${colors.secondary.main} 0%, ${colors.secondary.dark} 100%)`,
          '&:hover': {
            background: `linear-gradient(90deg, ${colors.secondary.main} 20%, ${colors.secondary.dark} 100%)`,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 12,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0px 2px 10px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
  },
});

export default theme;
