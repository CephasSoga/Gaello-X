const fs = require('fs');
const path = require('path');

// Get the application base path from environment variables
const appPath = process.env.APP_BASE_PATH;

// Path to your JSON file
const filePath = path.join(appPath, 'credentials', 'credentials.json');

// Function to read JSON file and extract `email` field
async function readEmailFromJsonFile(filePath) {
    try {
        // Read the file synchronously
        const fileContent = await fs.readFile(filePath, 'utf-8');
        
        // Parse the JSON content
        const data = JSON.parse(fileContent);
        
        // Extract email field and validate its presence
        const email = data.email;
        if (email) {
            return {email: email}; // Return the email;
        } else {
            console.error('Email field not found in JSON file');
            return null;
        }
    } catch (err) {
        console.error('Error reading or parsing the JSON file:', err);
        return null;
    }
}

module.exports = {
    readEmailFromJsonFile
};
