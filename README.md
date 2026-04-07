# Document Intelligence Web Demo (Google Gemini)

A sleek, premium web interface demonstrating document OCR and extraction. Built using Next.js and powered by the Google Gemini API. 
This is completely ready to be deployed directly to Vercel for potential clients to test document parsing.

## 🚀 How to Run Locally

The app should already be running on port 3001! If not:

1. Ensure your `.env.local` file contains your API key:
   ```txt
   GOOGLE_API_KEY=AIzaSyA_...
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3001](http://localhost:3001)

## ☁️ How to Deploy to Vercel

1. Push this directory to a GitHub repository.
2. Go to [Vercel.com](https://vercel.com) and click **Add New Project**.
3. Import your GitHub repository.
4. Under **Environment Variables**, add `GOOGLE_API_KEY` with your key from Google AI Studio.
5. Click **Deploy**.

That's it! Clients can now go directly to your `.vercel.app` URL, drop a PDF/Image, and instantly see the extracted Markdown. They do not need an API key.
