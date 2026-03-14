// Simple test script to verify backend connectivity
const http = require('http');

const testEndpoint = (path, method = 'GET', data = null) => {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: 8000,
      path: path,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:5173',
        'Access-Control-Request-Method': method,
        'Access-Control-Request-Headers': 'Content-Type'
      }
    };

    const req = http.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          data: responseData
        });
      });
    });

    req.on('error', (err) => {
      reject(err);
    });

    if (data) {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
};

const runTests = async () => {
  console.log('🧪 Testing UniGuru Backend Connectivity...\n');

  try {
    // Test 1: Health Check
    console.log('1. Testing Health Endpoint...');
    const healthResponse = await testEndpoint('/health');
    console.log(`   Status: ${healthResponse.status}`);
    console.log(`   CORS Headers: ${healthResponse.headers['access-control-allow-origin'] || 'Not set'}`);
    console.log(`   Response: ${healthResponse.data.substring(0, 100)}...\n`);

    // Test 2: CORS Preflight
    console.log('2. Testing CORS Preflight...');
    const corsResponse = await testEndpoint('/api/v1/auth/google', 'OPTIONS');
    console.log(`   Status: ${corsResponse.status}`);
    console.log(`   CORS Origin: ${corsResponse.headers['access-control-allow-origin'] || 'Not set'}`);
    console.log(`   CORS Methods: ${corsResponse.headers['access-control-allow-methods'] || 'Not set'}`);
    console.log(`   CORS Headers: ${corsResponse.headers['access-control-allow-headers'] || 'Not set'}\n`);

    // Test 3: Auth Endpoint (without token - should fail gracefully)
    console.log('3. Testing Auth Endpoint...');
    try {
      const authResponse = await testEndpoint('/api/v1/auth/google', 'POST', { token: 'test' });
      console.log(`   Status: ${authResponse.status}`);
      console.log(`   Response: ${authResponse.data.substring(0, 100)}...\n`);
    } catch (error) {
      console.log(`   Error: ${error.message}\n`);
    }

    // Test 4: Alternative Auth Endpoint
    console.log('4. Testing Alternative Auth Endpoint...');
    try {
      const altAuthResponse = await testEndpoint('/auth/google/token', 'POST', { token: 'test' });
      console.log(`   Status: ${altAuthResponse.status}`);
      console.log(`   Response: ${altAuthResponse.data.substring(0, 100)}...\n`);
    } catch (error) {
      console.log(`   Error: ${error.message}\n`);
    }

    console.log('✅ Backend connectivity tests completed!');
    console.log('\n📋 Summary:');
    console.log('- If health check returns 200, backend is running');
    console.log('- If CORS headers are present, CORS is configured');
    console.log('- If auth endpoints return 400/401, they are reachable');
    console.log('- If you see 429 errors, rate limiting is too strict');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Make sure backend server is running: cd server && npm start');
    console.log('2. Check if port 8000 is available');
    console.log('3. Verify environment variables are set correctly');
    console.log('4. Check firewall settings');
  }
};

runTests();
