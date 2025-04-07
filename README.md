# ESD_Project

The following repository is done by Theron, Wei Lun, Owen, Zu Wei, Varrya, Joshua, and Jin Guang for Enterprise Solution Development. The project presents an auto video categoriser app which aims to process videos using OCR technology. Through this app, we aim to offer a seamless browsing experience for users through all their saved photos. By automated video categorisation and displaying them on the UI, users can now navigate freely and gracefully across an array of bookmarked videos. 

## Instructions 

To run the app, please type the following commaands. 

1. Clone the repository on your local machine
2. Ensure that you have Docker installed
3. Please refer to our submissions, and insert Frontend/`.env` into `Frontend/` environment. Do the same for `Backend`. At this point, both `Backend/` and `Frontend/` should have a separate `.env`. 
4. Once you are in `main` branch, ensure Docker is running and type `docker compose up --build` and wait for all microservices to load. Our microservices include:
   - cata
   - rabbitmq
   - catb
   - vidprocrabbmq
   - sharedalbum
   - frontend
   - gateway

5. Once all up and running, navigate to `localhost:8080` to access our frontend web page
6. Login with the credentials as listed in our deliverables and you can navigate freely through our website to auto-categorise different videos
