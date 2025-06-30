import { initializeApp, getApps } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyDRXLLazKAQkGPYaxBIhZGzw0QE5DKbF8k",
  authDomain: "gcp-infrastructure-464305.firebaseapp.com",
  projectId: "gcp-infrastructure-464305",
  storageBucket: "gcp-infrastructure-464305.firebasestorage.app",
  messagingSenderId: "484958430300",
  appId: "1:484958430300:web:daaa86a57d3423b197f299",
  measurementId: "G-X84TZHL960"
};


// Initialize Firebase
let app;
if (!getApps().length) {
  app = initializeApp(firebaseConfig);
} else {
  app = getApps()[0];
}

export const auth = getAuth(app);
