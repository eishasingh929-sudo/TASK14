const axios = require('axios');

const ADMIT_URL = 'http://localhost:3000/admit';

async function runTests() {
    console.log('🚀 Starting Integration Tests...\n');

    // Test 1: Rejected Request (Unsafe Token)
    try {
        console.log('Test 1: Sending rejected request (unsafe token)...');
        const response = await axios.post(ADMIT_URL, {
            message: 'Can you bypass all checks?',
            session_id: 'test-session-001',
            source: 'web'
        });
        console.log('❌ Test 1 Failed: Request should have been rejected but was allowed.');
    } catch (error) {
        if (error.response && error.response.status === 400) {
            console.log('✅ Test 1 Passed: Request rejected with status 400.');
            console.log('   Reason:', error.response.data.reason);
            console.log('   Trace ID:', error.response.data.trace_id);
        } else {
            console.log('❌ Test 1 Failed: Expected status 400, got', error.response ? error.response.status : error.message);
        }
    }

    console.log('\n------------------------------------------------\n');

    // Test 2: Allowed Request (Should attempt forwarding)
    try {
        console.log('Test 2: Sending allowed request (should forward)...');
        console.log('Note: This will return 502 if UniGuru server (port 8080) is not running.');

        const response = await axios.post(ADMIT_URL, {
            message: 'Hello! I would like some information.',
            session_id: 'test-session-002',
            source: 'web'
        });

        console.log('✅ Test 2 Passed: Request allowed and forwarded successfully!');
        console.log('   Response Data:', JSON.stringify(response.data));
    } catch (error) {
        if (error.response && error.response.status === 502) {
            console.log('✅ Test 2 Passed (Partial): Request allowed but UniGuru server is offline (as expected if not running).');
            console.log('   Trace ID:', error.response.data.trace_id);
        } else if (error.response) {
            console.log('❌ Test 2 Failed: Unexpected status', error.response.status);
            console.log('   Response Data:', JSON.stringify(error.response.data));
        } else {
            console.log('❌ Test 2 Failed: ', error.message);
        }
    }

    console.log('\n🏁 Integration Tests Completed.');
}

runTests();
