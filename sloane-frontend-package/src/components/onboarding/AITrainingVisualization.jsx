import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  LinearProgress,
  Chip,
  Fade
} from '@mui/material';

const AITrainingVisualization = ({ isTraining, currentPhase = 'preparing', progress = 0, onComplete }) => {
  const [trainingMessages, setTrainingMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [messageIndex, setMessageIndex] = useState(0);
  
  const businessMessages = [
    "Analyzing business hours pattern...",
    "Learning about your services and pricing...",
    "Processing frequently asked questions...",
    "Understanding appointment scheduling preferences...",
    "Learning call handling protocols...",
    "Optimizing response accuracy for your industry...",
    "Creating personalized greeting for your business...",
    "Training voice recognition for industry terminology...",
    "Calibrating AI conversation flow for your business type...",
    "Final optimization for natural conversations..."
  ];
  
  const finalMessages = [
    "Processing complete! Sloane is now trained with your business data.",
    "Sloane has learned how to answer questions about your business.",
    "AI phone service is ready to handle your calls."
  ];

  useEffect(() => {
    if (isTraining) {
      const interval = setInterval(() => {
        if (progress < 100) {
          // During training, cycle through the business messages
          if (messageIndex < businessMessages.length) {
            setCurrentMessage(businessMessages[messageIndex]);
            setMessageIndex(prevIndex => prevIndex + 1);
            
            // Add the message to the history with a slight delay
            setTimeout(() => {
              setTrainingMessages(prev => [...prev, businessMessages[messageIndex]]);
            }, 500);
          }
        } else {
          // Training complete
          setCurrentMessage(finalMessages[0]);
          setTimeout(() => {
            setTrainingMessages(prev => [...prev, ...finalMessages]);
            if (onComplete) onComplete();
          }, 1000);
          clearInterval(interval);
        }
      }, 2000); // Show a new message every 2 seconds
      
      return () => clearInterval(interval);
    }
  }, [isTraining, messageIndex, progress]);

  // Colors for the brain visualization
  const getNodeColor = (index, total, phase) => {
    if (phase === 'preparing') return '#e0e0e0';
    
    const progressPercentage = progress / 100;
    const nodeThreshold = (index / total) * 1.1; // 1.1 multiplier to ensure all nodes get colored eventually
    
    if (progressPercentage >= nodeThreshold) {
      return '#6a3de8'; // Primary color when node is activated
    }
    return '#e0e0e0'; // Default inactive color
  };
  
  // Simple neural network visualization
  const renderNeuralNetwork = () => {
    const nodes = 20; // Number of nodes to display
    const connections = 30; // Number of connections
    
    return (
      <Box sx={{ 
        position: 'relative', 
        height: 200, 
        width: '100%',
        mt: 2, 
        mb: 2 
      }}>
        {/* Neural connections (lines) */}
        {Array.from({ length: connections }).map((_, i) => {
          const startX = Math.random() * 100;
          const startY = Math.random() * 100;
          const endX = Math.random() * 100;
          const endY = Math.random() * 100;
          
          return (
            <Box 
              key={`connection-${i}`}
              sx={{
                position: 'absolute',
                left: `${startX}%`,
                top: `${startY}%`,
                width: `${Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2))}%`,
                height: '1px',
                backgroundColor: progress > (i / connections) * 100 ? '#b39dfa' : '#e0e0e0',
                transform: `rotate(${Math.atan2(endY - startY, endX - startX) * (180 / Math.PI)}deg)`,
                transformOrigin: '0 0',
                transition: 'background-color 0.5s ease',
                opacity: 0.7
              }}
            />
          );
        })}
        
        {/* Nodes (circles) */}
        {Array.from({ length: nodes }).map((_, i) => (
          <Box 
            key={`node-${i}`}
            sx={{
              position: 'absolute',
              left: `${Math.random() * 90}%`,
              top: `${Math.random() * 90}%`,
              width: `${8 + Math.random() * 8}px`,
              height: `${8 + Math.random() * 8}px`,
              borderRadius: '50%',
              backgroundColor: getNodeColor(i, nodes, currentPhase),
              transition: 'background-color 0.5s ease',
              boxShadow: progress > (i / nodes) * 100 ? '0 0 10px #b39dfa' : 'none'
            }}
          />
        ))}
      </Box>
    );
  };

  return (
    <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom align="center">
        Training Sloane AI with Your Business Data
      </Typography>
      
      {renderNeuralNetwork()}
      
      <LinearProgress 
        variant="determinate" 
        value={progress} 
        sx={{ height: 10, borderRadius: 5 }} 
      />
      
      <Box sx={{ mt: 2, mb: 2, minHeight: '2rem', textAlign: 'center' }}>
        <Fade in={!!currentMessage} timeout={800}>
          <Typography variant="body1" color="primary.main" fontWeight="medium">
            {currentMessage}
          </Typography>
        </Fade>
      </Box>
      
      <Box sx={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: 1,
        justifyContent: 'center',
        mt: 3
      }}>
        {trainingMessages.map((message, index) => (
          <Chip 
            key={index} 
            label={message.split('...')[0]} 
            size="small" 
            color="primary" 
            variant="outlined"
            sx={{ 
              animation: 'fadeIn 0.5s ease-in',
              '@keyframes fadeIn': {
                '0%': { opacity: 0 },
                '100%': { opacity: 1 }
              }
            }}
          />
        ))}
      </Box>
      
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          {progress < 100 
            ? `${Math.round(progress)}% complete` 
            : "Training complete! Sloane is ready to answer your calls."}
        </Typography>
      </Box>
    </Paper>
  );
};

export default AITrainingVisualization;
