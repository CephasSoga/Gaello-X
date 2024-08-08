// db.js
require('dotenv').config();
const path = require('path');
const { MongoClient } = require('mongodb');
const { readEmailFromJsonFile } = require('./fileHandler.js');

// Get the application base path from environment variables
const appPath = process.env.APP_BASE_PATH;

// Path to your JSON file
const filePath = path.join(appPath, 'credentials', 'credentials.json');

const mongoUrl = process.env.MONGODB_URI;
const dbName = 'UsersAuth';

let dbClient;

const subscriptionLevels = {
    free: 1,
    standard: 2,
    advanced: 3,
};

/**
 * Creates an index on a MongoDB collection.
 *
 * @param {string} collectionName - The name of the collection to create the index on.
 * @param {object} index - The index specification.
 * @return {Promise<void>} - A promise that resolves when the index is created.
 * @throws {Error} - If there is an error creating the index.
 */
const createIndex = async (collectionName, index) => {
    try {
        const collection = await getCollection(collectionName);
        await collection.createIndex(index);
        console.log(`Index created on ${collectionName} for ${JSON.stringify(index)}`);
    } catch (err) {
        console.error(`Failed to create index on ${collectionName}:`, err);
        throw err;
    }
};

/**
 * Connects to the MongoDB database and returns the database client. If the client is already connected,
 * it returns the existing client. If the index on the 'users' collection does not exist, it creates the index.
 *
 * @return {Promise<MongoClient>} The database client.
 * @throws {Error} If there is an error connecting to the database or creating the index.
 */
async function connect() {
    if (dbClient) return dbClient;
    try {
        const client = await MongoClient.connect(mongoUrl, { useUnifiedTopology: true });
        dbClient = client.db(dbName);
        console.log('Connected to the database');
        // Call this function after database connection is established
        // Check if the index already exists before creating it
        const indexes = await dbClient.collection('users').indexes();
        const indexExists = indexes.some(index => index.name === 'email_1');

        if (!indexExists) {
            await createIndex('users', { email: 1 });
            console.log('Index created');
        } else {
            console.log('Index already exists');
        }
        return dbClient;
    } catch (err) {
        console.error('Failed to connect to the database:', err);
        throw err;
    }
}

/**
 * Retrieves a MongoDB collection by its name.
 *
 * @param {string} collectionName - The name of the collection to retrieve.
 * @return {Promise<Collection>} A Promise that resolves to the MongoDB collection.
 * @throws {Error} If there is an error connecting to the database or retrieving the collection.
 */
async function getCollection(collectionName) {
    try {
        const db = await connect();
        return db.collection(collectionName);
    } catch (err) {
        console.error('Failed to get collection:', err);
        throw err;
    }
}

/**
 * Updates a user's subscription details in the specified collection.
 *
 * @param {string} userEmail - The email of the user to update.
 * @param {string} collection - The name of the collection to update.
 * @param {string} subscription - The new subscription level.
 * @return {Promise<boolean>} A Promise that resolves to true if the update was successful, false otherwise.
 * @throws {Error} If there was an error updating the user.
 */
async function updateUser(userEmail, collection, subscription) {
    try {
        const authorizationLevel = subscriptionLevels[subscription] || 0;
        const subscriptionField = {
            authorizationLevel: authorizationLevel,
            subscription: subscription,
            status: 'ACTIVE',
        };

        const result = await getCollection(collection).updateOne({ email: userEmail }, { $set: subscriptionField });

        if (result.matchedCount === 0) {
            console.log('No matching user found');
            return false; // User not found
        }

        return result.modifiedCount > 0; // Return true if update successful
    } catch (err) {
        console.error('Failed to update user:', err);
        throw err;
    }
}

/**
 * Updates the current user's subscription based on the provided subscription level.
 *
 * @param {string} subscription - The new subscription level to update.
 */
async function updateCurrentUser(subscription) {
    try {
        const credentials = await readEmailFromJsonFile(filePath);
        if (!credentials) return; // Handle missing credentials gracefully
    
        const userEmail = credentials.email;
        const collection = 'users';
        await updateUser(userEmail, collection, subscription);
      } catch (err) {
        console.error('Error updating current user:', err);
        // Consider logging the error or notifying the user
      }
    }

module.exports = { updateCurrentUser };
