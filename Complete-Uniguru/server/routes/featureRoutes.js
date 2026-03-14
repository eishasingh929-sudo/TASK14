import express from 'express';
import {
  readPdf,
  talkWithPdfContent,
  createPdf,
  scanImageText,
  editImageText,
  getAvailableTools
} from '../controller/featureController.js';
import { protect } from '../middleware/auth.js';
import { uploadPdf, uploadImage } from '../middleware/upload.js';

const router = express.Router();

// All routes are protected
router.use(protect);

// PDF features
router.post('/pdf/r', uploadPdf, readPdf); // Read PDF content
router.post('/pdf/t', talkWithPdfContent); // Talk with PDF content using AI
router.post('/pdf/c', createPdf); // Create PDF from content

// Image features
router.post('/image/s', uploadImage, scanImageText); // Scan text from image
router.post('/image/e', uploadImage, editImageText); // Edit text in image

// General features
router.get('/tools', getAvailableTools); // Get available tools

export default router;
