require('dotenv').config(); // Ensure you have dotenv to manage environment variables
const express = require('express');
const ejs = require('ejs');
const path = require('path');
const { updateCurrentUser } = require('./db'); // Import the function from db.js

const app = express();

// Middleware for parsing JSON bodies
app.use(express.json()); // For parsing application/json

// Set the views directory to the 'views' subdirectory
app.set('views', './views/advanced'); // Adjust path if needed
app.set('view engine', 'ejs');
;

// Route to serve the main page
app.get('/', (req, res) => {
  const clientId = process.env.PAYPAL_CLIENT_ID; // Load from environment variables
  const planId = process.env.ADVANCED_PLAN_ID; // Load from environment variables
  res.render('index', { clientId, planId }); // Pass data to the template
});

// Route to handle payment submission
app.post('/submit-payment', async (req, res) => {
  try {
    const { subscriptionId, subscriptionType,  subscriptionStatus } = req.body; // Expecting subscriptionId and subscriptionStatus in the request body

    // Validate subscriptionStatus value if necessary
    if (subscriptionStatus !== 'approved') {
      return res.status(400).send('Invalid subscription status');
    }

    // Update the current user based on the subscription type
    const updateSuccessful = await updateCurrentUser(subscriptionType);

    if (updateSuccessful) {
      res.status(200).json({ message: 'User updated successfully' });
    } else {
      res.status(404).json({ message: 'User not found' });
    }
  } catch (err) {
    console.error('Error handling payment submission:', err);
    res.status(500).json({ message: 'Internal Server Error' });
  }
});

// Error-handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

app.listen(8888, () => console.log('Server listening on port 8888'));
