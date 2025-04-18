# Sloane Frontend Bug Tracking

This document tracks bugs found during testing of the Sloane AI Phone Answering Service frontend.

## Open Issues

### SLOANE-01
- **Component**: AuthContext
- **Description**: The token refresh mechanism needs to be implemented to handle expired JWT tokens
- **Steps to Reproduce**: 
  1. Login to the application
  2. Wait for the token to expire (typically after 1 hour)
  3. Try to access a protected route
- **Expected Behavior**: The system should automatically refresh the token if it's expired but the refresh token is still valid
- **Actual Behavior**: User is redirected to login page when token expires
- **Priority**: High
- **Status**: Open

### SLOANE-02
- **Component**: BusinessHoursForm
- **Description**: Time picker validation needs improvement for business hours
- **Steps to Reproduce**:
  1. Go to Business Hours page
  2. Set closing time earlier than opening time
  3. Submit the form
- **Expected Behavior**: Form should validate that closing time is after opening time
- **Actual Behavior**: Form allows submission with invalid time ranges
- **Priority**: Medium
- **Status**: Open

### SLOANE-03
- **Component**: API Integration
- **Description**: Error handling needs improvement for network failures
- **Steps to Reproduce**:
  1. Disconnect from the internet
  2. Try to fetch data or submit a form
- **Expected Behavior**: User-friendly error message explaining the network issue
- **Actual Behavior**: Generic error message or no feedback
- **Priority**: Medium
- **Status**: Open

## Fixed Issues

None yet - testing in progress.
