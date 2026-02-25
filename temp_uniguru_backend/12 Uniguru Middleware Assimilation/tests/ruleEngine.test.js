const { validateRequest } = require('../src/ruleEngine');

describe("Rule Engine Unit Tests", () => {

    test("rejects empty message", () => {
        const result = validateRequest({}, 100);
        expect(result.allowed).toBe(false);
    });

    test("rejects malformed request", () => {
        // Requires { message: "..." }
        const result = validateRequest({ foo: "bar" }, 100);
        expect(result.allowed).toBe(false);
    });

    test("rejects oversized payload", () => {
        const result = validateRequest({ message: "hello" }, 2 * 1024 * 1024);
        expect(result.allowed).toBe(false);
    });

    test("rejects unsafe tokens", () => {
        const result = validateRequest({ message: "DROP TABLE users" }, 100);
        expect(result.allowed).toBe(false);
    });

    test("allows valid request", () => {
        const result = validateRequest({ message: "Hello UniGuru" }, 100);
        expect(result.allowed).toBe(true);
    });

});
