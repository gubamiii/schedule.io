require('dotenv').config();
const fs = require('fs');
const { put } = require('@vercel/blob');

const BLOB_READ_WRITE_TOKEN = process.env.BLOB_READ_WRITE_TOKEN;
const BLOB_STORE_ID = process.env.BLOB_STORE_ID;

if (!BLOB_READ_WRITE_TOKEN || !BLOB_STORE_ID) {
  console.error('Missing environment variables. Please check .env file.');
  process.exit(1);
}

console.log(`BLOB_STORE_ID: ${BLOB_STORE_ID}`);
console.log(`BLOB_READ_WRITE_TOKEN set: ${Boolean(BLOB_READ_WRITE_TOKEN)}`);

async function uploadSchedule() {
  try {
    // Read schedule data
    console.log('Reading schedule.json');
    const scheduleData = fs.readFileSync('schedule.json', 'utf8');
    console.log('Schedule data loaded successfully');
    
    // Upload file to Vercel Blob Storage
    console.log('Uploading to Vercel Blob Storage...');
    const blob = await put('schedule.json', Buffer.from(scheduleData), {
      access: 'public',
      token: BLOB_READ_WRITE_TOKEN,
      addRandomSuffix: false,
    });
    
    console.log('Schedule successfully uploaded to Vercel Blob Storage');
    console.log(`URL: ${blob.url}`);
    console.log(`Size: ${blob.size} bytes`);
    
    // Print the public URL
    const publicUrl = `https://${BLOB_STORE_ID}.public.blob.vercel-storage.com/schedule.json`;
    console.log(`Public URL: ${publicUrl}`);
    
  } catch (error) {
    console.error('Error during upload:', error);
    process.exit(1);
  }
}

uploadSchedule(); 