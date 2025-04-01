const express = require('express');
const axios = require('axios');
const app = express();
const cors = require('cors'); 
app.use(cors());

app.use(express.json());



const NODE_ENV =  'development'; //process.env.NODE_ENV ||


// start of Cat A
const CAT_A_SERVICE_URL =
  //NODE_ENV === 'production'
    //? process.env.CAT_A_SERVICE_URL:  // place render url here 
     'http://localhost:5000'; 

app.post('/categorisation', async (req, res) => {
    console.log("Received request at /categorisation:", req.body);
    try {
        // posts frontend request to the cat a service 
        console.log("Gateway initiated")
        const response = await axios.post(`${CAT_A_SERVICE_URL}/post_video`, req.body);
        
        res.json(response.data);
    } catch (error) {
        console.error('Error forwarding request to CatA service:', error.message);
        res.status(500).json({ error: 'Error processing video categorisation' });
    }
    });

// end of Cat A


// Start of Categories retrieval
const CAT_RETRIEVAL_URL = 'https://personal-e5asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories'; 
app.post('/RetrieveAllAlbums', async (req, res) => {
    console.log("Received request at RetrieveAllAlbum:", req.body);
    const { email, categories } = req.body;
    try {
        // posts frontend request to the cat a service 
        console.log("Gateway initiated")
        
        const response = await axios.post(`${CAT_RETRIEVAL_URL}/RetrievePersonal`, {
            email,
            categories
          }, {
            headers: {
              'Content-Type': 'application/json'
            }
          });
        
        res.json(response.data);
    } catch (error) {
        console.error('Error forwarding request to Categories Retrieval service:', error.message);
        res.status(500).json({ error: 'Error processing saved categories retrieval' });
    }
    });

// End of Categories Retrieval 

//Start of Shared Album

const SHARED_ALBUM_URL =
  //NODE_ENV === 'production'
    //? process.env.CAT_A_SERVICE_URL:  // place render url here 
     'http://localhost:5100'; 

app.post('/saveSharedAlbum', async (req, res) => {
    console.log("Received request at Save Shared Album", req.body);
    try {
        // posts frontend request to the cat a service 
        console.log("Gateway initiated")
        const response = await axios.post(`${SHARED_ALBUM_URL}/shared-album/add`, req.body);
        
        res.json(response.data);
    } catch (error) {
        console.error('Error forwarding request to Saved Shared Album service:', error.message);
        res.status(500).json({ error: 'Error saving to shared album' });
    }
    });


//End of Shared album 


// Start of GetPastWeek
const CAT_GETPASTWEEK_URL = 'https://personal-e5asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories'; 
app.post('/GetPastWeek', async (req, res) => {
    console.log("Received request at GetPastWeek:", req.body);
    const {email, category} = req.body;
    try {
        // posts frontend request to the cat a service 
        console.log("Gateway initiated")
        
        const response = await axios.post(`${CAT_GETPASTWEEK_URL}/GetPastWeek`, {email, category}, {
            headers: {
              'Content-Type': 'application/json'
            }
          });
        
        res.json(response.data);
    } catch (error) {
        console.error('Error forwarding request to GetPastWeek service:', error.message);
        res.status(500).json({ error: 'Error processing GetPastWeek retrieval' });
    }
    });
// End of GetPastWeek






const PORT = process.env.PORT || 3000;
app.listen(PORT,'0.0.0.0', () => {
    console.log(`API Gateway running on port ${PORT} in ${NODE_ENV} mode.`);
});
      