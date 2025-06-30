"use client";

import { useAuth } from "@/lib/AuthProvider";
import { useEffect, useState } from "react";

interface ProfileData {
  message: string;
  user_id: string;
}

export default function ProfilePage() {
  const { user, loading } = useAuth();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) return;

      try {
        const token = await user.getIdToken();
        console.log("Making request to /api/profile with token");
        const response = await fetch("/api/profile", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        console.log("Profile response status:", response.status);
        console.log("Profile response headers:", Object.fromEntries(response.headers.entries()));

        if (!response.ok) {
          const errorText = await response.text();
          console.error("Profile request failed:", errorText);
          throw new Error(`Failed to fetch profile: ${response.status} ${errorText}`);
        }

        const data: ProfileData = await response.json();
        console.log("Profile data received:", data);
        setProfile(data);
      } catch (err: unknown) {
        console.error("Profile fetch error:", err);
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("An unknown error occurred");
        }
      }
    };

    fetchProfile();
  }, [user]);

  const testBackend = async () => {
    try {
      console.log("Testing backend connectivity...");
      const response = await fetch("/api/test");
      console.log("Test response status:", response.status);
      
      if (!response.ok) {
        throw new Error(`Test failed: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("Test response data:", data);
      setTestResult(`Backend test successful: ${JSON.stringify(data)}`);
    } catch (err) {
      console.error("Backend test error:", err);
      setTestResult(`Backend test failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const testPipedrive = async () => {
    if (!user) {
      setError("You must be logged in to test Pipedrive");
      return;
    }

    try {
      const token = await user.getIdToken();
      console.log("Testing Pipedrive API connectivity...");
      
      // Use the full backend URL
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8080';
      const response = await fetch(`${backendUrl}/api/test-pipedrive`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Pipedrive test failed: ${response.status} ${errorText}`);
      }
      
      const data = await response.json();
      console.log("Pipedrive test response:", data);
      setTestResult(`Pipedrive API test successful! User: ${data.pipedrive_user?.name} (${data.pipedrive_user?.email})`);
    } catch (err) {
      console.error("Pipedrive test error:", err);
      setTestResult(`Pipedrive API test failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const connectService = async (service: 'outlook' | 'pipedrive') => {
    if (!user) {
      setError("You must be logged in to connect services");
      return;
    }

    try {
      const token = await user.getIdToken();
      console.log(`Initiating ${service} OAuth flow...`);
      
      // First, authenticate with the backend to get the OAuth URL
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8080';
      const initiateUrl = `${backendUrl}/api/auth/initiate/${service}`;
      
      console.log(`Making authenticated request to: ${initiateUrl}`);
      
      const response = await fetch(initiateUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to initiate ${service} OAuth: ${response.status} ${errorText}`);
      }

      const data = await response.json();
      console.log(`Received OAuth URL for ${service}:`, data.auth_url);
      
      // Redirect to the OAuth provider
      window.location.href = data.auth_url;
      
    } catch (err) {
      console.error(`${service} connection error:`, err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(`Failed to connect ${service}`);
      }
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <div>Please log in to view your profile.</div>;
  }

  return (
    <div>
      <h1>Profile</h1>
      
      <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#f0f0f0' }}>
        <h3>Backend Test</h3>
        <button 
          onClick={testBackend} 
          style={{ 
            marginRight: '10px', 
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Test Backend Connection
        </button>
        <button 
          onClick={testPipedrive} 
          style={{ 
            marginRight: '10px',
            padding: '8px 16px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Test Pipedrive API
        </button>
        {testResult && (
          <div style={{ marginTop: '10px', padding: '10px', backgroundColor: testResult.includes('successful') ? '#d4edda' : '#f8d7da' }}>
            {testResult}
          </div>
        )}
      </div>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {profile ? (
        <pre>{JSON.stringify(profile, null, 2)}</pre>
      ) : (
        <p>Loading profile...</p>
      )}

      <h2>Connect Services</h2>
      <div>
        <button 
          onClick={() => connectService('outlook')}
          style={{ marginRight: '10px', marginBottom: '10px' }}
        >
          Connect Outlook
        </button>
        <button 
          onClick={() => connectService('pipedrive')}
          style={{ marginBottom: '10px' }}
        >
          Connect Pipedrive
        </button>
      </div>
    </div>
  );
}
