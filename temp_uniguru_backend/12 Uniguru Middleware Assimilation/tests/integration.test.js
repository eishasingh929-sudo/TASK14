const request = require('supertest');
const app = require('../src/server');
const axios = require('axios');

// Mock axios module completely to prevent actual network calls
jest.mock('axios');

describe('UniGuru Admission Middleware', () => {

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('Validation Logic (Day 2)', () => {
        test('should reject empty body', async () => {
            const res = await request(app)
                .post('/admit')
                .send({});

            expect(res.statusCode).toBe(400);
            expect(res.body.allowed).toBe(false);
            expect(res.body.reason).toMatch(/Empty message/);
        });

        test('should reject malformed body (missing message)', async () => {
            const res = await request(app)
                .post('/admit')
                .send({ foo: 'bar' });

            expect(res.statusCode).toBe(400); // Expecting 400 Bad Request
            expect(res.body.allowed).toBe(false);
            // The rule engine specifically checks for 'message' property
            expect(res.body.reason).toMatch(/Malformed request/);
        });

        test('should reject unsafe tokens (SQL Injection)', async () => {
            const res = await request(app)
                .post('/admit')
                .send({ message: "DROP TABLE users" });

            expect(res.statusCode).toBe(400);
            expect(res.body.allowed).toBe(false);
            expect(res.body.reason).toMatch(/Unsafe tokens/);
        });

        test('should handle oversized payload (via express limit)', async () => {
            // Express body-parser limit is 1mb
            const largeString = 'a'.repeat(1024 * 1024 + 100);
            const res = await request(app)
                .post('/admit')
                .send({ message: largeString });

            // Express will return 413 Payload Too Large
            expect(res.statusCode).toBe(413);
            expect(res.body.allowed).toBe(false);
            expect(res.body.reason).toMatch(/Payload exceeds size limit/);
        });
    });

    describe('Forwarding Logic (Day 3)', () => {
        test('should forward valid request to target', async () => {
            // Mock successful upstream response
            // axios.post resolves to { data: ... }
            axios.post.mockResolvedValue({
                status: 200,
                data: { success: true, message: "Processed by UniGuru" }
            });

            const validPayload = { message: "Hello UniGuru" };

            const res = await request(app)
                .post('/admit')
                .send(validPayload);

            expect(res.statusCode).toBe(200);
            expect(res.body.success).toBe(true);

            // Verify axios call
            expect(axios.post).toHaveBeenCalledTimes(1);
            // The forwarding logic sends body directly
            expect(axios.post).toHaveBeenCalledWith(
                'http://localhost:5000/chat',
                validPayload
            );
        });

        test('should return 502 if upstream fails', async () => {
            // Mock failure
            axios.post.mockRejectedValue(new Error('Network Error'));

            const res = await request(app)
                .post('/admit')
                .send({ message: "Hello UniGuru" });

            expect(res.statusCode).toBe(502);
            expect(res.body.allowed).toBe(true);
            expect(res.body.forwarded).toBe(false); // Checking response structure from admission.js
            expect(res.body.error).toMatch(/Upstream service unavailable/);
        });
    });

});
