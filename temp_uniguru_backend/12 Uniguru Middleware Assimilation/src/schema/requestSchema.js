/**
 * Admission API request contract schema.
 * Deterministic contract definition (Day-1 requirement)
 */

const requestSchema = {
    type: "object",
    required: ["message"],
    properties: {
        message: {
            type: "string",
            minLength: 1,
            maxLength: 10000
        }
    },
    additionalProperties: true
};

module.exports = requestSchema;
