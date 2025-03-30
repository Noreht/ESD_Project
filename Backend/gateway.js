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


// Start of Cat B



// End of Cat B












const PORT = process.env.PORT || 3000;
app.listen(PORT,'0.0.0.0', () => {
    console.log(`API Gateway running on port ${PORT} in ${NODE_ENV} mode.`);
});
      