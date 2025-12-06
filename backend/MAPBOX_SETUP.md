# Mapbox Setup Guide

## 🚀 Quick Setup (5 minutes, NO credit card needed)

### Step 1: Sign Up for Mapbox
1. Go to: **https://account.mapbox.com/auth/signup/**
2. Sign up with your email (NO credit card required)
3. Verify your email

### Step 2: Get Your Access Token
1. After logging in, you'll see your **Default public token**
2. Copy it (it looks like: `pk.eyJ1Ijoi...`)

### Step 3: Add Token to Your App
1. Open `local.config` in your project
2. Find the line: `# GOOGLE_MAPS_API_KEY=...`
3. Replace it with:
   ```
   GOOGLE_MAPS_API_KEY=pk.eyJ1Ijoi...YOUR_ACTUAL_TOKEN_HERE
   ```
   (Use your actual token from Step 2)

### Step 4: Restart Your App
```bash
uv run python app.py
```

## ✅ Done!

Your app now uses Mapbox with:
- ✅ **100,000 free requests per month**
- ✅ **Real geocoding for ANY location worldwide**
- ✅ **No credit card required**
- ✅ **No billing setup needed**

## 🎯 Test It

Create a trip to ANY destination:

```graphql
mutation {
  createTrip(
    token: "YOUR_TOKEN"
    input: {
      destination: "Mumbai, India"
      startDate: "2025-12-20"
      endDate: "2025-12-22"
      budgetLevel: MODERATE
    }
  ) {
    message
    trip {
      id
      destination
      itineraries {
        dayNumber
        activities {
          place { name }
        }
      }
    }
  }
}
```

Works with ANY city in the world! 🌍
