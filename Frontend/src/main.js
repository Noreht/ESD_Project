import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import { initializeApp } from "firebase/app";
import { getAuth } from 'firebase/auth'

createApp(App).mount('#app')

const firebaseConfig = {
    apiKey: "AIzaSyC8wNjLCuDy8cepNuc6yQI6t0idPTINvgU",
    authDomain: "esdproject-3fad1.firebaseapp.com",
    projectId: "esdproject-3fad1",
    storageBucket: "esdproject-3fad1.firebasestorage.app",
    messagingSenderId: "148218445152",
    appId: "1:148218445152:web:36f6c8ac9ff9da4da2b205",
    measurementId: "G-WTTT4E04P3"
  };
  
  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  
  //initialize firebase auth
  const auth = getAuth()

  export { app, auth }
