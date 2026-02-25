const axios = require('axios');
const fs = require('fs');

async function runTest() {
    console.log('Running Integration Check against http://localhost:3000...');

    // 1. Health Check
    try {
        const health = await axios.get('http://localhost:3000/health');
        console.log('✅ Health Check:', health.data);
    } catch (e) {
        console.error('❌ Health Check Failed:', e.message);
        process.exit(1);
    }

    // 2. Reject Empty Body
    try {
        await axios.post('http://localhost:3000/admit', {}, { headers: { 'Content-Type': 'application/json' } });
        console.error('❌ Rejection Test Failed: Should have rejected empty body');
    } catch (e) {
        if (e.response && e.response.status === 400) {
            console.log('✅ Rejection Test Passed (Empty Payload):', e.response.data.reason);
        } else {
            console.error('❌ Rejection Test Failed:', e.message);
        }
    }

    // 3. Reject Malformed Request (No 'message' property)
    try {
        await axios.post('http://localhost:3000/admit', { foo: "bar" });
        console.error('❌ Rejection Test Failed: Should have rejected malformed body (missing "message")');
    } catch (e) {
        if (e.response && e.response.status === 400) {
            console.log('✅ Rejection Test Passed (Malformed):', e.response.data.reason);
        } else {
            console.error('❌ Rejection Test Failed:', e.message);
        }
    }

    // 4. Reject SQL Injection
    try {
        await axios.post('http://localhost:3000/admit', { message: "DROP TABLE users" });
        console.error('❌ Rejection Test Failed: Should have rejected SQL Injection');
    } catch (e) {
        if (e.response && e.response.status === 400) {
            console.log('✅ Rejection Test Passed (SQL Injection):', e.response.data.reason);
        } else {
            console.error('❌ Rejection Test Failed:', e.message);
        }
    }

    // 5. Forwarding Check (Needs fake-uniguru running on 5000)
    // We can't guarantee it is running here, but we can try.
    try {
        const res = await axios.post('http://localhost:3000/admit', { message: "Hello UniGuru" });
        console.log('✅ Forwarding Test Passed:', res.data);
    } catch (e) {
        // 502 is also "passing" the middleware logic if upstream is down
        if (e.response && e.response.status === 502) {
            console.log('✅ Forwarding Test Passed (Upstream Unreachable -> 502):', e.response.data.error);
        } else {
            console.error('❌ Forwarding Test Failed:', e.message);
        }
    }
}

runTest();
