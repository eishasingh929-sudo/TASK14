import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

console.log('=== Environment Variables Test ===');
console.log('NODE_ENV:', process.env.NODE_ENV);
console.log('MONGODB_URI:', process.env.MONGODB_URI ? 'Set' : 'Not set');
console.log('GROQ_API_KEY:', process.env.GROQ_API_KEY ? `Set (${process.env.GROQ_API_KEY.substring(0, 10)}...)` : 'Not set');
console.log('JWT_SECRET:', process.env.JWT_SECRET ? 'Set' : 'Not set');
console.log('===================================');
