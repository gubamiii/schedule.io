require('dotenv').config();
const { put } = require('@vercel/blob');

const BLOB_READ_WRITE_TOKEN = process.env.BLOB_READ_WRITE_TOKEN;
const BLOB_STORE_ID = process.env.BLOB_STORE_ID;

if (!BLOB_READ_WRITE_TOKEN || !BLOB_STORE_ID) {
  console.error('Missing environment variables. Please check .env file.');
  process.exit(1);
}

// Получаем данные из stdin
async function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.on('data', (chunk) => {
      data += chunk;
    });
    process.stdin.on('end', () => {
      resolve(data);
    });
  });
}

async function uploadSchedule() {
  try {
    console.log('Reading schedule data from stdin...');
    
    // Получаем данные из stdin
    const scheduleData = await readStdin();
    console.log(`Received ${scheduleData.length} characters of data`);
    
    // Проверяем, что данные правильные
    try {
      JSON.parse(scheduleData);
    } catch (error) {
      console.error('Invalid JSON received:', error.message);
      process.exit(1);
    }
    
    // Получаем правильный формат ID хранилища (без префикса store_ и в нижнем регистре)
    const storeId = BLOB_STORE_ID.replace('store_', '').toLowerCase();
    
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
    
    // Возвращаем результат в стандартный вывод
    console.log(JSON.stringify({
      success: true,
      url: blob.url
    }));
    
    process.exit(0);
  } catch (error) {
    console.error('Error during upload:', error.message);
    process.exit(1);
  }
}

uploadSchedule(); 