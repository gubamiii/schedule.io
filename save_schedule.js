require('dotenv').config();
const fs = require('fs');
const { put } = require('@vercel/blob');

const BLOB_READ_WRITE_TOKEN = process.env.BLOB_READ_WRITE_TOKEN;
const BLOB_STORE_ID = process.env.BLOB_STORE_ID;

if (!BLOB_READ_WRITE_TOKEN || !BLOB_STORE_ID) {
  console.error('Missing environment variables. Please check .env file.');
  process.exit(1);
}

async function uploadSchedule() {
  try {
    // Read the temporary schedule file
    console.log('Reading temp_schedule.json');
    const scheduleData = fs.readFileSync('temp_schedule.json', 'utf8');
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
    
    process.exit(0);
  } catch (error) {
    console.error('Error during upload:', error);
    process.exit(1);
  }
}

uploadSchedule(); 