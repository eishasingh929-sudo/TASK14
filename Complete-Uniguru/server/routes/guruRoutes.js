import express from 'express';
import {
  getUserGurus,
  createNewGuru,
  createCustomGuru,
  getGuru,
  updateGuru,
  deleteGuru,
  getChatWithGuru,
  getAvailableAIModels
} from '../controller/guruController.js';
import { protect } from '../middleware/auth.js';
import { validateGuruCreation } from '../middleware/validation.js';

const router = express.Router();

// All routes are protected
router.use(protect);

// Guru management routes
router.get('/g-g', getUserGurus); // Get user's gurus
router.post('/n-g/:userid', createNewGuru); // Create new basic guru
router.post('/custom-guru/:userid', validateGuruCreation, createCustomGuru); // Create custom guru
router.get('/g-c/:chatbotid/:userid', getChatWithGuru); // Get chat with guru
router.delete('/g-d/:id', deleteGuru); // Delete guru

// Individual guru routes
router.get('/models', getAvailableAIModels); // Get available AI models
router.get('/:id', getGuru); // Get guru by ID
router.put('/:id', updateGuru); // Update guru

export default router;
