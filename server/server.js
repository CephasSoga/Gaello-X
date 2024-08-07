require('dotenv').config(); // Ensure you have dotenv to manage environment variables
const express = require('express');
const ejs = require('ejs');

const app = express();

// Set the views directory to the 'views' subdirectory
app.set('views', './views/standard'); // Adjust path if needed
app.set('view engine', 'ejs');

// Route handlers
app.get('/', (req, res) => {
  const clientId = process.env.PAYPAL_CLIENT_ID; // Load from environment variables
  const planId = process.env.STANDARD_PLAN_ID; // Load from environment variables
  res.render('index', { clientId, planId }); // Pass data to the template
});

// Error-handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

app.listen(8888, () => console.log('Server listening on port 8888'));
