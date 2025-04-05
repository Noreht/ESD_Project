const express = require("express");
const axios = require("axios");
const app = express();
const cors = require("cors");
app.use(cors());

app.use(express.json());
require("dotenv").config();

const NODE_ENV = "development"; //process.env.NODE_ENV ||

// start of Cat A
const CAT_A_SERVICE_URL =
  //NODE_ENV === 'production'
  //? process.env.CAT_A_SERVICE_URL:  // place render url here
  "http://catA:5001";

// app.post('/categorisation', async (req, res) => {
//     console.log("Received request at /categorisation:", req.body);
//     try {
//         // posts frontend request to the cat a service
//         console.log("Gateway initiated")
//         const response = await axios.post(`${CAT_A_SERVICE_URL}/post_video`, req.body);

//         res.json(response.data);
//     } catch (error) {
//         console.error('Error forwarding request to CatA service:', error.message);
//         res.status(500).json({ error: 'Error processing video categorisation' });
//     }
//     });
app.post("/categorisation", async (req, res) => {
  console.log("Received request at /categorisation:", req.body);
  try {
    console.log("Gateway initiated");
    const response = await axios.post(
      `${CAT_A_SERVICE_URL}/post_video`,
      req.body,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer fake-token", // <-- just needs to exist because CORS allows it
        },
      }
    );

    res.json(response.data);
  } catch (error) {
    console.error("Error forwarding request to CatA service:", error.message);
    res.status(500).json({ error: "Error processing video categorisation" });
  }
});

// end of Cat A

// Start of Categories retrieval
const CAT_RETRIEVAL_URL =
  "https://personal-e5asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories";
app.post("/RetrieveAllAlbums", async (req, res) => {
  console.log("Received request at RetrieveAllAlbum:", req.body);
  const { email, categories } = req.body;
  try {
    // posts frontend request to the cat a service
    console.log("Gateway initiated");

    const response = await axios.post(
      `${CAT_RETRIEVAL_URL}/RetrievePersonal`,
      {
        email,
        categories,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    res.json(response.data);
    console.log(response.data);
  } catch (error) {
    console.error(
      "Error forwarding request to Categories Retrieval service:",
      error.message
    );
    res
      .status(500)
      .json({ error: "Error processing saved categories retrieval" });
  }
});

// End of Categories Retrieval

//Start of Shared Album

const SHARED_ALBUM_URL =
  //NODE_ENV === 'production'
  //? process.env.CAT_A_SERVICE_URL:  // place render url here
  "http://sharedalbum:5100";

app.post("/saveSharedAlbum", async (req, res) => {
  console.log("Received request at Saved Shared Album Button", req.body);
  try {
    // posts frontend request to the cat a service
    console.log("Gateway initiated");

    const response = await axios.post(
      `${SHARED_ALBUM_URL}/shared-album/add`,
      req.body,
      {
        headers: {
          "Content-Type": "application/json", // 👈 Required for Flask
        },
      }
    );

    res.json(response.data);
  } catch (error) {
    console.error(
      "Error forwarding request to Saved Shared Album service:",
      error.message
    );
    res.status(500).json({ error: "Error saving to shared album" });
  }
});

//End of Shared album

// Start of GetPastWeek
const CAT_GETPASTWEEK_URL =
  "https://personal-e5asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories";
app.post("/GetPastWeek", async (req, res) => {
  console.log("Received request at GetPastWeek:", req.body);
  const { email, category } = req.body;
  try {
    // posts frontend request to the cat a service
    console.log("Gateway initiated");

    const response = await axios.post(
      `${CAT_GETPASTWEEK_URL}/GetPastWeek`,
      { email, category },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    res.json(response.data);
  } catch (error) {
    console.error(
      "Error forwarding request to GetPastWeek service:",
      error.message
    );
    res.status(500).json({ error: "Error processing GetPastWeek retrieval" });
  }
});
// End of GetPastWeek

//start of Find Top 5
const FIND_TOP_5_URL = "http://findtop5:5300";

app.get("/LoadDashboard", async (req, res) => {
  const email = req.query.email;

  console.log("Received request at LoadDashboard", req.query);

  if (!email) {
    return res.status(400).json({ error: "User email missing" });
  }
  try {
    // posts frontend request to the cat a service
    console.log("Gateway initiated");

    const response = await axios.post(
      `${FIND_TOP_5_URL}/find_top_5`,
      { email },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    res.json(response.data);
  } catch (error) {
    console.error(
      "Error forwarding request to GetPastWeek service:",
      error.message
    );
    res.status(500).json({ error: "Error processing GetPastWeek retrieval" });
  }
});

//End of Find Top 5

// Check Video Exists
const CHECK_EXISTS_URL =
  "https://personal-e5asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories";
app.post("/CheckExists", async (req, res) => {
  console.log("Received request at Check Exists:", req.body);
  const { VideoId, category, email } = req.body;
  try {
    // posts frontend request to the cat a service
    console.log("Gateway initiated");

    const response = await axios.post(
      `${CAT_RETRIEVAL_URL}/VideoExists`,
      {
        VideoId,
        category,
        email,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    res.json(response.data);
  } catch (error) {
    console.error(
      "Error forwarding request to Check Exists service:",
      error.message
    );
    res.status(500).json({ error: "Error processing check exists function" });
  }
});
//

//Start of Insert Video
const INSERT_URL =
  "https://personal-e5asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories";
app.post("/InsertProcessedVideo", async (req, res) => {
  console.log("Received request at Insert Processed Video:", req.body);
  const { VideoId, category, email } = req.body;
  try {
    // posts frontend request to the cat a service
    console.log("Gateway initiated");

    const response = await axios.post(
      `${CAT_RETRIEVAL_URL}/InsertPersonal`,
      {
        VideoId,
        category,
        email,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    res.json(response.data);
  } catch (error) {
    console.error(
      "Error forwarding request to Insert Processed service:",
      error.message
    );
    res.status(500).json({ error: "Error inserting video" });
  }
});
//End of Insert Video

// Console Log Received stuff from catb
//! Can send to Frontend 
app.post("/NotifyFrontend", (req, res) => {
  const { album_id } = req.body;

  console.log(`Received album_id: ${album_id}`);
  // Logic to fetch subcategories for the album_id from OutSystems or another service
  res.status(200).send(`Album ID ${album_id} processed successfully.`);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`API Gateway running on port ${PORT} in ${NODE_ENV} mode.`);
});
