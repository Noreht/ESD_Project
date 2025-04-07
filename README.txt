README – Instagram Content Organiser (IS213 ESD Project)

This is the source code repository for our IS213 Enterprise Solution Development project titled "Instagram Content Organiser".

The project is designed to help users save and organise video content from Instagram. Key features include:
- User login via Firebase
- Video saving and categorisation
- Display of top 5 categories recently saved
- Shared album functionality with other users
- Notification system (via email, SMS, or frontend alert)

This project is implemented using Python microservices, RabbitMQ for asynchronous messaging, Firebase for authentication, and optionally OutSystems for interfacing with legacy systems. We also applied the Strangler Fig Pattern to migrate functionality progressively from OutSystems to our microservices.

Repository: https://github.com/Noreht/ESD_Project

Setup Instructions:
1. Clone this repository:
   git clone https://github.com/Noreht/ESD_Project.git

2. Install required Python packages:
   pip install flask requests

3. Create a `.env` file in the root directory with the following variables:
   INSTAGRAM_USERNAME=dummy_user
   INSTAGRAM_PASSWORD=dummy_2025

Testing:
- Unit testing was supported using ChatGPT.
- Code was implemented in Python and tested for functional correctness.

Note:
The OCR library for auto-tagging is not yet implemented.
Login enforcement before using the system is also pending.
Dummy Instagram credentials have been set up for testing purposes.

For questions or contributions, please contact the project team via GitHub Issues.

Last updated: March 2025
